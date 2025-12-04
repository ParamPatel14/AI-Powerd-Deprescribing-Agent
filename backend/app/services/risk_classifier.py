from app.models.patient import PatientInput
from app.models.responses import RiskCategory, MedicationRiskAssessment
from app.services.frailty_risk_engine import FrailtyRiskEngine
from app.services.gender_risk_engine import GenderRiskEngine
from app.services.time_to_benefit_engine import TimeToBenefitEngine
from typing import List

class RiskClassifier:
    def __init__(self, frailty_engine: FrailtyRiskEngine, 
                 gender_engine: GenderRiskEngine,
                 ttb_engine: TimeToBenefitEngine):
        self.frailty_engine = frailty_engine
        self.gender_engine = gender_engine
        self.ttb_engine = ttb_engine
    
    def determine_base_risk(self, med_name: str, acb_score: int, 
                       has_beers: bool, has_stopp: bool) -> RiskCategory:
        """Determine initial risk category based on basic criteria"""
        
        # ✅ RED: Any single criterion is enough
        if acb_score >= 3:
            return RiskCategory.RED
        
        if has_beers:
            return RiskCategory.RED
        
        if has_stopp:
            return RiskCategory.RED
        
        # YELLOW: Moderate ACB
        if acb_score >= 1:
            return RiskCategory.YELLOW
        
        # GREEN: No major concerns
        return RiskCategory.GREEN
    
    def classify_medication(self, patient: PatientInput, med_name: str,
                           acb_score: int, has_beers: bool, has_stopp: bool,
                           drug_class: str = "") -> MedicationRiskAssessment:
        """
        Comprehensive medication risk classification
        Applies all risk modifiers in sequence
        """
        # Step 1: Base risk
        base_risk = self.determine_base_risk(med_name, acb_score, has_beers, has_stopp)
        risk_factors = []
        
        if acb_score > 0:
            risk_factors.append(f"ACB Score: {acb_score}")
        if has_beers:
            risk_factors.append("Beers Criteria matched")
        if has_stopp:
            risk_factors.append("STOPP criteria matched")
        
        # Step 2: Apply Time-to-Benefit modifier
        current_risk = base_risk
        ttb_risk, ttb_reasons = self.ttb_engine.apply_ttb_modifier(current_risk, patient, med_name)
        if ttb_reasons:
            risk_factors.extend(ttb_reasons)
            current_risk = ttb_risk
        
        # Step 3: Apply Gender modifier
        gender_risk, gender_reasons = self.gender_engine.apply_gender_modifier(current_risk, patient, med_name)
        if gender_reasons:
            risk_factors.extend(gender_reasons)
            current_risk = gender_risk
        
        # Step 4: Apply Frailty modifier (CFS)
        final_risk, frailty_reasons = self.frailty_engine.apply_frailty_modifier(
            current_risk, patient, drug_class, med_name
        )
        if frailty_reasons:
            risk_factors.extend(frailty_reasons)
        
        # Generate justification
        justification = f"Base: {base_risk.value}"
        if final_risk != base_risk:
            justification += f" → Final: {final_risk.value}"
        
        return MedicationRiskAssessment(
            medication_name=med_name,
            base_risk=base_risk,
            final_risk=final_risk,
            risk_factors=risk_factors,
            justification=justification
        )
