from typing import List, Dict, Optional
import pandas as pd
from app.models.api_models import TaperPlanRequest, TaperPlanResponse, TaperStep

class TaperPlanService:
    def __init__(self, tapering_df: pd.DataFrame, cfs_df: pd.DataFrame):
        self.tapering_df = tapering_df
        self.cfs_df = cfs_df
        self.tapering_df['drug_name'] = self.tapering_df['drug_name'].str.lower()
    
    def get_taper_plan(self, request: TaperPlanRequest) -> TaperPlanResponse:
        """Generate detailed taper plan for specific drug"""
        
        drug_lower = request.drug_name.lower()
        
        # Find drug in tapering dataset
        match = self.tapering_df[self.tapering_df['drug_name'] == drug_lower]
        
        if match.empty:
            # Generic taper for unknown drugs
            return self._generic_taper_plan(request)
        
        row = match.iloc[0]
        
        # Get frailty adjustment
        taper_multiplier = 1.0
        if request.patient_cfs_score:
            cfs_row = self.cfs_df[self.cfs_df['cfs_score'] == request.patient_cfs_score]
            if not cfs_row.empty:
                taper_multiplier = cfs_row.iloc[0]['taper_speed_multiplier']
        
        # Calculate duration
        base_duration = 8 if request.duration_on_medication == "long_term" else 4
        adjusted_duration = int(base_duration / taper_multiplier)
        
        # Generate steps
        steps = self._generate_taper_steps(
            row['step_logic'],
            row['withdrawal_symptoms'],
            adjusted_duration,
            request.current_dose,
            row['drug_class']
        )
        
        # Monitoring schedule
        monitoring_schedule = self._create_monitoring_schedule(
            row['monitoring_frequency'],
            adjusted_duration,
            row['withdrawal_symptoms']
        )
        
        # Patient education
        education = self._create_patient_education(
            request.drug_name,
            row['drug_class'],
            row['withdrawal_symptoms']
        )
        
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class=row['drug_class'],
            risk_profile=row['risk_profile'],
            taper_strategy=row['taper_strategy_name'],
            total_duration_weeks=adjusted_duration,
            steps=steps,
            pause_criteria=[
                row['pause_criteria'],
                "Severe withdrawal symptoms",
                "Patient request",
                "Clinical instability"
            ],
            reversal_criteria=[
                "Unmanageable withdrawal symptoms lasting >1 week",
                "Return of severe original symptoms",
                "Patient safety concerns",
                "Medical emergency"
            ],
            monitoring_schedule=monitoring_schedule,
            patient_education=education
        )
    
    def _generate_taper_steps(self, step_logic: str, withdrawal_symptoms: str, 
                             duration_weeks: int, current_dose: str, 
                             drug_class: str) -> List[TaperStep]:
        """Generate week-by-week taper steps"""
        steps = []
        
        # Parse current dose (simplified)
        try:
            dose_value = float(''.join(filter(str.isdigit, current_dose.split('mg')[0])))
        except:
            dose_value = 100  # Default
        
        # Determine reduction strategy
        if "10%" in step_logic:
            reduction_per_step = 10
        elif "25%" in step_logic:
            reduction_per_step = 25
        elif "50%" in step_logic:
            reduction_per_step = 50
        else:
            reduction_per_step = 20  # Default
        
        # Calculate steps
        num_steps = min(100 // reduction_per_step, duration_weeks // 2)
        weeks_per_step = max(2, duration_weeks // num_steps)
        
        current_percentage = 100
        current_week = 1
        
        for step_num in range(num_steps):
            current_percentage -= reduction_per_step
            calculated_dose = (dose_value * current_percentage) / 100
            
            if current_percentage <= 0:
                dose_str = "STOP"
                instructions = "Discontinue medication. Monitor for withdrawal symptoms."
            else:
                dose_str = f"{calculated_dose:.1f}mg" if 'mg' in current_dose else f"{current_percentage}% of original"
                instructions = f"Reduce to {current_percentage}% of starting dose. Take {dose_str}."
            
            monitoring = "Weekly check-in" if step_num < 2 else "Bi-weekly check-in"
            
            steps.append(TaperStep(
                week=current_week,
                dose=dose_str,
                percentage_of_original=max(0, current_percentage),
                instructions=instructions,
                monitoring=monitoring,
                withdrawal_symptoms_to_watch=withdrawal_symptoms.split(',')[:3]
            ))
            
            current_week += weeks_per_step
        
        # Final stop step
        if current_percentage > 0:
            steps.append(TaperStep(
                week=current_week,
                dose="STOP",
                percentage_of_original=0,
                instructions="Complete discontinuation. Continue monitoring for 4 weeks.",
                monitoring="Weekly for 4 weeks",
                withdrawal_symptoms_to_watch=withdrawal_symptoms.split(',')
            ))
        
        return steps
    
    def _create_monitoring_schedule(self, frequency: str, duration: int, 
                                   symptoms: str) -> Dict[str, List[str]]:
        """Create monitoring schedule"""
        return {
            "Week 1-2": [
                "Daily symptom diary",
                f"Watch for: {symptoms[:100]}",
                "Contact clinician if severe symptoms"
            ],
            "Week 3-4": [
                "Bi-weekly check-ins",
                "Vital signs if indicated",
                "Assess symptom severity"
            ],
            "Weeks 5+": [
                "Weekly to bi-weekly follow-up",
                "Adjust taper speed if needed",
                "Monitor for relapse of original condition"
            ],
            "Post-discontinuation": [
                "Monitor for 4 weeks after final dose",
                "Assess if discontinuation was successful",
                "Plan for long-term management"
            ]
        }
    
    def _create_patient_education(self, drug_name: str, drug_class: str, 
                                 symptoms: str) -> List[str]:
        """Create patient education points"""
        return [
            f"You are tapering off {drug_name} gradually to minimize withdrawal symptoms.",
            f"This medication is a {drug_class}, which should not be stopped abruptly.",
            f"Common withdrawal symptoms include: {symptoms[:150]}",
            "Follow the schedule exactly as prescribed. Do not speed up the taper.",
            "Keep a symptom diary and report any concerning symptoms to your doctor.",
            "If symptoms become severe, contact your healthcare provider immediately.",
            "Do not restart the medication without consulting your doctor.",
            "The taper schedule may be adjusted based on how you respond."
        ]
    
    def _generic_taper_plan(self, request: TaperPlanRequest) -> TaperPlanResponse:
        """Generic taper plan for drugs not in database"""
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class="Unknown",
            risk_profile="Standard",
            taper_strategy="Generic Gradual Reduction",
            total_duration_weeks=8,
            steps=[
                TaperStep(
                    week=1,
                    dose="75% of current dose",
                    percentage_of_original=75,
                    instructions="Reduce dose by 25%",
                    monitoring="Weekly assessment",
                    withdrawal_symptoms_to_watch=["General discomfort", "Return of symptoms"]
                ),
                TaperStep(
                    week=4,
                    dose="50% of current dose",
                    percentage_of_original=50,
                    instructions="Reduce dose by another 25%",
                    monitoring="Bi-weekly assessment",
                    withdrawal_symptoms_to_watch=["Monitor closely"]
                ),
                TaperStep(
                    week=6,
                    dose="25% of current dose",
                    percentage_of_original=25,
                    instructions="Reduce to 25% of original dose",
                    monitoring="Weekly assessment",
                    withdrawal_symptoms_to_watch=["Watch for withdrawal"]
                ),
                TaperStep(
                    week=8,
                    dose="STOP",
                    percentage_of_original=0,
                    instructions="Discontinue medication",
                    monitoring="Monitor for 4 weeks",
                    withdrawal_symptoms_to_watch=["Any new symptoms"]
                )
            ],
            pause_criteria=["Severe symptoms", "Patient distress"],
            reversal_criteria=["Unmanageable symptoms"],
            monitoring_schedule={"General": ["Weekly check-ins for 8 weeks"]},
            patient_education=["Gradual tapering is recommended", "Consult your doctor"]
        )
