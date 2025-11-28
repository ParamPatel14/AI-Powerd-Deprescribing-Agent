from typing import List, Dict, Tuple
from app.models.patient import PatientInput
from app.models.api_models import (
    MedicationAnalysis, TaperingSchedule, MonitoringPlan, AnalyzePatientResponse
)
from app.models.responses import RiskCategory
from app.services.priority_classifier import PriorityClassifier
from app.services.tapering_engine import TaperingEngine
import pandas as pd

class AnalysisService:
    def __init__(self, all_engines: Dict):
        """Initialize with all engine instances"""
        self.engines = all_engines
        self.priority_classifier = PriorityClassifier()
    
    def analyze_patient_comprehensive(self, patient: PatientInput) -> AnalyzePatientResponse:
        """Comprehensive patient analysis orchestration"""
        
        # Run all modules
        acb_result = self.engines['acb'].calculate_acb_score(patient.medications)
        beers_matches = self.engines['beers'].check_beers_criteria(patient)
        stopp_flags = self.engines['stopp'].check_stopp_criteria(patient)
        taper_plans = self.engines['tapering'].generate_taper_plans(patient)
        gender_flags = self.engines['gender'].check_gender_risks(patient)
        ttb_assessments = self.engines['ttb'].assess_time_to_benefit(patient)
        
        # Herbal interactions
        known_interactions = self.engines['ayurvedic'].check_known_interactions(
            patient.herbs, patient.medications
        )
        simulated_interactions = self.engines['ayurvedic'].simulate_unknown_interactions(
            patient.herbs, patient.medications, patient
        )
        all_interactions = known_interactions + simulated_interactions
        
        # Build medication analyses
        medication_analyses = self._build_medication_analyses(
            patient, acb_result, beers_matches, stopp_flags, 
            ttb_assessments, gender_flags, all_interactions
        )
        
        # Build tapering schedules
        tapering_schedules = self._build_tapering_schedules(taper_plans, patient)
        
        # Build monitoring plans
        monitoring_plans = self._build_monitoring_plans(
            medication_analyses, taper_plans, all_interactions
        )
        
        # Generate clinical recommendations
        clinical_recommendations = self._generate_clinical_recommendations(
            medication_analyses, all_interactions, patient
        )
        
        # Generate safety alerts
        safety_alerts = self._generate_safety_alerts(
            medication_analyses, all_interactions
        )
        
        # Patient summary
        patient_summary = {
            "age": patient.age,
            "gender": patient.gender.value,
            "cfs_score": patient.cfs_score or "Not provided",
            "frailty_status": "Frail" if patient.is_frail else "Not frail",
            "life_expectancy": patient.life_expectancy.value,
            "total_medications": len(patient.medications),
            "total_herbs": len(patient.herbs),
            "comorbidities": patient.comorbidities
        }
        
        # Priority summary
        priority_summary = {
            "RED": sum(1 for m in medication_analyses if m.risk_category == RiskCategory.RED),
            "YELLOW": sum(1 for m in medication_analyses if m.risk_category == RiskCategory.YELLOW),
            "GREEN": sum(1 for m in medication_analyses if m.risk_category == RiskCategory.GREEN)
        }
        
        # Herb-drug interactions summary
        herb_drug_interactions = [
            {
                "herb": i.herb_name,
                "drug": i.drug_name,
                "severity": i.severity,
                "effect": i.clinical_effect,
                "evidence": i.evidence_strength.value
            }
            for i in all_interactions
        ]
        
        return AnalyzePatientResponse(
            patient_summary=patient_summary,
            medication_analyses=medication_analyses,
            priority_summary=priority_summary,
            tapering_schedules=tapering_schedules,
            monitoring_plans=monitoring_plans,
            herb_drug_interactions=herb_drug_interactions,
            clinical_recommendations=clinical_recommendations,
            safety_alerts=safety_alerts
        )
    
    def _build_medication_analyses(self, patient, acb_result, beers_matches, 
                                   stopp_flags, ttb_assessments, gender_flags,
                                   interactions) -> List[MedicationAnalysis]:
        """Build detailed medication analysis"""
        analyses = []
        
        # Lookup tables
        acb_lookup = {item['name']: item['acb_score'] for item in acb_result.medications_with_acb}
        beers_dict = {m.drug_name: m for m in beers_matches}
        stopp_dict = {f.drug_medication.split()[0]: f for f in stopp_flags if f.drug_medication}
        ttb_dict = {a.drug_name: a for a in ttb_assessments}
        gender_dict = {g.drug_name: g for g in gender_flags}
        
        # Analyze each medication
        for med in patient.medications:
            flags = []
            recommendations = []
            monitoring = []
            
            acb_score = acb_lookup.get(med.generic_name, 0)
            if acb_score >= 3:
                flags.append(f"High anticholinergic burden (ACB={acb_score})")
                recommendations.append("Consider deprescribing to reduce cognitive impairment risk")
                monitoring.append("Cognitive function")
            elif acb_score > 0:
                flags.append(f"Moderate anticholinergic burden (ACB={acb_score})")
            
            if med.generic_name in beers_dict:
                beers = beers_dict[med.generic_name]
                flags.append(f"Beers Criteria: {beers.category}")
                recommendations.append(beers.recommendation)
            
            if any(med.generic_name.lower() in k.lower() for k in stopp_dict.keys()):
                flags.append("STOPP criteria matched")
                recommendations.append("Review indication and necessity")
            
            if med.generic_name in ttb_dict:
                ttb = ttb_dict[med.generic_name]
                if "DEPRESCRIBE" in ttb.recommendation:
                    flags.append("Time-to-benefit exceeds life expectancy")
                    recommendations.append(ttb.recommendation)
            
            if med.generic_name in gender_dict:
                gender = gender_dict[med.generic_name]
                flags.append(f"Gender-specific risk: {gender.risk_category}")
                monitoring.append(gender.monitoring_guidance)
            
            # Check herb interactions
            med_interactions = [i for i in interactions if i.drug_name.lower() == med.generic_name.lower()]
            if med_interactions:
                for interaction in med_interactions:
                    flags.append(f"Herb-drug interaction: {interaction.herb_name} ({interaction.severity})")
                    monitoring.append(f"Monitor for {interaction.clinical_effect}")
            
            # Determine risk category
            risk_category = self._determine_risk_category(acb_score, flags)
            risk_score = self._calculate_risk_score(acb_score, len(flags), risk_category)
            
            # Taper requirement
            taper_required = risk_category in [RiskCategory.RED, RiskCategory.YELLOW]
            
            if not recommendations:
                if risk_category == RiskCategory.GREEN:
                    recommendations.append("Continue medication with routine monitoring")
                else:
                    recommendations.append("Clinical review recommended")
            
            if not monitoring:
                monitoring.append("Routine clinical assessment")
            
            analyses.append(MedicationAnalysis(
                name=med.generic_name,
                type="allopathic",
                risk_category=risk_category,
                risk_score=risk_score,
                flags=flags if flags else ["No significant concerns"],
                recommendations=recommendations,
                taper_required=taper_required,
                taper_duration_weeks=None,  # Will be filled by tapering schedules
                monitoring_required=monitoring
            ))
        
        # Analyze herbs
        for herb in patient.herbs:
            herb_interactions = [i for i in interactions if i.herb_name.lower() == herb.generic_name.lower()]
            
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
            
            analyses.append(MedicationAnalysis(
                name=herb.generic_name,
                type="herbal",
                risk_category=risk_category,
                risk_score=self._calculate_risk_score(0, len(flags), risk_category),
                flags=flags,
                recommendations=["Monitor for interactions"] if herb_interactions else ["Continue as indicated"],
                taper_required=False,
                monitoring_required=["Watch for adverse effects"]
            ))
        
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
        if acb_score >= 3:
            return RiskCategory.RED
        
        red_keywords = ["High anticholinergic", "STOPP", "Major interaction", "Time-to-benefit"]
        if any(any(keyword in flag for keyword in red_keywords) for flag in flags):
            return RiskCategory.RED
        
        if acb_score >= 1 or len(flags) >= 2:
            return RiskCategory.YELLOW
        
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
