import pandas as pd
from app.models.patient import PatientInput, Gender
from app.models.responses import GenderRiskFlag, RiskCategory
from typing import List

class GenderRiskEngine:
    def __init__(self, gender_risk_df: pd.DataFrame):
        self.gender_risk_df = gender_risk_df
        self.gender_risk_df['drug_name'] = self.gender_risk_df['drug_name'].str.lower()
    
    def check_gender_risks(self, patient: PatientInput) -> List[GenderRiskFlag]:
        """Check for gender-specific medication risks"""
        flags = []
        
        if patient.gender != Gender.FEMALE:
            return flags  # Currently all risks are Female > Male
        
        for med in patient.medications:
            drug_lower = med.generic_name.lower()
            
            # Match drug in gender risk dataset
            matches = self.gender_risk_df[
                self.gender_risk_df['drug_name'].str.contains(drug_lower, na=False)
            ]
            
            for _, row in matches.iterrows():
                if 'Female > Male' in row['gender_risk']:
                    flags.append(GenderRiskFlag(
                        drug_name=med.generic_name,
                        risk_category=row['risk_category'],
                        risk_level=row['risk_level'],
                        mechanism=row['mechanism'],
                        monitoring_guidance=row['monitoring_guidance'],
                        escalation_applied=True
                    ))
        
        return flags
    
    def apply_gender_modifier(self, base_risk: RiskCategory, patient: PatientInput,
                             drug_name: str) -> tuple[RiskCategory, List[str]]:
        """
        Apply gender-based risk escalation
        Returns: (modified_risk, reasons)
        """
        reasons = []
        modified_risk = base_risk
        
        if patient.gender != Gender.FEMALE:
            return modified_risk, reasons
        
        drug_lower = drug_name.lower()
        matches = self.gender_risk_df[
            self.gender_risk_df['drug_name'].str.contains(drug_lower, na=False)
        ]
        
        for _, row in matches.iterrows():
            if row['risk_level'] == 'High':
                if base_risk == RiskCategory.YELLOW:
                    modified_risk = RiskCategory.RED
                    reasons.append(f"Escalated to RED: High gender-specific risk ({row['risk_category']}) - {row['mechanism']}")
                elif base_risk == RiskCategory.GREEN:
                    modified_risk = RiskCategory.YELLOW
                    reasons.append(f"Escalated to YELLOW: Gender-specific {row['risk_category']} risk")
        
        return modified_risk, reasons
