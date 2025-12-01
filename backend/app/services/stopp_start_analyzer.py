import pandas as pd
from typing import List, Dict, Any, Optional
import re

class STOPPSTARTAnalyzer:
    """Analyzer for STOPP/START v2 clinical criteria"""
    
    def __init__(self, stopp_df: pd.DataFrame, start_df: pd.DataFrame):
        self.stopp_df = stopp_df
        self.start_df = start_df
        
        # Drug class mappings for better matching
        self.drug_class_map = self._build_drug_class_map()
    
    def _build_drug_class_map(self) -> Dict[str, List[str]]:
        """Build mapping of drug classes to specific medications"""
        return {
            'benzodiazepines': ['alprazolam', 'lorazepam', 'diazepam', 'clonazepam', 'temazepam', 'triazolam', 'zolpidem', 'zaleplon', 'eszopiclone'],
            'tricyclic antidepressants': ['amitriptyline', 'nortriptyline', 'imipramine', 'doxepin', 'desipramine', 'clomipramine'],
            'ssri': ['fluoxetine', 'sertraline', 'paroxetine', 'citalopram', 'escitalopram', 'fluvoxamine'],
            'nsaid': ['ibuprofen', 'naproxen', 'diclofenac', 'celecoxib', 'meloxicam', 'indomethacin', 'ketorolac', 'piroxicam'],
            'ppi': ['omeprazole', 'esomeprazole', 'lansoprazole', 'pantoprazole', 'rabeprazole'],
            'antihistamines': ['diphenhydramine', 'chlorpheniramine', 'hydroxyzine', 'promethazine', 'cyclizine'],
            'antipsychotics': ['haloperidol', 'risperidone', 'quetiapine', 'olanzapine', 'aripiprazole', 'chlorpromazine'],
            'opioids': ['morphine', 'oxycodone', 'hydrocodone', 'fentanyl', 'tramadol', 'codeine', 'hydromorphone'],
            'acei': ['lisinopril', 'enalapril', 'ramipril', 'captopril', 'perindopril', 'quinapril'],
            'arb': ['losartan', 'valsartan', 'irbesartan', 'candesartan', 'olmesartan', 'telmisartan'],
            'beta-blocker': ['metoprolol', 'atenolol', 'bisoprolol', 'carvedilol', 'propranolol', 'nebivolol'],
            'thiazide': ['hydrochlorothiazide', 'chlorthalidone', 'indapamide', 'metolazone'],
            'loop diuretic': ['furosemide', 'torsemide', 'bumetanide', 'ethacrynic acid'],
            'statin': ['atorvastatin', 'simvastatin', 'rosuvastatin', 'pravastatin', 'lovastatin', 'fluvastatin'],
            'anticoagulant': ['warfarin', 'apixaban', 'rivaroxaban', 'dabigatran', 'edoxaban'],
            'antiplatelet': ['aspirin', 'clopidogrel', 'prasugrel', 'ticagrelor'],
            'sulfonylurea': ['glyburide', 'glipizide', 'glimepiride', 'chlorpropamide'],
            'bisphosphonate': ['alendronate', 'risedronate', 'ibandronate', 'zoledronic acid'],
            'alpha-blocker': ['tamsulosin', 'doxazosin', 'alfuzosin', 'terazosin'],
            'anticholinergic': ['oxybutynin', 'tolterodine', 'solifenacin', 'darifenacin', 'fesoterodine']
        }
    
    def analyze_medication(self, 
                          drug_name: str, 
                          patient_conditions: List[str],
                          patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if medication violates STOPP criteria
        
        Args:
            drug_name: Name of the medication
            patient_conditions: List of patient conditions/comorbidities
            patient_data: Patient information (age, labs, etc.)
        
        Returns:
            Dict with stopp_flags, severity, and should_stop
        """
        flags = []
        
        # Normalize drug name
        drug_lower = drug_name.lower().strip()
        
        # Check each STOPP criterion
        for _, criterion in self.stopp_df.iterrows():
            # Check if drug matches
            if self._matches_drug(drug_lower, criterion['drug_class']):
                # Check if patient condition matches
                if self._matches_condition(patient_conditions, patient_data, criterion['condition']):
                    flags.append({
                        'criterion_id': criterion['criterion_id'],
                        'criterion': criterion['criterion'],
                        'drug_class': criterion['drug_class'],
                        'condition': criterion['condition'],
                        'rationale': criterion['rationale'],
                        'action': criterion['action'],
                        'severity': criterion['severity'],
                        'system': criterion['system']
                    })
        
        # Determine overall severity
        has_high = any(f['severity'] == 'High' for f in flags)
        overall_severity = 'High' if has_high else 'Moderate' if flags else 'None'
        
        return {
            'stopp_flags': flags,
            'severity': overall_severity,
            'should_stop': len(flags) > 0,
            'flag_count': len(flags)
        }
    
    def recommend_start_medications(self, 
                                   patient_conditions: List[str],
                                   current_medications: List[str],
                                   patient_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify missing appropriate medications (START criteria)
        
        Args:
            patient_conditions: List of patient conditions
            current_medications: List of current medications
            patient_data: Patient information
        
        Returns:
            List of START recommendations
        """
        recommendations = []
        
        # Normalize current medications
        current_meds_lower = [med.lower().strip() for med in current_medications]
        
        for _, criterion in self.start_df.iterrows():
            # Check if patient meets the condition for this START criterion
            if self._matches_condition(patient_conditions, patient_data, criterion['condition']):
                # Check if patient is NOT already on this medication class
                if not self._already_on_medication(current_meds_lower, criterion['drug_class']):
                    recommendations.append({
                        'criterion_id': criterion['criterion_id'],
                        'criterion': criterion['criterion'],
                        'drug_class': criterion['drug_class'],
                        'condition': criterion['condition'],
                        'indication': criterion['indication'],
                        'recommendation': criterion['recommendation'],
                        'evidence': criterion['evidence'],
                        'system': criterion['system']
                    })
        
        # Sort by evidence level (Strong first)
        recommendations.sort(key=lambda x: 0 if x['evidence'] == 'Strong' else 1)
        
        return recommendations
    
    def _matches_drug(self, drug_name: str, drug_class_pattern: str) -> bool:
        """Check if drug matches the drug class pattern"""
        drug_lower = drug_name.lower()
        pattern_lower = drug_class_pattern.lower()
        
        # Direct substring match
        if drug_lower in pattern_lower or pattern_lower in drug_lower:
            return True
        
        # Check drug class mappings
        for drug_class, medications in self.drug_class_map.items():
            if drug_class in pattern_lower:
                if any(med in drug_lower for med in medications):
                    return True
            # Check if drug is in the medication list
            if drug_lower in medications:
                if drug_class in pattern_lower:
                    return True
        
        # Special pattern matching
        # TCAs
        if 'tricyclic' in pattern_lower or 'tca' in pattern_lower:
            if drug_lower in ['amitriptyline', 'nortriptyline', 'imipramine', 'doxepin', 'dosulepin']:
                return True
        
        # First-generation antihistamines
        if 'first-generation' in pattern_lower or 'antihistamine' in pattern_lower:
            if drug_lower in ['diphenhydramine', 'chlorpheniramine', 'hydroxyzine', 'promethazine', 'cyclizine']:
                return True
        
        return False
    
    def _matches_condition(self, 
                          patient_conditions: List[str],
                          patient_data: Dict[str, Any],
                          criterion_condition: str) -> bool:
        """Check if patient meets the condition criteria"""
        condition_lower = criterion_condition.lower()
        
        # Check comorbidities
        for condition in patient_conditions:
            condition_norm = condition.lower().strip()
            if condition_norm in condition_lower or condition_lower in condition_norm:
                return True
        
        # Check specific clinical parameters
        # eGFR checks
        if 'egfr' in condition_lower:
            egfr = patient_data.get('egfr') or patient_data.get('creatinine_clearance')
            if egfr is not None:
                if '<30' in condition_lower or '< 30' in condition_lower:
                    return egfr < 30
                elif '<50' in condition_lower or '< 50' in condition_lower:
                    return egfr < 50
                elif '<15' in condition_lower or '< 15' in condition_lower:
                    return egfr < 15
        
        # Blood pressure checks
        if 'sbp' in condition_lower or 'systolic' in condition_lower:
            sbp = patient_data.get('systolic_bp')
            if sbp is not None:
                if '>160' in condition_lower:
                    return sbp > 160
                elif '>140' in condition_lower:
                    return sbp > 140
        
        if 'dbp' in condition_lower or 'diastolic' in condition_lower:
            dbp = patient_data.get('diastolic_bp')
            if dbp is not None:
                if '>90' in condition_lower:
                    return dbp > 90
        
        # Electrolyte checks
        if 'k+' in condition_lower or 'potassium' in condition_lower:
            k = patient_data.get('potassium')
            if k is not None:
                if '<3.0' in condition_lower:
                    return k < 3.0
                elif '>6.0' in condition_lower:
                    return k > 6.0
        
        if 'na+' in condition_lower or 'sodium' in condition_lower:
            na = patient_data.get('sodium')
            if na is not None:
                if '<130' in condition_lower:
                    return na < 130
        
        # Falls check
        if 'fall' in condition_lower:
            recent_falls = patient_data.get('recent_falls', False)
            return recent_falls
        
        # Age-related conditions
        if 'age' in condition_lower:
            age = patient_data.get('age')
            if age is not None:
                if '≥65' in condition_lower or '>= 65' in condition_lower or '>65' in condition_lower:
                    return age >= 65
                elif '≥85' in condition_lower or '>= 85' in condition_lower:
                    return age >= 85
        
        return False
    
    def _already_on_medication(self, current_medications: List[str], drug_class: str) -> bool:
        """Check if patient is already on medication from this class"""
        for med in current_medications:
            if self._matches_drug(med, drug_class):
                return True
        return False
    
    def get_stopp_statistics(self) -> Dict[str, Any]:
        """Get statistics about STOPP criteria"""
        return {
            'total_criteria': len(self.stopp_df),
            'high_severity': len(self.stopp_df[self.stopp_df['severity'] == 'High']),
            'moderate_severity': len(self.stopp_df[self.stopp_df['severity'] == 'Moderate']),
            'by_system': self.stopp_df['system'].value_counts().to_dict()
        }
    
    def get_start_statistics(self) -> Dict[str, Any]:
        """Get statistics about START criteria"""
        return {
            'total_criteria': len(self.start_df),
            'strong_evidence': len(self.start_df[self.start_df['evidence'] == 'Strong']),
            'moderate_evidence': len(self.start_df[self.start_df['evidence'] == 'Moderate']),
            'by_system': self.start_df['system'].value_counts().to_dict()
        }
