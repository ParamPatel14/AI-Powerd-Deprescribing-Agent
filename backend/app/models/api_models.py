from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict
from enum import Enum
from app.models.patient import PatientInput, Medication, HerbalProduct
from app.models.responses import RiskCategory, EvidenceStrength

# ========== Endpoint 1: /analyze-patient ==========
class AnalyzePatientRequest(BaseModel):
    """Request model for comprehensive patient analysis"""
    patient: PatientInput

class MedicationAnalysis(BaseModel):
    """Detailed analysis for a single medication"""
    name: str
    type: str  # "allopathic" or "herbal"
    risk_category: RiskCategory
    risk_score: int  # 1-10 scale
    flags: List[str]
    recommendations: List[str]
    taper_required: bool
    taper_duration_weeks: Optional[int] = None
    monitoring_required: List[str]
    stopp_flags: List[str] = []              # NEW
    start_recommendations: List[str] = []
    taper_plan: Optional[Dict[str, Any]] = None

class TaperingSchedule(BaseModel):
    """Week-by-week tapering schedule"""
    medication_name: str
    week: int
    dose: str
    instructions: str
    monitoring: str

class MonitoringPlan(BaseModel):
    """Overall monitoring plan"""
    medication_name: str
    frequency: str  # "Weekly", "Bi-weekly", "Monthly"
    parameters: List[str]  # ["Blood pressure", "Glucose", "INR"]
    duration_weeks: int
    alert_criteria: List[str]

class AnalyzePatientResponse(BaseModel):
    """Comprehensive response for patient analysis"""
    patient_summary: Dict[str, Any]
    medication_analyses: List[MedicationAnalysis]
    priority_summary: Dict[str, int]  # RED/YELLOW/GREEN counts
    tapering_schedules: List[TaperingSchedule]
    monitoring_plans: List[MonitoringPlan]
    herb_drug_interactions: List[Dict[str, str]]
    clinical_recommendations: List[str]
    safety_alerts: List[str]
    global_start_recommendations: List[str] = []

# ========== Endpoint 2: /get-taper-plan ==========
class TaperPlanRequest(BaseModel):
    """Request for specific taper plan"""
    drug_name: str
    current_dose: str
    duration_on_medication: str  # "short_term" or "long_term"
    patient_cfs_score: Optional[int] = Field(None, ge=1, le=9)
    patient_age: int
    comorbidities: List[str] = []

class TaperStep(BaseModel):
    """Single step in taper schedule"""
    week: int
    dose: str
    percentage_of_original: int
    instructions: str
    monitoring: str
    withdrawal_symptoms_to_watch: List[str]

class TaperPlanResponse(BaseModel):
    """Detailed taper plan response"""
    drug_name: str
    drug_class: str
    risk_profile: str
    taper_strategy: str
    total_duration_weeks: int
    steps: List[TaperStep]
    pause_criteria: List[str]
    reversal_criteria: List[str]
    monitoring_schedule: Dict[str, List[str]]
    patient_education: List[str]

# ========== Endpoint 3: /interaction-checker ==========
class InteractionCheckRequest(BaseModel):
    """Request for interaction checking"""
    herbs: List[str]  # List of herb names
    medications: List[str]  # List of drug names
    patient_comorbidities: List[str] = []

class InteractionDetail(BaseModel):
    """Single interaction detail"""
    herb_name: str
    drug_name: str
    interaction_type: str
    severity: str  # "Major", "Moderate", "Minor"
    mechanism: str
    clinical_effect: str
    evidence_strength: EvidenceStrength
    recommendation: str
    monitoring_required: List[str]

class InteractionCheckResponse(BaseModel):
    """Response for interaction checking"""
    total_interactions: int
    major_interactions: int
    moderate_interactions: int
    minor_interactions: int
    interactions: List[InteractionDetail]
    overall_risk_assessment: str
    recommendations: List[str]
