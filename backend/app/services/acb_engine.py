import pandas as pd
from app.models.patient import Medication
from app.models.responses import ACBResult

class ACBEngine:
    def __init__(self, acb_df: pd.DataFrame):
        self.acb_df = acb_df
        # Normalize for case-insensitive matching
        self.acb_df['Generic Name'] = self.acb_df['Generic Name'].str.lower()
    
    def calculate_acb_score(self, medications: list[Medication]) -> ACBResult:
        total_score = 0
        meds_with_acb = []
        
        for med in medications:
            generic_lower = med.generic_name.lower()
            match = self.acb_df[self.acb_df['Generic Name'] == generic_lower]
            
            if not match.empty:
                score = int(match.iloc[0]['ACB Score'])
                total_score += score
                meds_with_acb.append({
                    "name": med.generic_name,
                    "brand": match.iloc[0]['Brand Name'],
                    "acb_score": score
                })
        
        return ACBResult(
            total_acb_score=total_score,
            medications_with_acb=meds_with_acb
        )
