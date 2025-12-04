from typing import List, Dict
from app.models.patient import PatientInput
from app.models.api_models import (
    MedicationAnalysis, TaperingSchedule, MonitoringPlan, AnalyzePatientResponse
)
from app.models.responses import RiskCategory
from app.services.priority_classifier import PriorityClassifier
from app.services.tapering_engine import TaperingEngine
import pandas as pd

from app.services.clinical_calculators import ClinicalCalculators
from app.services.organ_function_checker import OrganFunctionChecker
from app.services.taper_plan_service import TaperPlanService
from app.services.polypharmacy_detector import PolypharmacyDetector

class AnalysisService:
    def __init__(self, all_engines: Dict):
        """Initialize with all engine instances"""
        self.engines = all_engines
        self.priority_classifier = PriorityClassifier()
        self.polypharmacy_detector = PolypharmacyDetector()

    def analyze_patient_comprehensive(self, patient: PatientInput) -> AnalyzePatientResponse:
        """Comprehensive patient analysis orchestration"""

        # ===== STEP 1: Calculate clinical scores =====
        egfr = ClinicalCalculators.calculate_egfr_ckd_epi(patient)
        meld = ClinicalCalculators.calculate_meld_score(patient)
        
        if egfr:
            print(f"📊 Calculated eGFR: {egfr} mL/min/1.73m²")
        if meld:
            print(f"📊 Calculated MELD: {meld}")

        # ===== STEP 2: Run all rule engines ===== 
        acb_result = self.engines['acb'].calculate_acb_score(patient.medications)
        beers_matches = self.engines['beers'].check_beers_criteria(patient)
        stopp_flags = self.engines['stopp'].check_stopp_criteria(patient, egfr)  # ✅ Pass eGFR
        start_recs = self.engines['stopp'].check_start_criteria(patient, egfr)   # ✅ Pass eGFR
        taper_plans = self.engines['tapering'].generate_taper_plans(patient)
        gender_flags = self.engines['gender'].check_gender_risks(patient)
        ttb_assessments = self.engines['ttb'].assess_time_to_benefit(patient)

        # ===== STEP 3: Herbal interactions =====
        known_interactions = self.engines['ayurvedic'].check_known_interactions(
            patient.herbs, patient.medications
        )
        simulated_interactions = self.engines['ayurvedic'].simulate_unknown_interactions(
            patient.herbs, patient.medications, patient
        )
        all_interactions = known_interactions + simulated_interactions

        # ===== STEP 4: Get organ function warnings ===== 
        organ_warnings = OrganFunctionChecker.get_organ_function_flags(
            patient, 
            egfr, 
            patient.ast_u_l, 
            patient.alt_u_l
        )
        print("\n🔍 Polypharmacy Detection:")
        polypharmacy_alerts = self.polypharmacy_detector.detect_polypharmacy(patient)
        
        if polypharmacy_alerts:
            for alert in polypharmacy_alerts:
                print(f"   {'🔴' if alert['severity'] == 'HIGH' else '🟡'} {alert['reason']}")
                print(f"      Medications: {', '.join(alert['medications'])}")
        else:
            print("   ✅ No polypharmacy issues detected")

        # ===== STEP 5: Build medication analyses (with organ warnings) =====
        medication_analyses = self._build_medication_analyses(
            patient, acb_result, beers_matches, stopp_flags,
            ttb_assessments, gender_flags, all_interactions,
            organ_warnings,
            polypharmacy_alerts
        )

        # ===== STEP 6: Build tapering schedules =====
        tapering_schedules = self._build_tapering_schedules(taper_plans, patient)

        # ===== STEP 7: Build monitoring plans =====
        monitoring_plans = self._build_monitoring_plans(
            medication_analyses, taper_plans, all_interactions
        )

        # ===== STEP 8: Generate clinical recommendations =====
        clinical_recommendations = self._generate_clinical_recommendations(
            medication_analyses, all_interactions, patient
        )

        # ===== STEP 9: Generate safety alerts =====
        safety_alerts = self._generate_safety_alerts(
            medication_analyses, all_interactions
        )

        # ===== STEP 10: Patient summary =====
        patient_summary = {
            "age": patient.age,
            "gender": patient.gender.value,
            "cfs_score": patient.cfs_score or "Not provided",
            "frailty_status": "Frail" if patient.is_frail else "Not frail",
            "life_expectancy": patient.life_expectancy.value,
            "total_medications": len(patient.medications),
            "total_herbs": len(patient.herbs),
            "comorbidities": patient.comorbidities,
            # ✅ Add calculated scores
            "calculated_egfr": egfr,
            "calculated_meld": meld,
            "renal_function": self._classify_renal_function(egfr),
            "hepatic_function": self._classify_hepatic_function(patient.ast_u_l, patient.alt_u_l),
        }

        # ===== STEP 11: Priority summary =====
        priority_summary = {
            "RED": sum(1 for m in medication_analyses if m.risk_category == RiskCategory.RED),
            "YELLOW": sum(1 for m in medication_analyses if m.risk_category == RiskCategory.YELLOW),
            "GREEN": sum(1 for m in medication_analyses if m.risk_category == RiskCategory.GREEN),
        }

        # ===== STEP 12: Herb-drug interactions summary =====
        herb_drug_interactions = [
            {
                "herb": i.herb_name,
                "drug": i.drug_name,
                "severity": i.severity,
                "effect": i.clinical_effect,
                "evidence": i.evidence_strength.value,
            }
            for i in all_interactions
        ]

        # ===== STEP 13: Return complete response =====
        return AnalyzePatientResponse(
            patient_summary=patient_summary,
            medication_analyses=medication_analyses,
            priority_summary=priority_summary,
            tapering_schedules=tapering_schedules,
            monitoring_plans=monitoring_plans,
            herb_drug_interactions=herb_drug_interactions,
            clinical_recommendations=clinical_recommendations,
            safety_alerts=safety_alerts,
            global_start_recommendations=start_recs,  # ✅ Include START recommendations
        )

    def _build_medication_analyses(
        self,
        patient,
        acb_result,
        beers_matches,
        stopp_flags,
        ttb_assessments,
        gender_flags,
        interactions,
        organ_warnings,
        polypharmacy_alerts
        
    ) -> List[MedicationAnalysis]:
        """Build detailed medication analysis with organ function warnings"""
        
        analyses = []

        # Build lookup tables
        acb_lookup = {item['name']: item['acb_score'] for item in acb_result.medications_with_acb}
        beers_dict = {m.drug_name: m for m in beers_matches}
        
        # ✅ FIX: Parse STOPP drug_class to match ALL drugs listed (comma-separated)
        stopp_dict = {}
        for flag in stopp_flags:
            if flag.drug_medication:
                # Split by comma to get all drugs in the class
                drugs_in_class = [d.strip().lower() for d in flag.drug_medication.split(',')]
                for drug in drugs_in_class:
                    # Store each drug separately, pointing to the same flag
                    stopp_dict[drug] = flag
        
        ttb_dict = {a.drug_name: a for a in ttb_assessments}
        gender_dict = {g.drug_name: g for g in gender_flags}

        # Analyze each medication
        for med in patient.medications:
            flags: List[str] = []
            recommendations: List[str] = []
            monitoring: List[str] = []

            # ------ ACB SCORE ------
            acb_score = acb_lookup.get(med.generic_name, 0)
            if acb_score >= 3:
                flags.append(f"High anticholinergic burden (ACB={acb_score})")
                recommendations.append("Consider deprescribing to reduce cognitive impairment risk")
                monitoring.append("Cognitive function")
            elif acb_score > 0:
                flags.append(f"Moderate anticholinergic burden (ACB={acb_score})")

            # ------ BEERS ------
            if med.generic_name in beers_dict:
                beers = beers_dict[med.generic_name]
                flags.append(f"Beers Criteria: {beers.category}")
                recommendations.append(beers.recommendation)

            # ------ STOPP (improved matching) ------
            med_lower = med.generic_name.lower()
            matched_stopp = None
            
            # Check if medication matches any STOPP drug
            for drug_key, stopp_flag in stopp_dict.items():
                if med_lower in drug_key or drug_key in med_lower:
                    matched_stopp = stopp_flag
                    break
            
            if matched_stopp:
                flags.append(f"STOPP Criteria: {matched_stopp.full_text}")
                recommendations.append(f"Rationale: {matched_stopp.rationale}")
                recommendations.append("Review indication and necessity")

            # ------ TIME TO BENEFIT ------
            if med.generic_name in ttb_dict:
                ttb = ttb_dict[med.generic_name]
                if "DEPRESCRIBE" in ttb.recommendation:
                    flags.append("Time-to-benefit exceeds life expectancy")
                    recommendations.append(ttb.recommendation)

            # ------ GENDER RISKS ------
            if med.generic_name in gender_dict:
                gender = gender_dict[med.generic_name]
                flags.append(f"Gender-specific risk: {gender.risk_category}")
                monitoring.append(gender.monitoring_guidance)

            # ------ HERB INTERACTIONS ------
            med_interactions = [
                i for i in interactions if i.drug_name.lower() == med.generic_name.lower()
            ]
            if med_interactions:
                for interaction in med_interactions:
                    flags.append(f"Herb-drug interaction: {interaction.herb_name} ({interaction.severity})")
                    monitoring.append(f"Monitor for {interaction.clinical_effect}")

            # ------ ✅ ORGAN FUNCTION WARNINGS ------
            med_organ_warn = next(
                (w for w in organ_warnings if w["medication"].lower() == med.generic_name.lower()),
                None
            )

            if med_organ_warn:
                # Renal warnings
                for rw in med_organ_warn.get("renal_warnings", []):
                    flags.append(f"⚠️ RENAL: {rw['action']} - {rw['reason']}")
                    recommendations.append(rw["action"])
                    monitoring.append("Renal function (eGFR, CrCl)")

                # Hepatic warnings
                for hw in med_organ_warn.get("hepatic_warnings", []):
                    flags.append(f"⚠️ HEPATIC: {hw['reason']}")
                    recommendations.append("Monitor LFTs")
                    monitoring.append("Liver function tests")

            poly_flags = self.polypharmacy_detector.get_flags_for_medication(
                med.generic_name, polypharmacy_alerts
            )
        
            if poly_flags:
                flags.extend(poly_flags)
            
            # Add recommendations from polypharmacy alerts
                for alert in polypharmacy_alerts:
                    if med.generic_name in alert['medications']:
                        recommendations.append(alert['recommendation'])

            # ------ RISK SCORING ------
            risk_category = self._determine_risk_category(acb_score, flags)
            risk_score = self._calculate_risk_score(acb_score, len(flags), risk_category)
            taper_required = risk_category in [RiskCategory.RED, RiskCategory.YELLOW]


            taper_plan_dict = None
            if taper_required and 'taper_service' in self.engines:
                try:
                    print(f"🔧 Generating taper plan for {med.generic_name} ({risk_category.value})")
                    
                    # Import here to avoid circular imports
                    from app.models.api_models import TaperPlanRequest
                    
                    # Create taper request
                    taper_request = TaperPlanRequest(
                        drug_name=med.generic_name,
                        current_dose=f"{med.dose} {med.frequency}" if med.dose and med.frequency else "Standard dose",
                        duration_on_medication="long_term",  # Default assumption
                        patient_age=patient.age,
                        patient_cfs_score=patient.cfs_score,
                        comorbidities=patient.comorbidities if patient.comorbidities else []
                    )
                    
                    # Get taper plan from service
                    taper_response = self.engines['taper_service'].get_taper_plan(taper_request)
                    
                    # Convert to dict for JSON serialization
                    taper_plan_dict = {
                        "drug_name": taper_response.drug_name,
                        "drug_class": taper_response.drug_class,
                        "risk_profile": taper_response.risk_profile,
                        "taper_strategy": taper_response.taper_strategy,
                        "total_duration_weeks": taper_response.total_duration_weeks,
                        "steps": [
                            {
                                "week": step.week,
                                "dose": step.dose,
                                "percentage_of_original": step.percentage_of_original,
                                "instructions": step.instructions,
                                "monitoring": step.monitoring,
                                "withdrawal_symptoms_to_watch": step.withdrawal_symptoms_to_watch
                            }
                            for step in taper_response.steps
                        ],
                        "pause_criteria": taper_response.pause_criteria,
                        "reversal_criteria": taper_response.reversal_criteria,
                        "monitoring_schedule": taper_response.monitoring_schedule,
                        "patient_education": taper_response.patient_education
                    }
                    
                    print(f"✅ Taper plan generated: {taper_response.total_duration_weeks} weeks, {len(taper_response.steps)} steps")
                    
                except Exception as e:
                    print(f"⚠️ Failed to generate taper plan for {med.generic_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    taper_plan_dict = None

            # Default recommendations if none added
            if not recommendations:
                recommendations.append(
                    "Continue medication with routine monitoring"
                    if risk_category == RiskCategory.GREEN
                    else "Clinical review recommended"
                )

            # Default monitoring if none added
            if not monitoring:
                monitoring.append("Routine clinical assessment")

            

            # Build MedicationAnalysis object
            analyses.append(
                MedicationAnalysis(
                    name=med.generic_name,
                    type="allopathic",
                    risk_category=risk_category,
                    risk_score=risk_score,
                    flags=flags if flags else ["No significant concerns"],
                    recommendations=recommendations,
                    taper_required=taper_required,
                    taper_duration_weeks=None,
                    monitoring_required=monitoring,
                    taper_plan=taper_plan_dict,
                )
            )

        # ------ ANALYZE HERBS ------
        for herb in patient.herbs:
            herb_interactions = [
                i for i in interactions if i.herb_name.lower() == herb.generic_name.lower()
            ]

            if herb_interactions:
                major = [i for i in herb_interactions if i.severity == "Major"]
                if major:
                    risk_category = RiskCategory.RED
                    flags = [f"Major interaction with {i.drug_name}" for i in major]
                else:
                    risk_category = RiskCategory.YELLOW
                    flags = [f"Moderate interaction with {i.drug_name}" for i in herb_interactions]
            else:
                risk_category = RiskCategory.GREEN
                flags = ["No interactions identified"]

            analyses.append(
                MedicationAnalysis(
                    name=herb.generic_name,
                    type="herbal",
                    risk_category=risk_category,
                    risk_score=self._calculate_risk_score(0, len(flags), risk_category),
                    flags=flags,
                    recommendations=["Monitor for interactions"]
                    if herb_interactions
                    else ["Continue as indicated"],
                    taper_required=False,
                    monitoring_required=["Watch for adverse effects"],
                )
            )

        return analyses


    
    def _build_tapering_schedules(self, taper_plans, patient) -> List[TaperingSchedule]:
        """Build week-by-week tapering schedules"""
        schedules = []
        
        for plan in taper_plans:
            # Parse step logic to create week-by-week schedule
            steps = self._parse_taper_steps(
                plan.step_logic, 
                plan.adjusted_duration_weeks,
                plan.monitoring_frequency
            )
            
            for week, step in enumerate(steps, start=1):
                schedules.append(TaperingSchedule(
                    medication_name=plan.drug_name,
                    week=week,
                    dose=step['dose'],
                    instructions=step['instructions'],
                    monitoring=step['monitoring']
                ))
        
        return schedules
    
    def _build_monitoring_plans(self, medication_analyses, taper_plans, interactions) -> List[MonitoringPlan]:
        """Build comprehensive monitoring plans"""
        plans = []
        
        for analysis in medication_analyses:
            if analysis.taper_required:
                # Find taper plan
                taper = next((t for t in taper_plans if t.drug_name == analysis.name), None)
                
                if taper:
                    plans.append(MonitoringPlan(
                        medication_name=analysis.name,
                        frequency=taper.monitoring_frequency,
                        parameters=analysis.monitoring_required,
                        duration_weeks=taper.adjusted_duration_weeks,
                        alert_criteria=[
                            taper.pause_criteria,
                            *analysis.flags
                        ]
                    ))
            elif analysis.risk_category in [RiskCategory.YELLOW, RiskCategory.RED]:
                plans.append(MonitoringPlan(
                    medication_name=analysis.name,
                    frequency="Monthly",
                    parameters=analysis.monitoring_required,
                    duration_weeks=12,
                    alert_criteria=analysis.flags
                ))
        
        return plans
    
    def _generate_clinical_recommendations(self, analyses, interactions, patient) -> List[str]:
        """Generate top-level clinical recommendations"""
        recommendations = []
        
        red_count = sum(1 for a in analyses if a.risk_category == RiskCategory.RED)
        yellow_count = sum(1 for a in analyses if a.risk_category == RiskCategory.YELLOW)
        
        if red_count > 0:
            recommendations.append(f"URGENT: {red_count} medication(s) flagged as HIGH PRIORITY for deprescribing review")
        
        if yellow_count > 0:
            recommendations.append(f"{yellow_count} medication(s) require clinical review and monitoring")
        
        if patient.cfs_score and patient.cfs_score >= 6:
            recommendations.append("Patient is severely frail (CFS ≥6): Use extreme caution with any medication changes")
        
        major_interactions = [i for i in interactions if i.severity == "Major"]
        if major_interactions:
            recommendations.append(f"ALERT: {len(major_interactions)} major herb-drug interaction(s) identified - immediate review required")
        
        if patient.age >= 80:
            recommendations.append("Patient is 80+ years old: Enhanced pharmacovigilance recommended")
        
        return recommendations
    
    def _generate_safety_alerts(self, analyses, interactions) -> List[str]:
        """Generate safety alerts"""
        alerts = []
        
        # High ACB medications
        high_acb = [a for a in analyses if "High anticholinergic" in ' '.join(a.flags)]
        if high_acb:
            alerts.append(f"⚠️ {len(high_acb)} medication(s) with high anticholinergic burden - FALL RISK")
        
        # Major interactions
        major_herb = [i for i in interactions if i.severity == "Major"]
        if major_herb:
            for interaction in major_herb:
                alerts.append(f"🚨 MAJOR INTERACTION: {interaction.herb_name} + {interaction.drug_name} - {interaction.clinical_effect}")
        
        # Multiple RED flags
        red_meds = [a for a in analyses if a.risk_category == RiskCategory.RED]
        if len(red_meds) >= 3:
            alerts.append(f"⚠️ POLYPHARMACY RISK: {len(red_meds)} high-risk medications - comprehensive medication review recommended")
        
        return alerts
    
    def _parse_taper_steps(self, step_logic: str, duration_weeks: int, monitoring: str) -> List[Dict]:
        """Parse step logic into weekly schedule"""
        # Simplified parser - you can expand this
        steps = []
        weeks_per_step = max(1, duration_weeks // 4)
        
        # Example: Create 4 steps
        for i in range(4):
            week = i * weeks_per_step + 1
            reduction = 25 * (i + 1)
            steps.append({
                'dose': f"{100 - reduction}% of original dose",
                'instructions': f"Reduce by {25}% from previous dose",
                'monitoring': monitoring if i % 2 == 0 else "Continue monitoring"
            })
        
        return steps
    
    def _determine_risk_category(self, acb_score: int, flags: List[str]) -> RiskCategory:
        """Determine risk category based on scores and flags"""
        
        # ✅ RED if ANY of these core criteria are met:
        # 1. High ACB score
        if acb_score >= 3:
            return RiskCategory.RED
        
        # 2. Beers Criteria matched
        if any("Beers Criteria" in flag for flag in flags):
            return RiskCategory.RED
        
        # 3. STOPP Criteria matched
        if any("STOPP Criteria" in flag or "STOPP" in flag for flag in flags):
            return RiskCategory.RED
        
        if any("THERAPEUTIC DUPLICATION" in flag for flag in flags):
            return RiskCategory.RED
        
        # 4. Other high-risk flags
        red_keywords = ["Major interaction", "Time-to-benefit exceeds", "⚠️ RENAL: STOP", "⚠️ RENAL: AVOID"]
        if any(any(keyword in flag for keyword in red_keywords) for flag in flags):
            return RiskCategory.RED
        

        if any("POLYPHARMACY" in flag for flag in flags):
            return RiskCategory.YELLOW
        
        # YELLOW: Moderate concerns
        if acb_score >= 1 or len(flags) >= 2:
            return RiskCategory.YELLOW
        
        # GREEN: No major concerns
        return RiskCategory.GREEN

    
    def _calculate_risk_score(self, acb_score: int, flag_count: int, category: RiskCategory) -> int:
        """Calculate numerical risk score (1-10)"""
        base_score = {
            RiskCategory.GREEN: 2,
            RiskCategory.YELLOW: 5,
            RiskCategory.RED: 8
        }[category]
        
        score = base_score + acb_score + flag_count
        return min(10, max(1, score))
    
    def _classify_renal_function(self, egfr: float | None) -> str:
        if egfr is None:
            return "Not calculated"
        if egfr >= 90:
            return "Normal (G1)"
        elif egfr >= 60:
            return "Mild reduction (G2)"
        elif egfr >= 45:
            return "Mild-moderate reduction (G3a)"
        elif egfr >= 30:
            return "Moderate-severe reduction (G3b)"
        elif egfr >= 15:
            return "Severe reduction (G4)"
        else:
            return "Kidney failure (G5)"

    def _classify_hepatic_function(self, ast: float | None, alt: float | None) -> str:
        if ast is None or alt is None:
            return "Not calculated"
        if ast <= 40 and alt <= 40:
            return "Normal"
        elif ast <= 80 and alt <= 80:
            return "Mildly elevated (monitor)"
        else:
            return "Significantly elevated (caution)"

