# backend/test_stopp_engine.py

import json
from pathlib import Path

from app.utils.data_loader import load_stopp_start_v2
from app.services.stopp_engine import STOPPEngine
from app.models.patient import (
    PatientInput,
    Medication,
    HerbalProduct,
    DurationCategory,
    Gender,
    LifeExpectancyCategory,
)

def main():
    print("=== STOPP/START v2 TEST ===\n")

    # 1) Load CSVs
    stopp_df, start_df = load_stopp_start_v2()
    print("STOPP columns:", list(stopp_df.columns))
    print("START columns:", list(start_df.columns))
    print("\nFirst 3 STOPP rows:")
    print(stopp_df.head(3))
    print("\nFirst 3 START rows:")
    print(start_df.head(3))

    # 2) Check NEW column names (updated for v2 CSVs)
    stopp_required = ["section", "system", "criterion_id", "criterion", "drug_class", 
                      "condition", "rationale", "action", "severity"]
    start_required = ["section", "system", "criterion_id", "criterion", "drug_class", 
                      "condition", "indication", "recommendation", "evidence"]
    
    stopp_missing = [c for c in stopp_required if c not in stopp_df.columns]
    start_missing = [c for c in start_required if c not in start_df.columns]
    
    if stopp_missing:
        print("\n❌ MISSING STOPP columns:", stopp_missing)
        return
    if start_missing:
        print("\n❌ MISSING START columns:", start_missing)
        return

    print("\n✅ All required columns present in both CSVs!")

    # 3) Build test patient with conditions + medications that should trigger rules
    patient = PatientInput(
        age=78,
        gender=Gender.FEMALE,
        is_frail=True,
        cfs_score=6,
        life_expectancy=LifeExpectancyCategory.TWO_TO_FIVE_YEARS,
        comorbidities=["hypertension", "heart failure", "diabetes", "atrial fibrillation"],
        medications=[
            Medication(
                generic_name="diazepam",
                brand_name="Valium",
                dose="5 mg",
                frequency="OD",
                indication="anxiety",
                duration=DurationCategory.LONG_TERM,
            ),
            Medication(
                generic_name="digoxin",
                brand_name=None,
                dose="125 mcg",
                frequency="OD",
                indication="heart failure",
                duration=DurationCategory.LONG_TERM,
            ),
        ],
        herbs=[],
    )

    # 4) Test STOPP engine
    engine = STOPPEngine(stopp_df, start_df)
    
    print("\n" + "="*60)
    print("TESTING STOPP CRITERIA")
    print("="*60)
    try:
        flags = engine.check_stopp_criteria(patient)
        print(f"✅ STOPP flags found: {len(flags)}")
        for f in flags:
            print(f"\n  Rule ID: {f.rule_id}")
            print(f"  Drug/Class: {f.drug_medication}")
            print(f"  Condition: {f.condition_disease}")
            print(f"  Rationale: {f.rationale}")
            print(f"  Full text: {f.full_text}")
    except Exception as e:
        print(f"\n❌ ERROR in check_stopp_criteria: {repr(e)}")
        import traceback
        traceback.print_exc()

    # 5) Test START criteria
    print("\n" + "="*60)
    print("TESTING START CRITERIA")
    print("="*60)
    try:
        start_recs = engine.check_start_criteria(patient)
        print(f"✅ START recommendations found: {len(start_recs)}")
        for i, rec in enumerate(start_recs, 1):
            print(f"\n  {i}. {rec}")
    except Exception as e:
        print(f"\n❌ ERROR in check_start_criteria: {repr(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
