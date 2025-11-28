import pandas as pd
from app.models.patient import PatientInput
from app.models.responses import STOPPFlag

class STOPPEngine:
    def __init__(self, stopp_df: pd.DataFrame):
        self.stopp_df = stopp_df
    
    def check_stopp_criteria(self, patient: PatientInput) -> list[STOPPFlag]:
        flags = []
        
        for med in patient.medications:
            drug_lower = med.generic_name.lower()
            
            # Match drug or condition
            matches = self.stopp_df[
                (self.stopp_df['Drug_Medication'].str.lower().str.contains(drug_lower, na=False)) |
                (self.stopp_df['Condition_Disease'].str.lower().isin([c.lower() for c in patient.comorbidities]))
            ]
            
            for _, row in matches.iterrows():
                if row['Type'] == 'STOPP':
                    flags.append(STOPPFlag(
                        rule_id=str(row['Rule_ID']),
                        drug_medication=row['Drug_Medication'],
                        condition_disease=row['Condition_Disease'],
                        rationale=row['Rationale_Reason'],
                        full_text=row['Full_Text']
                    ))
        
        return flags
    
    def check_start_criteria(self, patient: PatientInput) -> list[str]:
        # Placeholder for START logic (missing meds)
        return []
