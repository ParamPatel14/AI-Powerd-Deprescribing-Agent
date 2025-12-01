from typing import List, Tuple
from app.models.patient import PatientInput, Medication


class OrganFunctionChecker:
    """Check medication safety based on kidney and liver function."""
    
    # Medications contraindicated or dose-limited by eGFR
    RENAL_CONTRAINDICATIONS = {
        "metformin": {"egfr_limit": 30, "action": "STOP", "reason": "Risk of lactic acidosis"},
        "dabigatran": {"egfr_limit": 30, "action": "STOP", "reason": "Risk of bleeding"},
        "rivaroxaban": {"egfr_limit": 15, "action": "STOP", "reason": "Risk of bleeding"},
        "apixaban": {"egfr_limit": 15, "action": "STOP", "reason": "Risk of bleeding"},
        "nsaid": {"egfr_limit": 50, "action": "STOP", "reason": "Risk of AKI and worsening renal function"},
        "ibuprofen": {"egfr_limit": 50, "action": "STOP", "reason": "Risk of AKI"},
        "diclofenac": {"egfr_limit": 50, "action": "STOP", "reason": "Risk of AKI"},
        "naproxen": {"egfr_limit": 50, "action": "STOP", "reason": "Risk of AKI"},
        "colchicine": {"egfr_limit": 10, "action": "STOP", "reason": "Risk of colchicine toxicity"},
        "digoxin": {"egfr_limit": 30, "action": "REDUCE DOSE", "reason": "Risk of digoxin toxicity"},
        "gabapentin": {"egfr_limit": 60, "action": "REDUCE DOSE", "reason": "Renal excretion - dose adjustment needed"},
        "pregabalin": {"egfr_limit": 60, "action": "REDUCE DOSE", "reason": "Renal excretion - dose adjustment needed"},
    }
    
    # Medications hepatotoxic or contraindicated in liver disease
    HEPATIC_CONTRAINDICATIONS = {
        "methotrexate": {"ast_alt_ratio": 2.0, "reason": "Hepatotoxic - monitor LFTs"},
        "statins": {"ast_alt_ratio": 3.0, "reason": "Risk of hepatotoxicity"},
        "paracetamol": {"ast_alt_ratio": 2.0, "reason": "Hepatotoxic in liver disease"},
        "acetaminophen": {"ast_alt_ratio": 2.0, "reason": "Hepatotoxic in liver disease"},
        "amiodarone": {"ast_alt_ratio": 2.0, "reason": "Hepatotoxic"},
        "isoniazid": {"ast_alt_ratio": 2.0, "reason": "Hepatotoxic"},
        "valproate": {"ast_alt_ratio": 2.0, "reason": "Hepatotoxic"},
        "azathioprine": {"ast_alt_ratio": 2.0, "reason": "Monitor LFTs"},
    }

    @staticmethod
    def check_renal_safety(medication: Medication, egfr: float) -> Tuple[bool, str, str]:
        """
        Returns: (is_unsafe, action, reason)
        """
        med_lower = medication.generic_name.lower()
        
        for drug, limits in OrganFunctionChecker.RENAL_CONTRAINDICATIONS.items():
            if drug in med_lower:
                if egfr < limits["egfr_limit"]:
                    return (
                        True,
                        limits["action"],
                        f"{limits['reason']} (eGFR {egfr} < {limits['egfr_limit']})"
                    )
        
        return (False, "", "")

    @staticmethod
    def check_hepatic_safety(medication: Medication, ast: float, alt: float) -> Tuple[bool, str]:
        """
        Returns: (is_unsafe, reason)
        Simple check: if AST or ALT > 2x upper normal limit (UNL ~40 U/L)
        """
        med_lower = medication.generic_name.lower()
        upper_normal = 40  # U/L
        
        for drug, limits in OrganFunctionChecker.HEPATIC_CONTRAINDICATIONS.items():
            if drug in med_lower:
                if ast > (upper_normal * limits["ast_alt_ratio"]) or alt > (upper_normal * limits["ast_alt_ratio"]):
                    return (
                        True,
                        f"{limits['reason']} (AST={ast}, ALT={alt})"
                    )
        
        return (False, "")

    @staticmethod
    def get_organ_function_flags(patient: PatientInput, egfr: float | None, 
                                  ast: float | None, alt: float | None) -> List[dict]:
        """
        Returns list of organ function warnings for all medications.
        """
        warnings = []
        
        for med in patient.medications:
            med_warnings = {
                "medication": med.generic_name,
                "renal_warnings": [],
                "hepatic_warnings": []
            }
            
            # Renal check
            if egfr is not None:
                unsafe, action, reason = OrganFunctionChecker.check_renal_safety(med, egfr)
                if unsafe:
                    med_warnings["renal_warnings"].append({
                        "action": action,
                        "reason": reason
                    })
            
            # Hepatic check
            if ast is not None and alt is not None:
                unsafe, reason = OrganFunctionChecker.check_hepatic_safety(med, ast, alt)
                if unsafe:
                    med_warnings["hepatic_warnings"].append({
                        "reason": reason
                    })
            
            if med_warnings["renal_warnings"] or med_warnings["hepatic_warnings"]:
                warnings.append(med_warnings)
        
        return warnings
