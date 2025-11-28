import os
import json
import re
import math
from typing import Dict, List, Optional, Any
from urllib import response

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


class GeminiTaperService:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-pro"):
        """Initialize Gemini API client and model"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable or pass api_key.")
        genai.configure(api_key=self.api_key)
        # If your SDK differs you may need to change this line
        self.model = genai.GenerativeModel(model_name)

    # ------------------------------
    # Helpers
    # ------------------------------
    @staticmethod
    def _strip_code_fence(text: str) -> str:
        """
        Remove surrounding markdown code fences and return the inner text.
        Handles:
          ```json ... ```
          ``` ... ```
        If no fences present, returns text unchanged.
        """
        if not isinstance(text, str):
            return str(text)

        t = text.strip()
        # Simple fenced-block removal (handles ```json and ``` cases)
        m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, flags=re.S | re.I)
        if m:
            return m.group(1).strip()
        return t

    @staticmethod
    def _extract_json_substring(text: str) -> str:
        """
        Try to extract the first JSON object/array substring from text.
        Returns the substring or raises ValueError if none found.
        """
        if not isinstance(text, str):
            text = str(text)

        s = text.strip()

        # Fast check: if the whole string is valid JSON, return it
        try:
            json.loads(s)
            return s
        except Exception:
            pass

        # Find first '{' or '[' and attempt to match braces
        starts = [m.start() for m in re.finditer(r"[\{\[]", text)]
        for start in starts:
            open_char = text[start]
            close_char = "}" if open_char == "{" else "]"
            depth = 0
            for i in range(start, len(text)):
                if text[i] == open_char:
                    depth += 1
                elif text[i] == close_char:
                    depth -= 1
                    if depth == 0:
                        candidate = text[start : i + 1]
                        try:
                            json.loads(candidate)
                            return candidate
                        except Exception:
                            break  # invalid candidate; try next start
        raise ValueError("No valid JSON object/array found in model output.")

    def _get_text_from_response(self, raw_response: Any) -> str:
        """
        Extract textual content from the model response object. Supports:
        - objects with .text
        - objects with .candidates (list) / .content
        - objects with .output or .response fields
        - plain strings
        """
        if raw_response is None:
            return ""

        # Common pattern for genai SDKs: object with .text
        if hasattr(raw_response, "text") and isinstance(raw_response.text, str):
            return raw_response.text

        # genai sometimes returns candidates or content fields
        # Try common places to extract content
        if hasattr(raw_response, "candidates"):
            try:
                # candidates often is a list of objects with .content or .text
                first = raw_response.candidates[0]
                if hasattr(first, "content"):
                    return first.content
                if hasattr(first, "text"):
                    return first.text
                return str(first)
            except Exception:
                pass

        # Some APIs return dict-like objects with 'output' or 'content' keys
        try:
            if isinstance(raw_response, dict):
                for key in ("output", "content", "response", "text"):
                    if key in raw_response:
                        return raw_response[key]
                # fallback stringify
                return json.dumps(raw_response)
        except Exception:
            pass

        # Fallback to str()
        return str(raw_response)

    def _parse_model_response_to_json(self, raw_response: Any) -> Any:
        """
        Convert model response to JSON-compatible object (dict/list).
        Raises ValueError on failure.
        """
        text = self._get_text_from_response(raw_response)
        if not text:
            raise ValueError("Empty text extracted from model response.")

        # Strip fences
        cleaned = self._strip_code_fence(text)

        # 1) try direct load
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 2) try to find a JSON substring inside the cleaned text
        try:
            candidate = self._extract_json_substring(cleaned)
            return json.loads(candidate)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from model output: {e}\nRaw response excerpt: {cleaned[:500]}")

    # ------------------------------
    # Public methods
    # ------------------------------
    def generate_detailed_taper_schedule(
        self,
        drug_name: str,
        drug_class: str,
        current_dose: str,
        duration_on_med: str,
        taper_strategy: str,
        step_logic: str,
        total_weeks: int,
        patient_age: int,
        cfs_score: int,
        comorbidities: List[str],
        withdrawal_symptoms: str,
    ) -> Dict:
        """
        Use Gemini to generate detailed, personalized taper schedule.
        On failure, return conservative fallback schedule.
        """
        prompt = f"""
You are a clinical pharmacist specializing in deprescribing. Generate a detailed, week-by-week tapering schedule.

**Patient Information:**
- Age: {patient_age} years
- Clinical Frailty Scale: {cfs_score}/9
- Comorbidities: {', '.join(comorbidities) if comorbidities else 'None specified'}

**Medication Details:**
- Drug: {drug_name}
- Drug Class: {drug_class}
- Current Dose: {current_dose}
- Duration on Medication: {duration_on_med}
- Taper Strategy: {taper_strategy}

**Tapering Protocol:**
{step_logic}

**Total Tapering Duration:** {total_weeks} weeks (adjusted for frailty)

**Known Withdrawal Symptoms:** {withdrawal_symptoms}

**CRITICAL INSTRUCTIONS:**
Generate a JSON response with this EXACT structure. Each step must have a SINGLE INTEGER for the week field:

{{
  "taper_steps": [
    {{
      "week": 1,
      "dose": "specific dose with units",
      "percentage_of_original": 100,
      "instructions": "Clear patient instructions",
      "monitoring": "What to monitor this week",
      "withdrawal_symptoms_to_watch": ["symptom1", "symptom2"]
    }},
    {{
      "week": 3,
      "dose": "specific dose with units",
      "percentage_of_original": 75,
      "instructions": "Clear patient instructions",
      "monitoring": "What to monitor this week",
      "withdrawal_symptoms_to_watch": ["symptom1", "symptom2"]
    }}
  ],
  "patient_education": [
    "Education point 1",
    "Education point 2",
    "Education point 3"
  ],
  "pause_criteria": [
    "When to pause tapering - criteria 1",
    "When to pause tapering - criteria 2"
  ],
  "success_indicators": [
    "Signs tapering is going well",
    "What successful completion looks like"
  ]
}}

**STRICT REQUIREMENTS:**
1. "week" field must be a SINGLE INTEGER (e.g., 1, 3, 5) NOT a range (e.g., "1-2")
2. Create {max(4, total_weeks // 3)} to {min(8, total_weeks // 2)} steps with appropriate week intervals
3. First step should always be week 1
4. Each subsequent step should be at least 1-2 weeks apart
5. Each dose reduction should be specific with units (mg, tablets, etc.)
6. If step_logic mentions substitution, include substitution steps
7. Adjust reduction speed for frailty level {cfs_score}
8. Include specific monitoring parameters relevant to {drug_class}
9. Patient instructions must be in simple, non-medical language
10. Final step should be complete discontinuation (week {total_weeks})
11. Be extra cautious with high-risk classes (benzodiazepines, SSRIs, opioids)

**EXAMPLE of CORRECT format:**
{{
  "taper_steps": [
    {{"week": 1, "dose": "20mg", "percentage_of_original": 100, ...}},
    {{"week": 3, "dose": "15mg", "percentage_of_original": 75, ...}},
    {{"week": 5, "dose": "10mg", "percentage_of_original": 50, ...}},
    {{"week": 8, "dose": "STOP", "percentage_of_original": 0, ...}}
  ]
}}

Return ONLY valid JSON, no additional text. Do not use week ranges.
"""
        try:
            raw = self.model.generate_content(prompt)
            parsed = self._parse_model_response_to_json(raw)
            return parsed
        except Exception as e:
            print(f"[GeminiTaperService] failed to generate taper schedule: {e}")
            return self._generate_fallback_schedule(total_weeks, current_dose, patient_age, cfs_score)

    def _generate_fallback_schedule(self, total_weeks: int, current_dose: str, patient_age: int, cfs_score: int) -> Dict:
        """Fallback schedule if LLM response is unavailable or invalid."""
        frailty_multiplier = 1 + max(0, (cfs_score - 4) * 0.1)
        base_steps = max(4, total_weeks // 2)
        num_steps = math.ceil(base_steps * frailty_multiplier)

        num_steps = max(2, num_steps)
        reduction_per_step = 100 / num_steps

        steps = []
        for i in range(num_steps):
            percentage = round(max(0, 100 - reduction_per_step * i), 1)
            week = 1 + int(i * (total_weeks / num_steps))
            steps.append(
                {
                    "week": week,
                    "dose": f"{percentage}% of {current_dose}",
                    "percentage_of_original": percentage,
                    "instructions": f"Reduce dose to {percentage}% of the original. Take exactly as directed.",
                    "monitoring": "Watch for withdrawal symptoms and return of original condition",
                    "withdrawal_symptoms_to_watch": ["anxiety", "insomnia", "agitation"],
                }
            )

        # ensure final step indicates discontinuation
        if steps and steps[-1]["percentage_of_original"] > 0:
            steps.append(
                {
                    "week": total_weeks,
                    "dose": "0 (discontinue)",
                    "percentage_of_original": 0,
                    "instructions": "Stop the medication entirely. Contact clinician if issues arise.",
                    "monitoring": "Monitor for withdrawal and symptom recurrence.",
                    "withdrawal_symptoms_to_watch": ["severe withdrawal", "worsening condition"],
                }
            )

        return {
            "taper_steps": steps,
            "patient_education": [
                "Follow the schedule exactly.",
                "If you feel severe symptoms, pause and contact your clinician.",
            ],
            "pause_criteria": ["Severe withdrawal symptoms", "Marked functional decline"],
            "success_indicators": ["Minimal withdrawal symptoms", "Stable functional status"],
        }

    # ------------------------------
    # Monitoring plan via Gemini
    # ------------------------------
    def generate_monitoring_plan(
        self,
        medication_name: str,
        risk_category: str,
        risk_factors: List[str],
        patient_age: int,
        comorbidities: List[str],
    ) -> Dict:
        """
        Generate a monitoring plan for the given medication.
        Returns a dict with monitoring_schedule, alert_criteria and patient_diary_items.
        """
        prompt = f"""
You are a clinical pharmacist. Create a practical monitoring plan in JSON only.

Medication: {medication_name}
Risk category: {risk_category}
Risk factors: {', '.join(risk_factors) if risk_factors else 'None'}
Patient age: {patient_age}
Comorbidities: {', '.join(comorbidities) if comorbidities else 'None'}

Return JSON like:
{{
  "monitoring_schedule": {{
    "Week 1-2": ["parameter1", "parameter2"],
    "Week 3-4": ["parameter1", "parameter2"],
    "Monthly": ["parameter1", "parameter2"]
  }},
  "alert_criteria": ["string"],
  "patient_diary_items": ["string"]
}}

Use realistic monitoring parameters and clear alarm thresholds. Return ONLY JSON.
"""
        try:
            raw = self.model.generate_content(prompt)
            parsed = self._parse_model_response_to_json(raw)
            return parsed
        except Exception as e:
            print(f"[GeminiTaperService] monitoring plan generation failed: {e}")
            return {
                "monitoring_schedule": {"Week 1-4": ["symptom check", "blood pressure if indicated"], "Monthly": ["clinical review"]},
                "alert_criteria": ["Worsening symptoms", "New concerning signs"],
                "patient_diary_items": ["Daily symptom log", "Medication adherence"],
            }

    # ------------------------------
    # Clinical recommendations via Gemini
    # ------------------------------
    def generate_clinical_recommendations(
        self,
        patient_summary: Dict,
        red_medications: List[str],
        yellow_medications: List[str],
        interactions: List[Dict],
    ) -> List[str]:
        """Generate personalized clinical recommendations using Gemini"""

        prompt = f"""
You are a clinical pharmacist reviewing a patient's medication regimen.

**Patient Summary:**
- Age: {patient_summary.get('age')}
- Frailty: {patient_summary.get('frailty_status')}
- CFS Score: {patient_summary.get('cfs_score')}
- Life Expectancy: {patient_summary.get('life_expectancy')}
- Comorbidities: {', '.join(patient_summary.get('comorbidities', []))}

**High-Priority Medications (RED):** {', '.join(red_medications) if red_medications else 'None'}
**Review-Needed Medications (YELLOW):** {', '.join(yellow_medications) if yellow_medications else 'None'}

**Herb-Drug Interactions:** {len(interactions)} identified

Generate 5–7 prioritized clinical recommendations for clinicians.

Requirements:
1. Start with urgent/high-risk items first.
2. Be specific and actionable.
3. Adjust for frailty and life expectancy.
4. Address polypharmacy.
5. Mention serious herb–drug interactions.
6. Include monitoring items.
7. Ensure recommendations fit goals of care.

Return ONLY valid JSON array of strings:

[
  "Recommendation 1",
  "Recommendation 2"
]
"""
        try:
            raw = self.model.generate_content(prompt)
            parsed = self._parse_model_response_to_json(raw)

            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                return parsed

            # If model returned dict with key 'recommendations' or similar, try extracting it
            if isinstance(parsed, dict):
                for key in ("recommendations", "clinical_recommendations", "results"):
                    if key in parsed and isinstance(parsed[key], list):
                        return [str(x) for x in parsed[key]]

            raise ValueError("Model did not return a JSON array of strings.")
        except Exception as e:
            print(f"[GeminiTaperService] Clinical recommendation generation failed: {e}")
            return [
                "Reassess high-risk medications and consider deprescribing.",
                "Evaluate benzodiazepine use, especially in frail older adults.",
                "Monitor for herb–drug interactions and adjust therapy accordingly.",
                "Review goals of care with patient and family.",
                "Monitor cognition, fall risk, and sedation weekly.",
                "Simplify regimen to reduce polypharmacy burden."
            ]
        
    def get_drug_information(self, drug_name: str) -> Dict:
        """Extract detailed drug information using Gemini with strong JSON guarantees."""

        prompt = f"""
    You are a clinical pharmacologist. Provide comprehensive information about the medication: {drug_name}

    Return a JSON object with this EXACT structure:

    {{
    "drug_class": "Primary drug class (e.g., Benzodiazepine, SSRI, PPI, Beta-blocker)",
    "risk_profile": "High-risk" or "Standard" or "Low-risk",
    "taper_strategy_name": "Name of recommended tapering approach",
    "step_logic": "Detailed tapering instructions (e.g., 'Reduce by 25% every 2 weeks' or 'Ashton substitution protocol')",
    "withdrawal_symptoms": "Common withdrawal symptoms (comma-separated)",
    "monitoring_frequency": "Recommended monitoring frequency during taper",
    "pause_criteria": "When to pause tapering",
    "requires_taper": true or false,
    "typical_duration_weeks": 4 to 24,
    "special_considerations": "Any special considerations for elderly/frail patients"
    }}

    Guidelines:
    1. If this is a HIGH-RISK medication (benzodiazepines, SSRIs, SNRIs, opioids, corticosteroids), set requires_taper: true
    2. For standard medications (statins, ACE inhibitors, metformin), requires_taper: false
    3. Withdrawal symptoms must be specific and relevant to the drug class
    4. Output must consider elderly deprescribing safety
    5. If drug name is unknown or misspelled, infer based on closest known medication
    6. Return ONLY valid JSON — no commentary, no markdown.
    """

        try:
            raw = self.model.generate_content(prompt)

            # Clean output (handles ```json, ``` fences and raw text)
            cleaned = self._strip_code_fence(raw.text)

            # Try direct JSON load
            try:
                drug_info = json.loads(cleaned)
            except json.JSONDecodeError:
                # Extract inner JSON substring
                candidate = self._extract_json_substring(cleaned)
                drug_info = json.loads(candidate)

            # Required keys
            required_fields = [
                "drug_class",
                "risk_profile",
                "taper_strategy_name",
                "step_logic",
                "withdrawal_symptoms",
                "monitoring_frequency",
                "pause_criteria",
                "requires_taper",
                "typical_duration_weeks",
                "special_considerations",
            ]

            # Insert defaults for missing fields
            for field in required_fields:
                if field not in drug_info:
                    print(f"⚠️ Missing {field} in Gemini response — inserting default.")
                    drug_info[field] = "Unknown"

            print(f"✅ Gemini extracted drug info for {drug_name}:")
            print(f"   Class: {drug_info.get('drug_class')}")
            print(f"   Risk: {drug_info.get('risk_profile')}")
            print(f"   Requires Taper: {drug_info.get('requires_taper')}")

            return drug_info
           
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error for {drug_name}: {e}")
            print(f"Raw response: {response.text[:200]}")
            return self._get_fallback_drug_info(drug_name)
            
        except Exception as e:
            print(f"❌ Gemini API error for {drug_name}: {e}")
            return self._get_fallback_drug_info(drug_name)

    def _get_fallback_drug_info(self, drug_name: str) -> Dict:
        """Fallback drug information if Gemini fails"""
        return {
            "drug_class": "Unknown",
            "risk_profile": "Standard",
            "taper_strategy_name": "Gradual Reduction",
            "step_logic": "Reduce by 25% every 2 weeks",
            "withdrawal_symptoms": "Possible return of symptoms, general discomfort",
            "monitoring_frequency": "Weekly",
            "pause_criteria": "Severe symptoms or patient distress",
            "requires_taper": False,
            "typical_duration_weeks": 4,
            "special_considerations": "Consult healthcare provider for personalized plan"
        }
