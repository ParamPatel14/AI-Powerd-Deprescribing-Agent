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
        """Generate detailed taper plan (with proper logic)"""
        
        try:
            drug_lower = request.drug_name.lower()
            
            # ===== STEP 1: Check tapering_rules_dataset.csv (10 drugs) =====
            match = self.tapering_df[self.tapering_df['drug_name'] == drug_lower]
            
            if not match.empty:
                print(f"✅ Found {request.drug_name} in tapering database (one of the 10)")
                row = match.iloc[0]
                # Continue with existing logic...
                return self._generate_plan_from_row(row, request)
            
            # ===== STEP 2: Drug NOT in 10 - Check Beers/STOPP =====
            print(f"⚠️  Drug '{request.drug_name}' not in tapering database")
            print(f"🔍 Checking if it's in Beers or STOPP criteria...")
            
            # Check Beers Criteria
            beers_info = self._check_beers_for_drug(request.drug_name)
            
            # Check STOPP Criteria  
            stopp_info = self._check_stopp_for_drug(request.drug_name)
            
            # ===== STEP 3: Decide if tapering is needed =====
            if beers_info or stopp_info:
                print(f"✅ {request.drug_name} found in clinical criteria")
                
                if beers_info:
                    print(f"   Beers: {beers_info.get('rationale', 'N/A')}")
                if stopp_info:
                    print(f"   STOPP: {stopp_info.get('criterion', 'N/A')}")
                
                # Use Gemini to generate taper plan with context
                if self.use_gemini and self.gemini_service:
                    return self._generate_plan_with_gemini_context(
                        request, 
                        beers_info, 
                        stopp_info
                    )
                else:
                    # Fallback: Clinical criteria taper
                    return self._generate_clinical_criteria_taper(
                        request,
                        beers_info,
                        stopp_info
                    )
            else:
                print(f"⚠️  {request.drug_name} not in Beers/STOPP")
                print(f"   Likely safe to discontinue with monitoring")
                return self._generate_safe_discontinuation_plan(request)
        
        except Exception as e:
            print(f"❌ Error in get_taper_plan: {e}")
            import traceback
            traceback.print_exc()
            return self._emergency_fallback_plan(request)

# ===== NEW HELPER METHODS =====

    def _check_beers_for_drug(self, drug_name: str):
        """Check if drug is in Beers Criteria"""
        try:
            from app.utils.data_loader import load_beers_data
            beers_df = load_beers_data()
            
            # Search in drug_name column (case-insensitive)
            drug_lower = drug_name.lower()
            matches = beers_df[beers_df['drug_name'].str.lower().str.contains(drug_lower, na=False)]
            
            if not matches.empty:
                row = matches.iloc[0]
                return {
                    'table': row.get('table', 'Unknown'),
                    'therapeutic_category': row.get('therapeutic_category', 'Unknown'),
                    'rationale': row.get('rationale', 'Potentially inappropriate'),
                    'recommendation': row.get('recommendation', 'Avoid'),
                    'quality': row.get('quality', 'Unknown'),
                    'strength': row.get('strength', 'Unknown')
                }
            return None
        except Exception as e:
            print(f"   Error checking Beers: {e}")
            return None

    def _check_stopp_for_drug(self, drug_name: str):
        """Check if drug is in STOPP v2 Criteria"""
        try:
            from app.utils.data_loader import load_stopp_start_v2
            stopp_df, _ = load_stopp_start_v2()  # ✅ Load STOPP v2
            
            # Search in drug_class column (STOPP v2)
            drug_lower = drug_name.lower()
            matches = stopp_df[stopp_df['drug_class'].str.lower().str.contains(drug_lower, na=False)]
            
            if not matches.empty:
                row = matches.iloc[0]
                return {
                    'criterion_id': row.get('criterion_id', 'Unknown'),
                    'system': row.get('system', 'Unknown'),
                    'criterion': row.get('criterion', 'Potentially inappropriate'),
                    'action': row.get('action', 'Review'),
                    'condition': row.get('condition', 'N/A'),
                    'rationale': row.get('rationale', 'N/A'),  # ✅ Add rationale
                    'severity': row.get('severity', 'Unknown')  # ✅ Add severity
                }
            return None
        except Exception as e:
            print(f"   Error checking STOPP: {e}")
            import traceback
            traceback.print_exc()  # ✅ Show full error
            return None


    def _generate_plan_with_gemini_context(self, request, beers_info, stopp_info):
        """Use Gemini with clinical context from Beers/STOPP"""
        
        print(f"🤖 Using Gemini to generate taper plan with clinical context...")
        
        # Build context string
        context = f"Drug: {request.drug_name}\n"
        
        if beers_info:
            context += f"\nBeers Criteria:\n"
            context += f"- Category: {beers_info['therapeutic_category']}\n"
            context += f"- Rationale: {beers_info['rationale']}\n"
            context += f"- Recommendation: {beers_info['recommendation']}\n"
            context += f"- Quality of Evidence: {beers_info['quality']}\n"
        
        if stopp_info:
            context += f"\nSTOPP Criteria:\n"
            context += f"- System: {stopp_info['system']}\n"
            context += f"- Criterion: {stopp_info['criterion']}\n"
            context += f"- Action: {stopp_info['action']}\n"
        
        # Get drug info from Gemini with context
        try:
            drug_info = self.gemini_service.get_drug_information_with_context(
                drug_name=request.drug_name,
                clinical_context=context,
                patient_age=request.patient_age,
                comorbidities=request.comorbidities
            )
            
            # Check if tapering is needed
            if not drug_info.get('requires_taper', True):
                print(f"ℹ️  {request.drug_name} does not require tapering per Gemini analysis")
                return self._no_taper_needed_plan(request, drug_info)
            
            # Create synthetic row for taper generation
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
            
            print(f"✅ Gemini-generated profile: {row['drug_class']}, Risk: {row['risk_profile']}")
            
            # Continue with normal taper generation
            return self._generate_plan_from_row(row, request)
            
        except Exception as e:
            print(f"❌ Gemini generation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_clinical_criteria_taper(request, beers_info, stopp_info)

    def _generate_clinical_criteria_taper(self, request, beers_info, stopp_info):
        """Generate taper plan based on Beers/STOPP without Gemini"""
        
        # Determine drug class from Beers/STOPP
        if beers_info:
            drug_class = beers_info['therapeutic_category']
        elif stopp_info:
            drug_class = stopp_info['system']
        else:
            drug_class = "Unknown"
        
        # Simple classification
        high_risk_classes = [
            'Benzodiazepine', 'Anticholinergic', 'Antidepressant', 
            'Antipsychotic', 'Opioid', 'Sedative'
        ]
        
        requires_slow_taper = any(risk in drug_class for risk in high_risk_classes)
        
        if requires_slow_taper:
            duration = 8
            strategy = "Gradual reduction due to high-risk classification"
            symptoms = "Potential withdrawal symptoms - monitor closely"
        else:
            duration = 2
            strategy = "Gradual discontinuation with monitoring"
            symptoms = "Minimal withdrawal expected"
        
        steps = self._generate_basic_steps(
            step_logic=f"Reduce by 25% every {duration//4} weeks",
            symptoms=symptoms,
            duration=duration,
            current_dose=request.current_dose,
            drug_class=drug_class
        )
        
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class=drug_class,
            risk_profile="Based on Beers/STOPP",
            taper_strategy=strategy,
            total_duration_weeks=duration,
            steps=steps,
            pause_criteria=["Severe symptoms", "Patient distress"],
            reversal_criteria=["Unmanageable symptoms"],
            monitoring_schedule={
                "Weekly": ["Monitor for withdrawal symptoms", "Assess patient tolerance"]
            },
            patient_education=[
                f"{request.drug_name} was identified in clinical guidelines as potentially inappropriate",
                "Your healthcare provider has determined it's appropriate to reduce/stop this medication",
                "Follow the schedule and report any concerning symptoms immediately"
            ]
        )

    def _generate_safe_discontinuation_plan(self, request):
        """For drugs NOT in Beers/STOPP - likely safe to stop"""
    
        return TaperPlanResponse(
            drug_name=request.drug_name,
            drug_class="Not classified as high-risk",
            risk_profile="Standard",
            taper_strategy="Safe discontinuation",
            total_duration_weeks=1,
            steps=[
                TaperStep(
                    week=1,
                    dose="Current dose",
                    percentage_of_original=100,
                    instructions=f"{request.drug_name} is not classified as high-risk for withdrawal. May be discontinued with medical supervision.",
                    monitoring="Monitor for return of symptoms being treated",
                    withdrawal_symptoms_to_watch=["Return of original symptoms"]
                ),
                TaperStep(
                    week=2,
                    dose="STOP",
                    percentage_of_original=0,
                    instructions="Medication discontinued. Continue monitoring.",
                    monitoring="Follow up with healthcare provider in 2-4 weeks",
                    withdrawal_symptoms_to_watch=["Any new symptoms"]
                )
            ],
            pause_criteria=["Return of symptoms"],
            reversal_criteria=["Medical necessity"],
            monitoring_schedule={
                "Week 1-2": ["Monitor for return of original symptoms"],
                "Week 3-4": ["Follow-up assessment with healthcare provider"]
            },
            patient_education=[
                f"{request.drug_name} was not identified in high-risk medication lists",
                "It can likely be stopped safely with monitoring",
                "Always inform your healthcare provider before stopping any medication",
                "Report any concerning symptoms immediately"
            ]
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
    def _generate_plan_from_row(self, row, request: TaperPlanRequest) -> TaperPlanResponse:
        """Generate plan from database row (for the 10 drugs in CSV)"""
        
        # Get frailty adjustment
        taper_multiplier = 1.0
        if request.patient_cfs_score:
            cfs_row = self.cfs_df[self.cfs_df['cfs_score'] == request.patient_cfs_score]
            if not cfs_row.empty:
                taper_multiplier = cfs_row.iloc[0]['taper_speed_multiplier']
                print(f"   CFS {request.patient_cfs_score}: Taper multiplier = {taper_multiplier}")
        
        # Calculate duration
        base_duration = int(row.get('base_taper_duration_weeks', 8))
        if request.duration_on_medication == "long_term":
            base_duration = max(base_duration, 8)
        else:
            base_duration = max(base_duration // 2, 4)
            
        adjusted_duration = int(base_duration / taper_multiplier)
        print(f"   Duration: {base_duration} weeks → {adjusted_duration} weeks (frailty-adjusted)")
        
        # Generate steps - TRY Gemini first for detailed schedule
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
                
                # Validate and convert steps
                if gemini_schedule and 'taper_steps' in gemini_schedule:
                    validated_steps = []
                    for step_dict in gemini_schedule.get('taper_steps', []):
                        try:
                            # Ensure week is integer
                            if isinstance(step_dict.get('week'), str):
                                week_str = step_dict['week'].split('-')[0].strip()
                                step_dict['week'] = int(week_str)
                            
                            validated_steps.append(TaperStep(**step_dict))
                        except Exception as e:
                            print(f"⚠️  Skipping invalid step: {e}")
                            continue
                    
                    steps = validated_steps
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

