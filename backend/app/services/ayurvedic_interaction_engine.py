import pandas as pd
import json
from typing import List, Dict, Tuple, Optional
from app.models.patient import PatientInput, HerbalProduct, Medication
from app.models.responses import HerbalInteraction, EvidenceStrength, RiskCategory

class AyurvedicInteractionEngine:
    def __init__(self, known_interactions_df: pd.DataFrame, 
                 pharmacological_profiles: Dict, 
                 herbs_summary_df: pd.DataFrame):
        self.known_interactions_df = known_interactions_df
        self.pharmacological_profiles = pharmacological_profiles
        self.herbs_summary_df = herbs_summary_df
        
        # Normalize for case-insensitive matching
        self.known_interactions_df['herb_name'] = self.known_interactions_df['herb_name'].str.lower()
        self.known_interactions_df['specific_drugs'] = self.known_interactions_df['specific_drugs'].str.lower()
        self.herbs_summary_df['Herb Name'] = self.herbs_summary_df['Herb Name'].str.lower()
        
        # Build herb profile lookup
        self.herb_profiles = {}
        for herb in self.pharmacological_profiles.get('herbs', []):
            self.herb_profiles[herb['herb_name'].lower()] = herb
    
    def check_known_interactions(self, herbs: List[HerbalProduct], 
                                 medications: List[Medication]) -> List[HerbalInteraction]:
        """Check evidence-based herb-drug interactions"""
        interactions = []
        
        for herb in herbs:
            herb_lower = herb.generic_name.lower()
            
            for med in medications:
                drug_lower = med.generic_name.lower()
                
                # Direct drug name match
                matches = self.known_interactions_df[
                    (self.known_interactions_df['herb_name'] == herb_lower) &
                    (self.known_interactions_df['specific_drugs'].str.contains(drug_lower, na=False, case=False))
                ]
                
                if not matches.empty:
                    for _, row in matches.iterrows():
                        interactions.append(HerbalInteraction(
                            herb_name=herb.generic_name,
                            drug_name=med.generic_name,
                            interaction_type=row['interaction_type'],
                            mechanism=row['mechanism'],
                            severity=row['severity'],
                            clinical_effect=row['clinical_effect'],
                            evidence_strength=EvidenceStrength.KNOWN,
                            recommendation=self._generate_recommendation(row['severity'], row['clinical_effect'])
                        ))
        
        return interactions
    
    def simulate_unknown_interactions(self, herbs: List[HerbalProduct], 
                                     medications: List[Medication],
                                     patient: PatientInput) -> List[HerbalInteraction]:
        """Simulate interactions for herbs without documented evidence"""
        simulated_interactions = []
        
        for herb in herbs:
            herb_lower = herb.generic_name.lower()
            herb_profile = self.herb_profiles.get(herb_lower)
            
            if not herb_profile:
                # Infer from intended effect if no profile exists
                herb_profile = self._infer_herb_profile(herb)
            
            for med in medications:
                # Check if already covered by known interactions
                if self._has_known_interaction(herb.generic_name, med.generic_name):
                    continue
                
                # Simulate based on pharmacological overlap
                simulated = self._simulate_interaction(herb, med, herb_profile, patient)
                if simulated:
                    simulated_interactions.append(simulated)
        
        return simulated_interactions
    
    def _has_known_interaction(self, herb_name: str, drug_name: str) -> bool:
        """Check if known interaction already exists"""
        herb_lower = herb_name.lower()
        drug_lower = drug_name.lower()
        
        matches = self.known_interactions_df[
            (self.known_interactions_df['herb_name'] == herb_lower) &
            (self.known_interactions_df['specific_drugs'].str.contains(drug_lower, na=False, case=False))
        ]
        return not matches.empty
    
    def _infer_herb_profile(self, herb: HerbalProduct) -> Dict:
        """Infer pharmacological profile from intended effect"""
        intended = (herb.intended_effect or "").lower()
        
        # Default profile
        profile = {
            'herb_name': herb.generic_name,
            'pharmacological_profile': {},
            'safety_concerns': []
        }
        
        # Inference rules
        if any(word in intended for word in ['sleep', 'insomnia', 'rest']):
            profile['pharmacological_profile']['sedative_like'] = 0.6
            profile['safety_concerns'].append('sedation')
        
        if any(word in intended for word in ['sugar', 'diabetes', 'glucose']):
            profile['pharmacological_profile']['hypoglycemic'] = 0.7
            profile['safety_concerns'].append('hypoglycemia')
        
        if any(word in intended for word in ['blood pressure', 'hypertension', 'bp']):
            profile['pharmacological_profile']['hypotensive'] = 0.6
            profile['safety_concerns'].append('hypotension')
        
        if any(word in intended for word in ['immunity', 'immune']):
            profile['pharmacological_profile']['immunomodulator'] = 0.6
            profile['safety_concerns'].append('immunomodulation')
        
        if any(word in intended for word in ['pain', 'inflammation', 'arthritis']):
            profile['pharmacological_profile']['anti_inflammatory'] = 0.6
            profile['pharmacological_profile']['antiplatelet'] = 0.4
            profile['safety_concerns'].append('bleeding risk')
        
        if any(word in intended for word in ['anxiety', 'stress', 'calm']):
            profile['pharmacological_profile']['anxiolytic_like'] = 0.6
            profile['pharmacological_profile']['sedative_like'] = 0.4
        
        return profile
    
    def _simulate_interaction(self, herb: HerbalProduct, med: Medication, 
                             herb_profile: Dict, patient: PatientInput) -> Optional[HerbalInteraction]:
        """Simulate potential interaction based on pharmacological profiles"""
        pharm_profile = herb_profile.get('pharmacological_profile', {})
        med_lower = med.generic_name.lower()
        
        # Sedative interactions
        if pharm_profile.get('sedative_like', 0) >= 0.5:
            if any(term in med_lower for term in ['benzodiazepine', 'zolpidem', 'zopiclone', 'alprazolam', 'diazepam', 'lorazepam']):
                return HerbalInteraction(
                    herb_name=herb.generic_name,
                    drug_name=med.generic_name,
                    interaction_type="Pharmacodynamic (simulated)",
                    mechanism="Both have sedative properties; additive CNS depression possible",
                    severity="Moderate",
                    clinical_effect="Increased sedation, drowsiness, fall risk",
                    evidence_strength=EvidenceStrength.SIMULATED,
                    recommendation="Monitor for excessive sedation. Consider reducing doses or timing separation."
                )
        
        # Hypoglycemic interactions
        if pharm_profile.get('hypoglycemic', 0) >= 0.5:
            if any(term in med_lower for term in ['insulin', 'metformin', 'glyburide', 'glipizide', 'sulfonylurea']):
                return HerbalInteraction(
                    herb_name=herb.generic_name,
                    drug_name=med.generic_name,
                    interaction_type="Pharmacodynamic (simulated)",
                    mechanism="Both may lower blood glucose; additive hypoglycemic effect",
                    severity="Moderate",
                    clinical_effect="Increased risk of hypoglycemia",
                    evidence_strength=EvidenceStrength.SIMULATED,
                    recommendation="Monitor blood glucose closely. May need to adjust diabetes medication dose."
                )
        
        # Hypotensive interactions
        if pharm_profile.get('hypotensive', 0) >= 0.5:
            if any(term in med_lower for term in ['amlodipine', 'lisinopril', 'losartan', 'metoprolol', 'atenolol']):
                return HerbalInteraction(
                    herb_name=herb.generic_name,
                    drug_name=med.generic_name,
                    interaction_type="Pharmacodynamic (simulated)",
                    mechanism="Both may lower blood pressure; additive hypotensive effect",
                    severity="Moderate",
                    clinical_effect="Risk of hypotension, dizziness, falls",
                    evidence_strength=EvidenceStrength.SIMULATED,
                    recommendation="Monitor blood pressure. Consider dose adjustment if symptomatic hypotension occurs."
                )
        
        # Antiplatelet/bleeding interactions
        if pharm_profile.get('antiplatelet', 0) >= 0.4:
            if any(term in med_lower for term in ['warfarin', 'aspirin', 'clopidogrel', 'rivaroxaban', 'apixaban']):
                return HerbalInteraction(
                    herb_name=herb.generic_name,
                    drug_name=med.generic_name,
                    interaction_type="Pharmacodynamic (simulated)",
                    mechanism="Both may affect blood clotting; increased bleeding risk",
                    severity="Major",
                    clinical_effect="Increased bleeding risk",
                    evidence_strength=EvidenceStrength.SIMULATED,
                    recommendation="Avoid combination or monitor INR/bleeding parameters closely. Inform patient of bleeding signs."
                )
        
        # Immunomodulator interactions
        if pharm_profile.get('immunomodulator', 0) >= 0.6:
            if any(term in med_lower for term in ['cyclosporine', 'tacrolimus', 'prednisone', 'azathioprine']):
                return HerbalInteraction(
                    herb_name=herb.generic_name,
                    drug_name=med.generic_name,
                    interaction_type="Pharmacodynamic (simulated)",
                    mechanism="Immune stimulation may counteract immunosuppression",
                    severity="Moderate",
                    clinical_effect="Reduced immunosuppressive effect; risk of transplant rejection",
                    evidence_strength=EvidenceStrength.SIMULATED,
                    recommendation="Avoid combination in transplant patients. Consult specialist before use."
                )
        
        return None
    
    def _generate_recommendation(self, severity: str, clinical_effect: str) -> str:
        """Generate recommendation based on interaction severity"""
        severity_lower = severity.lower()
        
        if 'major' in severity_lower:
            return f"AVOID combination. {clinical_effect}. Consult prescriber immediately."
        elif 'moderate' in severity_lower:
            return f"Use with CAUTION. {clinical_effect}. Close monitoring required."
        else:
            return f"Monitor for: {clinical_effect}."
    
    def apply_herbal_risk_modifier(self, base_risk: RiskCategory, 
                                   herb_interactions: List[HerbalInteraction]) -> Tuple[RiskCategory, List[str]]:
        """Apply risk escalation based on herb-drug interactions"""
        reasons = []
        modified_risk = base_risk
        
        for interaction in herb_interactions:
            if interaction.severity == "Major":
                if base_risk != RiskCategory.RED:
                    modified_risk = RiskCategory.RED
                    reasons.append(f"Major herb-drug interaction: {interaction.herb_name} + {interaction.drug_name} ({interaction.evidence_strength.value})")
            elif interaction.severity == "Moderate":
                if base_risk == RiskCategory.GREEN:
                    modified_risk = RiskCategory.YELLOW
                    reasons.append(f"Moderate herb-drug interaction: {interaction.herb_name} + {interaction.drug_name} ({interaction.evidence_strength.value})")
        
        return modified_risk, reasons
