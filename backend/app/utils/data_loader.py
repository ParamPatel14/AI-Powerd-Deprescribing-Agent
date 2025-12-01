import pandas as pd
from pathlib import Path
import json
# Points to: project_root / datasets
DATA_DIR = Path(__file__).resolve().parents[3] / "datasets"


def _read_csv_safe(path: Path):
    """Read CSV safely with fallback encodings."""
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp1252")  # Windows encoding fallback


def load_acb_data():
    return _read_csv_safe(DATA_DIR / "acb_brand_list.csv")


def load_beers_data():
    return _read_csv_safe(DATA_DIR / "beers.csv")


def load_stopp_data():
    return _read_csv_safe(DATA_DIR / "stopp.csv")


def load_tapering_data():
    return _read_csv_safe(DATA_DIR / "tapering_rules_dataset.csv")


def load_cfs_map():
    return _read_csv_safe(DATA_DIR / "cfs_risk_taper_map.csv")

def load_gender_risk_data():
    return _read_csv_safe(DATA_DIR / "gender_risk_medications.csv")

def load_ttb_data():
    return _read_csv_safe(DATA_DIR / "time_to_benefit_dataset.csv")

def load_ayurvedic_known_interactions():
    return _read_csv_safe(DATA_DIR / "ayurvedic_known_interactions.csv")

def load_ayurvedic_pharmacological_profiles():
    file_path = DATA_DIR / "ayurvedic_pharmacological_profiles.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="utf-8-sig") as f:  # handles BOM issues
            return json.load(f)

def load_ayurvedic_herbs_summary():
    return _read_csv_safe(DATA_DIR / "ayurvedic_herbs_summary.csv")

import pandas as pd
from pathlib import Path

# Add to existing file
def load_stopp_start_v2():
    """Load STOPP/START v2 criteria from CSV files"""
    base_path = Path(__file__).resolve().parents[3] / "datasets"
    
    stopp_df = _read_csv_safe(base_path / "stopp_criteria_v2.csv")
    start_df = _read_csv_safe(base_path / "start_criteria_v2.csv")
    
    print(f"✅ Loaded {len(stopp_df)} STOPP criteria")
    print(f"✅ Loaded {len(start_df)} START criteria")
    
    return stopp_df, start_df

