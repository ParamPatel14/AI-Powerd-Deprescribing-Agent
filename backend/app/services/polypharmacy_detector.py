from typing import List, Dict, Optional

from flask.cli import load_dotenv
from app.models.patient import PatientInput
import json
import os

class PolypharmacyDetector:
    """Detect therapeutic duplication and same-class polypharmacy"""
    
    def __init__(self):
        # Define drug classes with common medications
        self.drug_classes = {
            # Antidiabetics
            'sulfonylureas': ['glipizide', 'glyburide', 'glibenclamide', 'glimepiride', 'gliclazide'],
            'biguanides': ['metformin'],
            'dpp4_inhibitors': ['sitagliptin', 'linagliptin', 'saxagliptin', 'alogliptin', 'vildagliptin'],
            'sglt2_inhibitors': ['dapagliflozin', 'empagliflozin', 'canagliflozin', 'ertugliflozin'],
            'glp1_agonists': ['liraglutide', 'semaglutide', 'exenatide', 'dulaglutide'],
            'thiazolidinediones': ['pioglitazone', 'rosiglitazone'],
            'insulin': ['insulin', 'glargine', 'detemir', 'aspart', 'lispro', 'degludec'],
            
            # Antihypertensives
            'ace_inhibitors': ['lisinopril', 'enalapril', 'ramipril', 'captopril', 'perindopril', 'fosinopril'],
            'arbs': ['losartan', 'valsartan', 'irbesartan', 'candesartan', 'telmisartan', 'olmesartan'],
            'beta_blockers': ['metoprolol', 'atenolol', 'carvedilol', 'bisoprolol', 'propranolol', 'labetalol'],
            'calcium_channel_blockers': ['amlodipine', 'nifedipine', 'diltiazem', 'verapamil', 'felodipine'],
            'diuretics': ['furosemide', 'hydrochlorothiazide', 'chlorthalidone', 'spironolactone', 'eplerenone', 'amiloride', 'bumetanide'],
            
            # Anticoagulants
            'anticoagulants': ['warfarin', 'apixaban', 'rivaroxaban', 'edoxaban', 'dabigatran'],
            'antiplatelets': ['aspirin', 'clopidogrel', 'prasugrel', 'ticagrelor'],
            
            # Statins
            'statins': ['atorvastatin', 'simvastatin', 'rosuvastatin', 'pravastatin', 'lovastatin', 'fluvastatin'],
            
            # Antidepressants
            'ssris': ['fluoxetine', 'sertraline', 'paroxetine', 'citalopram', 'escitalopram'],
            'snris': ['venlafaxine', 'duloxetine', 'desvenlafaxine'],
            'tricyclics': ['amitriptyline', 'nortriptyline', 'doxepin', 'imipramine'],
            
            # Benzodiazepines
            'benzodiazepines': ['diazepam', 'lorazepam', 'alprazolam', 'clonazepam', 'temazepam'],
            
            # PPIs
            'ppis': ['omeprazole', 'esomeprazole', 'pantoprazole', 'lansoprazole', 'rabeprazole'],
            
            # NSAIDs
            'nsaids': ['ibuprofen', 'naproxen', 'diclofenac', 'celecoxib', 'indomethacin', 'ketorolac'],
        }
        
        # Group drug classes into therapeutic categories
        self.therapeutic_categories = {
            'antidiabetic': ['sulfonylureas', 'biguanides', 'dpp4_inhibitors', 'sglt2_inhibitors', 
                            'glp1_agonists', 'thiazolidinediones', 'insulin'],
            'antihypertensive': ['ace_inhibitors', 'arbs', 'beta_blockers', 'calcium_channel_blockers', 'diuretics'],
            'anticoagulation': ['anticoagulants', 'antiplatelets'],
            'lipid_lowering': ['statins'],
            'antidepressant': ['ssris', 'snris', 'tricyclics'],
            'sedative': ['benzodiazepines'],
            'gastric_protection': ['ppis'],
            'anti_inflammatory': ['nsaids'],
        }
        
        # Cache for AI-classified drugs
        self.classification_cache = {}
        
        # Initialize Gemini if API key provided
        self.use_gemini = False
        from dotenv import load_dotenv
        load_dotenv()
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.use_gemini = True
                print("✅ Gemini initialized for unknown drug classification")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.use_gemini = False
    
    def classify_medication(self, med_name: str) -> List[str]:
        """Return list of drug classes this medication belongs to (rule-based + AI fallback)"""
        med_lower = med_name.lower()
        classes = []
        
        # Step 1: Try rule-based classification
        for class_name, drugs in self.drug_classes.items():
            if any(drug in med_lower or med_lower in drug for drug in drugs):
                classes.append(class_name)
        
        # Step 2: If not found and Gemini available, use AI
        if not classes and self.use_gemini:
            # Check cache first
            if med_name in self.classification_cache:
                print(f"   💾 Using cached classification for {med_name}")
                return self.classification_cache[med_name]
            
            # Call Gemini
            print(f"   🤖 Unknown drug '{med_name}' - classifying with Gemini...")
            ai_classes = self._classify_with_gemini(med_name)
            if ai_classes:
                classes = ai_classes
                # Cache result
                self.classification_cache[med_name] = classes
                print(f"   ✅ Gemini classified as: {classes}")
        
        return classes
    
    def _classify_with_gemini(self, drug_name: str) -> Optional[List[str]]:
        """Use Gemini to classify unknown drugs"""
        
        prompt = f"""You are a pharmacology expert. Classify "{drug_name}" into therapeutic class(es).

Return ONLY a JSON array of class names from this list:
["sulfonylureas", "biguanides", "dpp4_inhibitors", "sglt2_inhibitors", "glp1_agonists", "thiazolidinediones", "insulin",
 "ace_inhibitors", "arbs", "beta_blockers", "calcium_channel_blockers", "diuretics",
 "anticoagulants", "antiplatelets", "statins", "ssris", "snris", "tricyclics", "benzodiazepines", "ppis", "nsaids"]

Example responses:
- "Enalapril" → ["ace_inhibitors"]
- "Empagliflozin" → ["sglt2_inhibitors"]
- "Unknown123" → []

Drug: "{drug_name}"
Response (JSON array only):"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean response (remove markdown code blocks if present)
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            
            classes = json.loads(text)
            return classes if isinstance(classes, list) else []
        except Exception as e:
            print(f"   ❌ Gemini classification error: {e}")
            return []
    
    def detect_polypharmacy(self, patient: PatientInput) -> List[Dict]:
        """Detect therapeutic duplication and same-class polypharmacy"""
        
        alerts = []
        
        # Map each medication to its drug classes
        med_to_classes = {}
        for med in patient.medications:
            classes = self.classify_medication(med.generic_name)
            if classes:
                med_to_classes[med.generic_name] = classes
        
        # Check for multiple drugs in same therapeutic category
        for category, class_list in self.therapeutic_categories.items():
            # Find all meds in this therapeutic category
            meds_in_category = []
            for med_name, drug_classes in med_to_classes.items():
                if any(dc in class_list for dc in drug_classes):
                    meds_in_category.append((med_name, drug_classes))
            
            # Alert if 2+ medications in same category
            if len(meds_in_category) >= 2:
                # Check if they're from SAME subclass (worse) or different subclasses
                subclasses_used = set()
                for _, drug_classes in meds_in_category:
                    subclasses_used.update(drug_classes)
                
                med_names = [m[0] for m in meds_in_category]
                
                # Same subclass = HIGH severity, different subclasses = MODERATE
                if len(subclasses_used) < len(meds_in_category):
                    # Duplication within same subclass (e.g., 2 ACE inhibitors)
                    alerts.append({
                        'severity': 'HIGH',
                        'category': category,
                        'medications': med_names,
                        'subclasses': list(subclasses_used),
                        'reason': f"Therapeutic duplication: {len(med_names)} {category} medications from same class ({', '.join(subclasses_used)})",
                        'recommendation': "Review indication - consider deprescribing one agent to reduce polypharmacy"
                    })
                else:
                    # Multiple agents but different subclasses (may be intentional combination therapy)
                    alerts.append({
                        'severity': 'MODERATE',
                        'category': category,
                        'medications': med_names,
                        'subclasses': list(subclasses_used),
                        'reason': f"Multiple {category} agents: {len(med_names)} medications from {len(subclasses_used)} different classes",
                        'recommendation': "Verify clinical rationale for combination therapy - ensure benefit outweighs polypharmacy risk"
                    })
        
        return alerts
    
    def get_flags_for_medication(self, med_name: str, all_alerts: List[Dict]) -> List[str]:
        """Get polypharmacy flags for a specific medication"""
        flags = []
        
        for alert in all_alerts:
            if med_name in alert['medications']:
                other_meds = [m for m in alert['medications'] if m != med_name]
                
                if alert['severity'] == 'HIGH':
                    flags.append(f"⚠️ THERAPEUTIC DUPLICATION: Same class as {', '.join(other_meds)}")
                else:
                    flags.append(f"ℹ️ POLYPHARMACY: Multiple {alert['category']} agents with {', '.join(other_meds)}")
        
        return flags
