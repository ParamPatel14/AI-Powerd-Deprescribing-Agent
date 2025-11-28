import pandas as pd
from app.models.patient import PatientInput, DurationCategory
from app.models.responses import TaperPlan

class TaperingEngine:
    def __init__(self, tapering_df: pd.DataFrame, cfs_map_df: pd.DataFrame):
        self.tapering_df = tapering_df
        self.cfs_map_df = cfs_map_df
    
    def generate_taper_plans(self, patient: PatientInput) -> list[TaperPlan]:
        plans = []
        
        # Get frailty adjustment
        cfs_score = patient.cfs_score if patient.cfs_score else (5 if patient.is_frail else 2)
        frailty_data = self.cfs_map_df[self.cfs_map_df['cfs_score'] == cfs_score].iloc[0]
        taper_multiplier = frailty_data['taper_speed_multiplier']
        
        for med in patient.medications:
            drug_lower = med.generic_name.lower()
            
            # Match drug in tapering rules
            match = self.tapering_df[
                self.tapering_df['drug_name'].str.lower() == drug_lower
            ]
            
            if not match.empty:
                row = match.iloc[0]
                
                # Adjust duration based on frailty
                base_duration_weeks = 4  # Default
                if med.duration == DurationCategory.LONG_TERM:
                    base_duration_weeks = 8
                
                adjusted_duration = int(base_duration_weeks / taper_multiplier)
                
                plans.append(TaperPlan(
                    drug_name=med.generic_name,
                    taper_strategy=row['taper_strategy_name'],
                    step_logic=row['step_logic'],
                    adjusted_duration_weeks=adjusted_duration,
                    monitoring_frequency=row['monitoring_frequency'],
                    withdrawal_symptoms=row['withdrawal_symptoms'],
                    pause_criteria=row['pause_criteria'],
                    frailty_adjustment=f"CFS {cfs_score}: {frailty_data['clinical_guidance']}"
                ))
        
        return plans
