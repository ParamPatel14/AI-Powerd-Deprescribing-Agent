import pandas as pd
from app.models.patient import PatientInput
from app.models.responses import BeersMatch

class BeersEngine:
    def __init__(self, beers_df: pd.DataFrame):
        self.beers_df = beers_df
        self.beers_df['drug_name'] = self.beers_df['drug_name'].str.lower()
    
    def check_beers_criteria(self, patient: PatientInput) -> list[BeersMatch]:
        matches = []
        
        for med in patient.medications:
            drug_lower = med.generic_name.lower()
            
            # Match drug in Beers list
            drug_matches = self.beers_df[
                self.beers_df['drug_name'].str.contains(drug_lower, na=False)
            ]
            
            for _, row in drug_matches.iterrows():
                # Age check (if Table 2 PIM, applies to age >= 65)
                if patient.age >= 65 or row['category_or_disease'] != 'N/A':
                    matches.append(BeersMatch(
                        drug_name=med.generic_name,
                        category=row['category_or_disease'],
                        rationale=row['rationale'],
                        recommendation=row['recommendation'],
                        strength=row['strength'],
                        quality=row['quality']
                    ))
        
        return matches
