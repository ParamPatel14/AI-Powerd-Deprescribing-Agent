import math
from app.models.patient import PatientInput, Gender


class ClinicalCalculators:
    @staticmethod
    def calculate_egfr_ckd_epi(patient: PatientInput) -> float | None:
        """
        Calculate eGFR using CKD-EPI 2021 equation (race-agnostic).
        Returns eGFR in mL/min/1.73m² or None if creatinine missing.
        """
        if patient.serum_creatinine_mg_dl is None:
            return None
        
        scr = patient.serum_creatinine_mg_dl
        age = patient.age
        
        # Gender-specific constants
        if patient.gender == Gender.FEMALE:
            kappa = 0.7
            alpha = -0.241
            multiplier = 1.012
        else:  # Male or Other
            kappa = 0.9
            alpha = -0.302
            multiplier = 1.0
        
        # CKD-EPI formula
        min_term = min(scr / kappa, 1.0) ** alpha
        max_term = max(scr / kappa, 1.0) ** -1.200
        age_term = 0.9938 ** age
        
        egfr = 142 * min_term * max_term * age_term * multiplier
        return round(egfr, 1)
    
    @staticmethod
    def calculate_meld_score(patient: PatientInput) -> float | None:
        """
        Calculate MELD score (3.0 version).
        Returns MELD score (6-40 range) or None if labs missing.
        """
        if not all([
            patient.serum_bilirubin_mg_dl,
            patient.inr,
            patient.serum_creatinine_mg_dl
        ]):
            return None
        
        # Clamp values to valid ranges
        bili = max(1.0, patient.serum_bilirubin_mg_dl)
        inr = max(1.0, patient.inr)
        cr = max(1.0, patient.serum_creatinine_mg_dl)
        
        # MELD formula
        meld = (
            3.78 * math.log(bili) +
            11.2 * math.log(inr) +
            9.57 * math.log(cr) +
            6.43
        )
        
        # Round and clamp to 6-40
        meld = round(meld)
        return max(6, min(40, meld))
    
    @staticmethod
    def calculate_meld_na(patient: PatientInput) -> float | None:
        """
        Calculate MELD-Na (includes sodium for better accuracy).
        """
        meld = ClinicalCalculators.calculate_meld_score(patient)
        if meld is None or patient.serum_sodium_mmol_l is None:
            return meld
        
        # Clamp sodium to 125-137 range
        na = max(125, min(137, patient.serum_sodium_mmol_l))
        
        meld_na = meld + 1.32 * (137 - na) - (0.033 * meld * (137 - na))
        return round(meld_na, 1)
