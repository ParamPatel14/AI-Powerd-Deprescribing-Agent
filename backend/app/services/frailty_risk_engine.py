import pandas as pd
from app.models.patient import PatientInput
from app.models.responses import RiskCategory
from typing import List

class FrailtyRiskEngine:
    def __init__(self, cfs_map_df: pd.DataFrame):
        self.cfs_map_df = cfs_map_df
    
    def get_frailty_data(self, cfs_score: int) -> dict:
        """Get frailty parameters for a given CFS score"""
        row = self.cfs_map_df[self.cfs_map_df['cfs_score'] == cfs_score]
        if row.empty:
            return None
        return row.iloc[0].to_dict()
    
    def should_escalate_risk(self, patient: PatientInput, drug_class: str) -> tuple[bool, str]:
        """
        Determine if risk should be escalated based on CFS score
        Returns: (should_escalate, reason)
        """
        cfs_score = patient.cfs_score if patient.cfs_score else (5 if patient.is_frail else 2)
        
        # CFS >= 6 triggers escalation for high-risk drug classes
        if cfs_score >= 6:
            high_risk_classes = [
                'benzodiazepine', 'sedative', 'hypnotic', 'anticholinergic',
                'antipsychotic', 'z-drug', 'opioid', 'tricyclic'
            ]
            
            for risk_class in high_risk_classes:
                if risk_class in drug_class.lower():
                    frailty_data = self.get_frailty_data(cfs_score)
                    reason = f"CFS {cfs_score} ({frailty_data['clinical_label']}): {frailty_data['clinical_guidance']}"
                    return True, reason
        
        return False, ""
    
    def apply_frailty_modifier(self, base_risk: RiskCategory, patient: PatientInput, 
                              drug_class: str, drug_name: str) -> tuple[RiskCategory, List[str]]:
        """
        Apply frailty-based risk escalation
        Returns: (modified_risk, reasons)
        """
        reasons = []
        modified_risk = base_risk
        
        should_escalate, escalation_reason = self.should_escalate_risk(patient, drug_class)
        
        if should_escalate:
            if base_risk == RiskCategory.YELLOW:
                modified_risk = RiskCategory.RED
                reasons.append(f"Escalated YELLOW → RED due to severe frailty: {escalation_reason}")
            elif base_risk == RiskCategory.GREEN:
                modified_risk = RiskCategory.YELLOW
                reasons.append(f"Escalated GREEN → YELLOW due to frailty: {escalation_reason}")
        
        return modified_risk, reasons
