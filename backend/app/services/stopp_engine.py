import pandas as pd
from app.models.patient import PatientInput
from app.models.responses import STOPPFlag


class STOPPEngine:
    def __init__(self, stopp_df: pd.DataFrame, start_df: pd.DataFrame | None = None):
        self.stopp_df = stopp_df
        self.start_df = start_df

    def check_stopp_criteria(self, patient: PatientInput, egfr: float | None = None) -> list[STOPPFlag]:
        """
        Check STOPP v2 criteria with eGFR-aware matching.
        """
        flags = []
        patient_drugs = {m.generic_name.lower() for m in patient.medications}
        patient_conditions = {c.lower() for c in patient.comorbidities}

        for _, row in self.stopp_df.iterrows():
            drug_class = str(row["drug_class"]).lower()
            condition = str(row["condition"]).lower()
            
            drug_match = any(drug in drug_class or drug_class in drug for drug in patient_drugs)
            condition_match = any(cond in condition or condition in cond for cond in patient_conditions)
            
            # ✅ NEW: eGFR-based matching
            egfr_match = False
            if egfr is not None and drug_match:
                if "egfr <30" in condition and egfr < 30:
                    egfr_match = True
                elif "egfr <50" in condition and egfr < 50:
                    egfr_match = True
                elif "egfr <15" in condition and egfr < 15:
                    egfr_match = True

            if drug_match and (condition_match or egfr_match or "any" in condition.lower()):
                flags.append(STOPPFlag(
                    rule_id=str(row["criterion_id"]),
                    drug_medication=str(row["drug_class"]),
                    condition_disease=str(row["condition"]),
                    rationale=str(row["rationale"]),
                    full_text=f"{row['criterion']} - {row['action']}",
                ))

        return flags

    def check_start_criteria(self, patient: PatientInput, egfr: float | None = None) -> list[str]:
        """START recommendations with eGFR awareness."""
        if self.start_df is None:
            return []

        recs = []
        current_drugs = {m.generic_name.lower() for m in patient.medications}
        patient_conditions = {c.lower() for c in patient.comorbidities}

        for _, row in self.start_df.iterrows():
            condition = str(row["condition"]).lower()
            drug_class = str(row["drug_class"]).lower()
            criterion = str(row["criterion"])
            recommendation = str(row["recommendation"])

            condition_match = any(cond in condition or condition in cond for cond in patient_conditions)
            drug_missing = not any(drug in drug_class or drug_class in drug for drug in current_drugs)

            # ✅ Skip ACEIs/ARBs if eGFR <30 (contraindicated)
            if egfr is not None and egfr < 30:
                if any(d in drug_class for d in ["acei", "ace inhibitor", "arb"]):
                    continue  # Don't recommend

            if condition_match and drug_missing:
                recs.append(f"{criterion} → {recommendation}")

        return recs
