from typing import List, Dict
from app.models.patient import PatientInput
from app.models.responses import (
    RiskCategory, MedicationRiskAssessment, HerbalInteraction
)

class PriorityClassifier:
    def __init__(self):
        pass
    
    def classify_medication(self, 
                          med_name: str,
                          med_type: str,  # "allopathic" or "herbal"
                          acb_score: int,
                          has_beers: bool,
                          has_stopp: bool,
                          has_ttb_issue: bool,
                          has_gender_risk: bool,
                          has_frailty_escalation: bool,
                          herb_interactions: List[HerbalInteraction],
                          patient: PatientInput) -> MedicationRiskAssessment:
        """
        Comprehensive priority classification using all module outputs
        Returns final RED/YELLOW/GREEN classification
        """
        
        risk_factors = []
        contributing_modules = []
        
        # Step 1: Determine base risk
        base_risk = self._determine_base_risk(acb_score, has_beers, has_stopp)
        
        if acb_score > 0:
            risk_factors.append(f"ACB Score: {acb_score}")
            contributing_modules.append("ACB Engine")
        
        if has_beers:
            risk_factors.append("Beers Criteria matched")
            contributing_modules.append("Beers Engine")
        
        if has_stopp:
            risk_factors.append("STOPP criteria matched")
            contributing_modules.append("STOPP Engine")
        
        current_risk = base_risk
        
        # Step 2: Apply Time-to-Benefit escalation
        if has_ttb_issue:
            if current_risk != RiskCategory.RED:
                current_risk = RiskCategory.RED
                risk_factors.append("Time-to-benefit exceeds life expectancy")
                contributing_modules.append("Time-to-Benefit Engine")
        
        # Step 3: Apply Gender-specific risk escalation
        if has_gender_risk:
            if current_risk == RiskCategory.GREEN:
                current_risk = RiskCategory.YELLOW
                risk_factors.append("Gender-specific risk identified")
                contributing_modules.append("Gender Risk Engine")
            elif current_risk == RiskCategory.YELLOW:
                current_risk = RiskCategory.RED
                risk_factors.append("High gender-specific risk escalation")
                contributing_modules.append("Gender Risk Engine")
        
        # Step 4: Apply Frailty escalation
        if has_frailty_escalation:
            if current_risk == RiskCategory.YELLOW:
                current_risk = RiskCategory.RED
                risk_factors.append(f"Severe frailty (CFS {patient.cfs_score}) with high-risk medication")
                contributing_modules.append("Frailty Risk Engine")
            elif current_risk == RiskCategory.GREEN:
                current_risk = RiskCategory.YELLOW
                risk_factors.append(f"Frailty-adjusted risk (CFS {patient.cfs_score})")
                contributing_modules.append("Frailty Risk Engine")
        
        # Step 5: Apply Herbal Interaction escalation
        major_interactions = [i for i in herb_interactions if i.severity == "Major"]
        moderate_interactions = [i for i in herb_interactions if i.severity == "Moderate"]
        
        if major_interactions:
            current_risk = RiskCategory.RED
            for interaction in major_interactions:
                risk_factors.append(f"Major herb-drug interaction: {interaction.herb_name} ({interaction.evidence_strength.value})")
            contributing_modules.append("Ayurvedic Interaction Engine")
        elif moderate_interactions:
            if current_risk == RiskCategory.GREEN:
                current_risk = RiskCategory.YELLOW
                for interaction in moderate_interactions:
                    risk_factors.append(f"Moderate herb-drug interaction: {interaction.herb_name} ({interaction.evidence_strength.value})")
                contributing_modules.append("Ayurvedic Interaction Engine")
        
        # Final risk is now determined
        final_risk = current_risk
        
        # Generate justification
        justification = self._generate_justification(base_risk, final_risk, risk_factors)
        
        return MedicationRiskAssessment(
            medication_name=med_name,
            medication_type=med_type,
            base_risk=base_risk,
            final_risk=final_risk,
            risk_factors=risk_factors if risk_factors else ["No significant risk factors identified"],
            contributing_modules=list(set(contributing_modules)) if contributing_modules else ["None"],
            justification=justification
        )
    
    def _determine_base_risk(self, acb_score: int, has_beers: bool, has_stopp: bool) -> RiskCategory:
        """Determine initial risk category"""
        
        # ✅ RED: Any of these alone is RED
        if acb_score >= 3:
            return RiskCategory.RED
        
        if has_beers:
            return RiskCategory.RED
        
        if has_stopp:
            return RiskCategory.RED
        
        # YELLOW: Moderate concerns
        if acb_score >= 1:
            return RiskCategory.YELLOW
        
        # GREEN: No major concerns at baseline
        return RiskCategory.GREEN
    
    def _generate_justification(self, base_risk: RiskCategory, 
                               final_risk: RiskCategory, 
                               risk_factors: List[str]) -> str:
        """Generate human-readable justification"""
        if not risk_factors or risk_factors == ["No significant risk factors identified"]:
            return f"Final Classification: {final_risk.value} - Appropriate therapy with favorable risk-benefit ratio."
        
        if base_risk == final_risk:
            return f"Final Classification: {final_risk.value} - {'; '.join(risk_factors[:3])}"
        else:
            return f"Escalated from {base_risk.value} → {final_risk.value} due to: {'; '.join(risk_factors[:3])}"
