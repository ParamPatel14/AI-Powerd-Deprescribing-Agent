from pydantic import BaseModel
from typing import Any, List, Dict, Optional
from enum import Enum

class RiskCategory(str, Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"

class EvidenceStrength(str, Enum):
    KNOWN = "known"
    SIMULATED = "simulated"


class ACBResult(BaseModel):
    total_acb_score: int
    medications_with_acb: List[Dict[str, Any]]

class BeersMatch(BaseModel):
    drug_name: str
    category: str
    rationale: str
    recommendation: str
    strength: str
    quality: str

class STOPPFlag(BaseModel):
    rule_id: str
    drug_medication: str
    condition_disease: str
    rationale: str
    full_text: str

class TaperPlan(BaseModel):
    drug_name: str
    taper_strategy: str
    step_logic: str
    adjusted_duration_weeks: int
    monitoring_frequency: str
    withdrawal_symptoms: str
    pause_criteria: str
    frailty_adjustment: Optional[str] = None

class GenderRiskFlag(BaseModel):
    drug_name: str
    risk_category: str
    risk_level: str
    mechanism: str
    monitoring_guidance: str
    escalation_applied: bool

class TimeToBenefit(BaseModel):
    drug_name: str
    indication: str
    time_to_benefit: str
    ttb_months_min: int
    ttb_months_max: int
    patient_life_expectancy: str
    recommendation: str
    deprescribing_guidance: str
    reference: str

class HerbalInteraction(BaseModel):
    herb_name: str
    drug_name: str
    interaction_type: str
    mechanism: str
    severity: str
    clinical_effect: str
    evidence_strength: EvidenceStrength
    recommendation: str

class MedicationRiskAssessment(BaseModel):
    medication_name: str
    medication_type: str  # "allopathic" or "herbal"
    base_risk: RiskCategory
    final_risk: RiskCategory
    risk_factors: List[str]
    contributing_modules: List[str]
    justification: str

class RuleEngineOutput(BaseModel):
    acb_result: "ACBResult"
    beers_matches: List["BeersMatch"]
    stopp_flags: List["STOPPFlag"]
    start_flags: List[str]
    taper_plans: List["TaperPlan"]
    gender_risk_flags: List["GenderRiskFlag"]
    time_to_benefit_assessments: List["TimeToBenefit"]
    herbal_interactions: List[HerbalInteraction]
    medication_risk_classifications: List[MedicationRiskAssessment]
    summary: Dict[str, int]

class STOPPFlagDetailed(BaseModel):
    """Detailed STOPP flag for frontend display"""
    criterion_id: str
    criterion: str
    drug_class: str
    condition: str
    rationale: str
    action: str
    severity: str