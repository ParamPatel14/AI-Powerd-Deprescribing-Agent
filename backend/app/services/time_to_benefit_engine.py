import pandas as pd
from app.models.patient import PatientInput, LifeExpectancyCategory
from app.models.responses import TimeToBenefit, RiskCategory
from typing import List

class TimeToBenefitEngine:
    def __init__(self, ttb_df: pd.DataFrame):
        self.ttb_df = ttb_df
        self.ttb_df['drug_name'] = self.ttb_df['drug_name'].str.lower()
    
    def convert_life_expectancy_to_months(self, le_category: LifeExpectancyCategory) -> int:
        """Convert life expectancy category to months"""
        mapping = {
            LifeExpectancyCategory.LESS_THAN_1_YEAR: 6,
            LifeExpectancyCategory.ONE_TO_TWO_YEARS: 18,
            LifeExpectancyCategory.TWO_TO_FIVE_YEARS: 36,
            LifeExpectancyCategory.FIVE_TO_TEN_YEARS: 90,
            LifeExpectancyCategory.MORE_THAN_TEN_YEARS: 120
        }
        return mapping.get(le_category, 120)
    
    def assess_time_to_benefit(self, patient: PatientInput) -> List[TimeToBenefit]:
        """Assess if medications will provide benefit within patient's life expectancy"""
        assessments = []
        patient_le_months = self.convert_life_expectancy_to_months(patient.life_expectancy)
        
        for med in patient.medications:
            drug_lower = med.generic_name.lower()
            
            # Check if drug is in TTB dataset
            matches = self.ttb_df[
                self.ttb_df['drug_name'].str.contains(drug_lower, na=False) |
                self.ttb_df['drug_class'].str.lower().str.contains(drug_lower, na=False)
            ]
            
            for _, row in matches.iterrows():
                ttb_min = row['ttb_months_min']
                ttb_max = row['ttb_months_max']
                
                # Determine recommendation
                if ttb_min == 999:  # No benefit (e.g., Aspirin primary prevention)
                    recommendation = "DEPRESCRIBE - No proven benefit or harm > benefit"
                elif patient_le_months < ttb_min:
                    recommendation = f"DEPRESCRIBE - Life expectancy ({patient.life_expectancy.value}) < Time to benefit ({row['time_to_benefit']})"
                elif patient_le_months < ttb_max:
                    recommendation = "CONSIDER DEPRESCRIBING - Marginal benefit window"
                else:
                    recommendation = "CONTINUE - Adequate time for benefit"
                
                assessments.append(TimeToBenefit(
                    drug_name=med.generic_name,
                    indication=row['indication_context'],
                    time_to_benefit=row['time_to_benefit'],
                    ttb_months_min=ttb_min,
                    ttb_months_max=ttb_max,
                    patient_life_expectancy=patient.life_expectancy.value,
                    recommendation=recommendation,
                    deprescribing_guidance=row['deprescribing_guidance'],
                    reference=row['reference_trial']
                ))
        
        return assessments
    
    def apply_ttb_modifier(self, base_risk: RiskCategory, patient: PatientInput,
                          drug_name: str) -> tuple[RiskCategory, List[str]]:
        """
        Apply time-to-benefit risk escalation
        Returns: (modified_risk, reasons)
        """
        reasons = []
        modified_risk = base_risk
        patient_le_months = self.convert_life_expectancy_to_months(patient.life_expectancy)
        
        drug_lower = drug_name.lower()
        matches = self.ttb_df[
            self.ttb_df['drug_name'].str.contains(drug_lower, na=False) |
            self.ttb_df['drug_class'].str.lower().str.contains(drug_lower, na=False)
        ]
        
        for _, row in matches.iterrows():
            ttb_min = row['ttb_months_min']
            
            # No benefit drugs (TTB = 999)
            if ttb_min == 999:
                modified_risk = RiskCategory.RED
                reasons.append(f"Escalated to RED: No proven benefit for {row['indication_context']}")
            
            # Life expectancy less than minimum TTB
            elif patient_le_months < ttb_min:
                if base_risk != RiskCategory.RED:
                    modified_risk = RiskCategory.RED
                    reasons.append(f"Escalated to RED: Life expectancy insufficient for benefit (need {row['time_to_benefit']})")
        
        return modified_risk, reasons
