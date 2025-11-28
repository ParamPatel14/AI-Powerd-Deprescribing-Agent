from typing import List, Dict, Optional
import pandas as pd
from app.models.api_models import TaperPlanRequest, TaperPlanResponse, TaperStep

class TaperPlanService:
    def __init__(self, tapering_df: pd.DataFrame, cfs_df: pd.DataFrame, gemini_api_key: str = None):
        self.tapering_df = tapering_df
        self.cfs_df = cfs_df
        self.tapering_df['drug_name'] = self.tapering_df['drug_name'].str.lower()
        
        # Initialize Gemini service with error handling
        self.use_gemini = False
        self.gemini_service = None
        
        if gemini_api_key:
            try:
                from app.services.gemini_service import GeminiTaperService
                self.gemini_service = GeminiTaperService(api_key=gemini_api_key)
                self.use_gemini = True
                print("✅ Gemini API initialized for taper schedule generation")
            except ImportError as e:
                print(f"⚠️ Gemini service not available: {e}")
                print("   Install with: pip install google-generativeai")
                self.use_gemini = False
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.use_gemini = False
        else:
            print("ℹ️  No Gemini API key provided. Using basic taper schedules.")
    
    def get_taper_plan(self, request: TaperPlanRequest) -> TaperPlanResponse:
        """Generate detailed taper plan (with Gemini if available)"""
        
        try:
            drug_lower = request.drug_name.lower()
            
            # Find drug in tapering dataset
            match = self.tapering_df[self.tapering_df['drug_name'] == drug_lower]
            
            # ===== GEMINI ENHANCEMENT: Extract drug info if not in database =====
            if match.empty:
                print(f"⚠️  Drug '{request.drug_name}' not found in database.")
                
                # Check if Gemini is available
                if self.use_gemini and self.gemini_service:
                    print(f"🤖 Using Gemini to extract drug information for {request.drug_name}...")
                    
                    try:
                        # Get drug information from Gemini
                        drug_info = self.gemini_service.get_drug_information(request.drug_name)
                        
                        # Check if drug requires tapering
                        if not drug_info.get('requires_taper', True):
                            print(f"ℹ️ {request.drug_name} does not require tapering per Gemini analysis")
                            return self._no_taper_needed_plan(request, drug_info)
                        
                        # Create a synthetic row using Gemini data
                        print(f"✅ Creating drug profile from Gemini data")
                        row = pd.Series({
                            'drug_name': request.drug_name,
                            'drug_class': drug_info.get('drug_class', 'Unknown'),
                            'risk_profile': drug_info.get('risk_profile', 'Standard'),
                            'taper_strategy_name': drug_info.get('taper_strategy_name', 'Gradual Reduction'),
                            'step_logic': drug_info.get('step_logic', 'Reduce by 25% every 2 weeks'),
                            'withdrawal_symptoms': drug_info.get('withdrawal_symptoms', 'General discomfort'),
                            'monitoring_frequency': drug_info.get('monitoring_frequency', 'Weekly'),
                            'pause_criteria': drug_info.get('pause_criteria', 'Severe symptoms'),
                            'base_taper_duration_weeks': drug_info.get('typical_duration_weeks', 4)
                        })
                        
                        print(f"✅ Gemini-enhanced profile created for {request.drug_name}")
                        print(f"   Class: {row['drug_class']}, Risk: {row['risk_profile']}")
                        
                    except Exception as e:
                        print(f"❌ Gemini drug info extraction failed: {e}")
                        import traceback
                        traceback.print_exc()
                        print(f"🔄 Falling back to generic plan")
                        return self._generic_taper_plan(request)
                else:
                    print(f"⚠️  Gemini not available. Using generic plan.")
                    return self._generic_taper_plan(request)
            else:
                row = match.iloc[0]
                print(f"✅ Found {request.drug_name} in database")
            
            # Rest of the method continues as normal...
            # Get frailty adjustment
            taper_multiplier = 1.0
            if request.patient_cfs_score:
                cfs_row = self.cfs_df[self.cfs_df['cfs_score'] == request.patient_cfs_score]
                if not cfs_row.empty:
                    taper_multiplier = cfs_row.iloc[0]['taper_speed_multiplier']
            
            # Calculate duration
            base_duration = int(row.get('base_taper_duration_weeks', 8))
            if request.duration_on_medication == "long_term":
                base_duration = max(base_duration, 8)
            else:
                base_duration = max(base_duration // 2, 4)
                
            adjusted_duration = int(base_duration / taper_multiplier)
            
            # Generate steps
            steps = []
            patient_education = []
            pause_criteria = []
            reversal_criteria = []
            
            if self.use_gemini and self.gemini_service:
                try:
                    print(f"🤖 Generating detailed AI taper schedule...")
                    gemini_schedule = self.gemini_service.generate_detailed_taper_schedule(
                        drug_name=request.drug_name,
                        drug_class=row['drug_class'],
                        current_dose=request.current_dose,
                        duration_on_med=request.duration_on_medication,
                        taper_strategy=row['taper_strategy_name'],
                        step_logic=row['step_logic'],
                        total_weeks=adjusted_duration,
                        patient_age=request.patient_age,
                        cfs_score=request.patient_cfs_score or 3,
                        comorbidities=request.comorbidities,
                        withdrawal_symptoms=row['withdrawal_symptoms']
                    )
                    
                    steps = [TaperStep(**step) for step in gemini_schedule.get('taper_steps', [])]
                    patient_education = gemini_schedule.get('patient_education', [])
                    pause_criteria = gemini_schedule.get('pause_criteria', [])
                    reversal_criteria = gemini_schedule.get('success_indicators', [])
                    
                    print(f"✅ AI generated {len(steps)} taper steps")
                    
                except Exception as e:
                    print(f"⚠️  Gemini schedule generation failed: {e}")
                    print("🔄 Using basic taper generation")
            
            # Fallback to basic generation if needed
            if not steps:
                print(f"📋 Generating basic taper plan")
                steps = self._generate_basic_steps(
                    row['step_logic'],
                    row['withdrawal_symptoms'],
                    adjusted_duration,
                    request.current_dose,
                    row['drug_class']
                )
                patient_education = self._create_patient_education(
                    request.drug_name, row['drug_class'], row['withdrawal_symptoms']
                )
                pause_criteria = [str(row['pause_criteria']), "Severe withdrawal symptoms", "Patient request"]
                reversal_criteria = [
                    "Unmanageable symptoms lasting >1 week",
                    "Return of severe symptoms",
                    "Medical emergency"
                ]
            
            # Monitoring schedule
            monitoring_schedule = self._create_monitoring_schedule(
                row['monitoring_frequency'],
                adjusted_duration,
                row['withdrawal_symptoms']
            )
            
            return TaperPlanResponse(
                drug_name=request.drug_name,
                drug_class=row['drug_class'],
                risk_profile=row['risk_profile'],
                taper_strategy=row['taper_strategy_name'],
                total_duration_weeks=adjusted_duration,
                steps=steps,
                pause_criteria=pause_criteria,
                reversal_criteria=reversal_criteria,
                monitoring_schedule=monitoring_schedule,
                patient_education=patient_education
            )
        
        except Exception as e:
            print(f"❌ Error in get_taper_plan: {e}")
            import traceback
            traceback.print_exc()
            return self._emergency_fallback_plan(request)


    def _no_taper_needed_plan(self, request: TaperPlanRequest, drug_info: Dict) -> TaperPlanResponse:
        """Return a plan indicating no taper is needed"""
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class=drug_info.get('drug_class', 'Unknown'),
            risk_profile=drug_info.get('risk_profile', 'Low-risk'),
            taper_strategy="No Taper Required",
            total_duration_weeks=0,
            steps=[
                TaperStep(
                    week=1,
                    dose="Can be discontinued",
                    percentage_of_original=0,
                    instructions=f"{request.drug_name} can typically be stopped without tapering. However, consult your healthcare provider before making any changes.",
                    monitoring="Monitor for return of symptoms for which medication was prescribed",
                    withdrawal_symptoms_to_watch=drug_info.get('withdrawal_symptoms', 'Return of symptoms').split(',')[:3]
                )
            ],
            pause_criteria=["Return of severe symptoms"],
            reversal_criteria=["Symptoms worsen significantly"],
            monitoring_schedule={
                "First 2 weeks": [
                    "Monitor for return of original symptoms",
                    "General well-being assessment"
                ],
                "Ongoing": [
                    "Follow up with healthcare provider if concerns arise"
                ]
            },
            patient_education=[
                f"{request.drug_name} ({drug_info.get('drug_class')}) typically does not require gradual tapering.",
                "However, always inform your doctor before stopping any medication.",
                f"Watch for: {drug_info.get('withdrawal_symptoms', 'return of symptoms')}",
                drug_info.get('special_considerations', 'Monitor as directed by your healthcare provider.')
            ]
        )

    
    def _generate_basic_steps(self, step_logic: str, symptoms: str, duration: int, 
                             current_dose: str, drug_class: str) -> List[TaperStep]:
        """Generate basic taper steps without AI"""
        num_steps = max(4, duration // 2)
        reduction_per_step = 100 // num_steps
        
        steps = []
        for i in range(num_steps):
            current_percentage = 100 - (reduction_per_step * i)
            week = (i * (duration // num_steps)) + 1
            
            if current_percentage <= 0:
                dose_str = "STOP"
                instructions = "Discontinue medication. Monitor for withdrawal symptoms for 4 weeks."
            else:
                dose_str = f"{current_percentage}% of {current_dose}"
                instructions = f"Reduce to {current_percentage}% of starting dose ({current_dose})"
            
            steps.append(TaperStep(
                week=week,
                dose=dose_str,
                percentage_of_original=max(0, current_percentage),
                instructions=instructions,
                monitoring="Check-in with healthcare provider" if i % 2 == 0 else "Self-monitoring",
                withdrawal_symptoms_to_watch=symptoms.split(',')[:3] if symptoms else ["General discomfort"]
            ))
        
        # Add final STOP step if not already there
        if steps[-1].percentage_of_original > 0:
            steps.append(TaperStep(
                week=duration,
                dose="STOP",
                percentage_of_original=0,
                instructions="Complete discontinuation. Continue monitoring for 4 weeks.",
                monitoring="Weekly assessment for 4 weeks",
                withdrawal_symptoms_to_watch=symptoms.split(',') if symptoms else ["Return of symptoms"]
            ))
        
        return steps
    
    def _create_patient_education(self, drug_name: str, drug_class: str, 
                                  symptoms: str) -> List[str]:
        """Create patient education points"""
        return [
            f"You are gradually reducing {drug_name} to minimize withdrawal effects.",
            f"This medication is a {drug_class}, which should not be stopped suddenly.",
            f"Common withdrawal symptoms may include: {symptoms[:100] if symptoms else 'discomfort'}",
            "Follow the schedule exactly as prescribed. Do not skip doses or speed up the taper.",
            "Keep a daily symptom diary and report concerning symptoms to your doctor.",
            "Contact your healthcare provider immediately if symptoms become severe.",
            "The tapering schedule may be adjusted based on how you respond."
        ]
    
    def _create_monitoring_schedule(self, frequency: str, duration: int, 
                                   symptoms: str) -> Dict[str, List[str]]:
        """Create monitoring schedule"""
        return {
            "Week 1-2": [
                "Daily symptom diary",
                f"Watch for: {symptoms[:80] if symptoms else 'withdrawal symptoms'}",
                "Contact clinician if severe symptoms develop"
            ],
            "Week 3-4": [
                "Bi-weekly check-ins",
                "Monitor vital signs if indicated",
                "Assess symptom severity and functioning"
            ],
            "Ongoing": [
                frequency or "Weekly to bi-weekly follow-up",
                "Adjust taper speed if needed",
                "Monitor for relapse of original condition"
            ],
            "Post-discontinuation": [
                "Continue monitoring for 4 weeks after final dose",
                "Assess if discontinuation was successful",
                "Plan for long-term symptom management"
            ]
        }
    
    def _generic_taper_plan(self, request: TaperPlanRequest) -> TaperPlanResponse:
        """Generic plan for unknown drugs"""
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
                    withdrawal_symptoms_to_watch=["Monitor closely for symptoms"]
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
                    instructions="Discontinue medication. Monitor for 4 weeks.",
                    monitoring="Weekly monitoring",
                    withdrawal_symptoms_to_watch=["Any new symptoms"]
                )
            ],
            pause_criteria=["Severe symptoms", "Patient distress", "Safety concerns"],
            reversal_criteria=["Unmanageable symptoms", "Medical necessity"],
            monitoring_schedule={"General": ["Weekly check-ins for 8 weeks", "Daily symptom diary"]},
            patient_education=["Gradual tapering is recommended", "Consult your doctor before making changes"]
        )
    
    def _emergency_fallback_plan(self, request: TaperPlanRequest) -> TaperPlanResponse:
        """Last resort if everything fails"""
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class="Unknown",
            risk_profile="Requires clinical assessment",
            taper_strategy="Consult healthcare provider",
            total_duration_weeks=4,
            steps=[
                TaperStep(
                    week=1,
                    dose="Current dose",
                    percentage_of_original=100,
                    instructions="Maintain current dose. Schedule appointment with healthcare provider.",
                    monitoring="Daily self-monitoring",
                    withdrawal_symptoms_to_watch=["Any changes"]
                )
            ],
            pause_criteria=["Any concerning symptoms"],
            reversal_criteria=["Medical advice"],
            monitoring_schedule={"Immediate": ["Contact healthcare provider for personalized plan"]},
            patient_education=["This medication requires individualized tapering guidance from your healthcare provider"]
        )
    def _no_taper_needed_plan(self, request: TaperPlanRequest, drug_info: Dict) -> TaperPlanResponse:
        """Return a plan indicating no taper is needed"""
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class=drug_info.get('drug_class', 'Unknown'),
            risk_profile=drug_info.get('risk_profile', 'Low-risk'),
            taper_strategy="No Taper Required",
            total_duration_weeks=0,
            steps=[
                TaperStep(
                    week=1,
                    dose="Can be discontinued",
                    percentage_of_original=0,
                    instructions=f"{request.drug_name} can typically be stopped without tapering. However, consult your healthcare provider before making any changes.",
                    monitoring="Monitor for return of symptoms",
                    withdrawal_symptoms_to_watch=drug_info.get('withdrawal_symptoms', 'Return of symptoms').split(',')[:3]
                )
            ],
            pause_criteria=["Return of severe symptoms"],
            reversal_criteria=["Symptoms worsen significantly"],
            monitoring_schedule={
                "First 2 weeks": ["Monitor for return of original symptoms"],
                "Ongoing": ["Follow up with healthcare provider if concerns arise"]
            },
            patient_education=[
                f"{request.drug_name} typically does not require gradual tapering.",
                "Always inform your doctor before stopping any medication.",
                drug_info.get('special_considerations', 'Monitor as directed.')
            ]
        )

