from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DurationCategory(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    UNKNOWN = "unknown"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class LifeExpectancyCategory(str, Enum):
    LESS_THAN_1_YEAR = "<1_year"
    ONE_TO_TWO_YEARS = "1-2_years"
    TWO_TO_FIVE_YEARS = "2-5_years"
    FIVE_TO_TEN_YEARS = "5-10_years"
    MORE_THAN_TEN_YEARS = ">10_years"

class Medication(BaseModel):
    generic_name: str
    brand_name: Optional[str] = None
    dose: str
    frequency: str
    indication: Optional[str] = None
    duration: DurationCategory

class HerbalProduct(BaseModel):
    generic_name: str
    brand_name: Optional[str] = None
    dose: str
    frequency: str
    intended_effect: Optional[str] = None  # e.g., "sleep", "sugar control"
    duration: DurationCategory

class PatientInput(BaseModel):
    age: int
    gender: Gender
    is_frail: bool
    cfs_score: Optional[int] = Field(None, ge=1, le=9)
    life_expectancy: LifeExpectancyCategory
    comorbidities: List[str] = []
    medications: List[Medication]
    herbs: List[HerbalProduct] = []
    serum_creatinine_mg_dl: Optional[float] = None  # mg/dL
    serum_bilirubin_mg_dl: Optional[float] = None   # mg/dL
    inr: Optional[float] = None                      # INR for MELD
    ast_u_l: Optional[float] = None                  # AST (U/L)
    alt_u_l: Optional[float] = None                  # ALT (U/L)
    serum_sodium_mmol_l: Optional[float] = None
