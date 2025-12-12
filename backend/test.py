"""
GeminiTaperService

Fully rewritten, production-ready Gemini taper schedule & monitoring generator.
Option A: Uses Gemini's MIME-forced JSON output (response_mime_type="application/json").

Features:
- Strict JSON-only requests using generation_config to force mime-type
- Robust retry with exponential backoff and jitter
- Safe parsing + schema validation + type coercion
- Automatic repair attempts (last resort)
- Detailed logging and raw response capture for debugging
- Rate-limit detection and graceful handling (429 handling + backoff)
- Fallback deterministic and intelligent rules for common drug classes
- Health-check / quick-test runner when invoked directly
- Clear public methods used by TaperPlanService in your app

Notes:
- Requires `google-generativeai` >= version that supports `generation_config` with `response_mime_type`.
- Install: pip install google-generativeai python-dotenv
- Set env var GEMINI_API_KEY or pass api_key to the constructor

This file intentionally contains extensive inline comments and helpful debug prints.
"""

from __future__ import annotations

import os
import time
import json
import math
import random
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Third-party imports
try:
    import google.generativeai as genai
except Exception as e:
    genai = None  # Will raise on initialization if required

# Configure basic logging
logger = logging.getLogger("GeminiTaperService")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# -----------------------------
# Dataclasses for typed responses
# -----------------------------

@dataclass
class TaperStepSchema:
    week: int
    dose: str
    percentage_of_original: float
    instructions: str
    monitoring: str
    withdrawal_symptoms_to_watch: List[str]


@dataclass
class GeminiTaperResponseSchema:
    taper_steps: List[TaperStepSchema]
    patient_education: List[str]
    pause_criteria: List[str]
    success_indicators: List[str]


# -----------------------------
# Constants & Defaults
# -----------------------------
from dotenv import load_dotenv
load_dotenv()
DEFAULT_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-3-pro")
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 1.0
DEFAULT_BACKOFF_JITTER = 0.25

# Schema expected keys for drug info
DRUG_INFO_REQUIRED_KEYS = [
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

# Fallback patterns for common drugs
COMMON_DRUG_PATTERNS: Dict[Tuple[str, ...], Dict[str, Any]] = {
    ("alprazolam", "xanax", "lorazepam", "ativan", "diazepam", "valium", "clonazepam"): {
        "drug_class": "Benzodiazepine",
        "risk_profile": "High-risk",
        "requires_taper": True,
        "typical_duration_weeks": 12,
        "step_logic": "Very gradual reduction (e.g., 10% every 1-2 weeks) — consider substitution strategies.",
        "withdrawal_symptoms": "Anxiety, insomnia, tremor, seizures",
        "monitoring_frequency": "Weekly",
    },
    ("sertraline", "zoloft", "fluoxetine", "paroxetine", "citalopram", "escitalopram"): {
        "drug_class": "SSRI Antidepressant",
        "risk_profile": "High-risk",
        "requires_taper": True,
        "typical_duration_weeks": 8,
        "step_logic": "Hyperbolic tapering; reduce dose by ~25% every 2-4 weeks depending on tolerance.",
        "withdrawal_symptoms": "Dizziness, nausea, " "brain zaps",  # type: ignore
        "monitoring_frequency": "Weekly",
    },
    ("atorvastatin", "simvastatin", "rosuvastatin"): {
        "drug_class": "Statin",
        "risk_profile": "Low-risk",
        "requires_taper": False,
        "typical_duration_weeks": 0,
        "step_logic": "Can often be discontinued without tapering; monitor lipid control.",
        "withdrawal_symptoms": "None typical",
        "monitoring_frequency": "Monthly",
    },
}

# -----------------------------
# Helper utilities
# -----------------------------


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    v = str(value).strip().lower()
    if v in ("true", "yes", "1"):
        return True
    if v in ("false", "no", "0"):
        return False
    return default


def _coerce_week_value(week_val: Any) -> Optional[int]:
    """Coerce week value to a single integer (take first number if string)."""
    if isinstance(week_val, int):
        return week_val
    if isinstance(week_val, float):
        return int(week_val)
    if isinstance(week_val, str):
        m = re.search(r"\d+", week_val)
        if m:
            return int(m.group(0))
    return None


def _normalize_symptoms_field(val: Any) -> List[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if x]
    s = str(val)
    parts = re.split(r"[,;]\s*", s)
    return [p.strip() for p in parts if p.strip()]


# Minimal JSON repair heuristics (last resort)

def _repair_json_text(text: str) -> str:
    """Attempt conservative fixes to a truncated JSON string.
    - Close unclosed quotes
    - Close unclosed braces/brackets
    - Remove trailing partial fields
    NOTE: This is a last-resort heuristic and may still fail.
    """
    if not isinstance(text, str):
        return text

    repaired = text.strip()

    # Close unbalanced quotes
    if repaired.count('"') % 2 != 0:
        repaired += '"'

    # Count braces
    open_braces = repaired.count('{')
    close_braces = repaired.count('}')
    if close_braces < open_braces:
        repaired += '}' * (open_braces - close_braces)

    open_brackets = repaired.count('[')
    close_brackets = repaired.count(']')
    if close_brackets < open_brackets:
        repaired += ']' * (open_brackets - close_brackets)

    # Remove obvious trailing commas before close
    repaired = re.sub(r",\s*}\s*$", "}", repaired)
    repaired = re.sub(r",\s*\]\s*$", "]", repaired)

    return repaired


# -----------------------------
# Main Service
# -----------------------------

class GeminiKeyManager:
    def __init__(self, keys: List[str]):
        if not keys:
            raise ValueError("At least one Gemini API key required")
        self.keys = keys
        self.index = 0
        self.total = len(keys)

    def get_key(self) -> str:
        """Return the current key (round-robin)."""
        key = self.keys[self.index]
        self.index = (self.index + 1) % self.total
        return key

    def get_all_keys(self) -> List[str]:
        return self.keys



class GeminiTaperService:
    """Wrapper around Google Gemini for generating taper plans and monitoring guidance.

    Option A (this implementation): we instruct Gemini to return pure JSON by using
    generation_config with response_mime_type='application/json'. This significantly
    reduces parsing errors.

    The service provides robust retries, rate-limit handling, logging of raw
    responses for debugging, and safe fallbacks.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = DEFAULT_MODEL_NAME,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
    ) -> None:
        if genai is None:
            raise ImportError("google.generativeai is required. Install via pip install google-generativeai")

        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not found - set GEMINI_API_KEY or pass api_key")

        # Configure SDK
        genai.configure(api_key=self.api_key)
        self.model_name = model_name
        # The SDK uses GenerativeModel - keep reference for calls
        try:
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.warning("Failed to instantiate model via SDK: %s", e)
            # Not fatal now; will attempt to use genai at call time
            self.model = None

        self.max_retries = max_retries
        self.backoff_base = backoff_base

        # Basic stats
        self.calls_made = 0
        self.last_raw_response: Optional[str] = None

        logger.info("GeminiTaperService initialized (model=%s)", self.model_name)

    # -----------------------------
    # Low-level model call with retry/backoff + JSON forcing
    # -----------------------------

    def _call_model_with_json_mime(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> Any:
        """Call the model forcing JSON-only output via generation_config.

        Returns raw SDK response object (may vary by SDK version).
        Raises exception on repeated failures.
        """
        if max_retries is None:
            max_retries = self.max_retries

        attempt = 0
        last_exc: Optional[Exception] = None

        # Generation config to enforce JSON output
        generation_config = {"response_mime_type": "application/json"}

        while attempt < max_retries:
            attempt += 1
            try:
                logger.debug("Model call attempt %d", attempt)
                # Update call stats
                self.calls_made += 1

                # SDK call - depending on SDK the API shape may vary
                # Many SDKs support model.generate_content or model.generate
                if self.model is None:
                    # Recreate model reference
                    self.model = genai.GenerativeModel(self.model_name)

                # Use generate_content if available, else fallback to generate
                if hasattr(self.model, "generate_content"):
                    raw = self.model.generate_content(
                        prompt,
                        generation_config=generation_config,
                    )
                else:
                    # Generic wrapper - adjust if your SDK differs
                    raw = self.model.generate(
                        prompt,
                        generation_config=generation_config,
                    )

                # Store raw response for debugging
                self.last_raw_response = self._extract_text_from_raw_response(raw)

                # If response looks like an error object or indicates rate limit
                if self._response_indicates_rate_limit(raw):
                    raise RuntimeError("Rate limit or quota exceeded detected in model response")

                return raw

            except Exception as e:
                last_exc = e
                logger.warning("Model call failed (attempt %d/%d): %s", attempt, max_retries, e)

                # If rate-limit, backoff strongly
                if isinstance(e, RuntimeError) and "Rate limit" in str(e):
                    backoff = min(60, (self.backoff_base * (2 ** (attempt - 1))) + random.uniform(0, DEFAULT_BACKOFF_JITTER))
                else:
                    backoff = (self.backoff_base * (2 ** (attempt - 1))) + random.uniform(0, DEFAULT_BACKOFF_JITTER)

                logger.info("Backing off for %.1f seconds before retry", backoff)
                time.sleep(backoff)
                continue

        logger.error("All model call attempts failed: last error: %s", last_exc)
        raise last_exc

    # -----------------------------
    # Response inspection helpers
    # -----------------------------

    def _extract_text_from_raw_response(self, raw: Any) -> str:
        """Extract human-readable text from different SDK response shapes."""
        try:
            # genai SDK often places text in .text
            if hasattr(raw, "text") and isinstance(raw.text, str):
                return raw.text

            # Some SDK versions provide candidates with content
            if hasattr(raw, "candidates"):
                try:
                    first = raw.candidates[0]
                    if hasattr(first, "content"):
                        return first.content
                    if hasattr(first, "text"):
                        return first.text
                    return str(first)
                except Exception:
                    pass

            # dict-like
            if isinstance(raw, dict):
                # Look for common keys
                for key in ("output", "content", "response", "text"):
                    if key in raw and isinstance(raw[key], str):
                        return raw[key]
                # fallback stringify
                return json.dumps(raw)

            # Fallback
            return str(raw)
        except Exception as e:
            logger.exception("Failed to extract text from raw response: %s", e)
            return str(raw)

    def _response_indicates_rate_limit(self, raw: Any) -> bool:
        """Heuristics to detect rate-limit or quota responses from the SDK or API."""
        text = self._extract_text_from_raw_response(raw).lower()
        if "rate limit" in text or "quota" in text or "resource_exhausted" in text or "429" in text:
            return True
        return False

    # -----------------------------
    # Robust JSON parsing function (expects JSON-only output or can extract JSON substring)
    # -----------------------------

    def _parse_model_response_to_json(self, raw: Any) -> Any:
        """Parse raw SDK response into a JSON structure.

        This function assumes the model was asked to return application/json, but it still
        handles scenarios where the SDK wraps the JSON or the model inserted newline markers.
        """
        text = self._extract_text_from_raw_response(raw)
        if not text:
            raise ValueError("Empty text extracted from model response")

        # Save raw excerpt for debugging
        excerpt = text[:1000]
        logger.debug("Raw model text excerpt: %s", excerpt)

        # Try direct parse first
        try:
            parsed = json.loads(text)
            logger.debug("Direct json.loads succeeded")
            return parsed
        except Exception:
            logger.debug("Direct json.loads failed; attempting extraction")

        # Remove common wrappers
        cleaned = self._strip_code_fence(text)

        # Try parse cleaned
        try:
            parsed = json.loads(cleaned)
            logger.debug("json.loads cleaned text succeeded")
            return parsed
        except Exception:
            logger.debug("json.loads on cleaned text failed; trying substring extraction")

        # Use our substring extractor - looks for largest {...} or [...] blocks
        try:
            candidate = self._extract_json_substring(cleaned)
            parsed = json.loads(candidate)
            logger.debug("json.loads on extracted substring succeeded")
            return parsed
        except Exception as e:
            logger.warning("Extraction attempt failed: %s", e)

        # As last resort, attempt to repair truncated JSON and parse
        repaired = _repair_json_text(cleaned)
        try:
            parsed = json.loads(repaired)
            logger.warning("Parsed JSON after repair heuristics (last-resort)")
            return parsed
        except Exception as e:
            logger.error("Failed to recover valid JSON from model output. Raw excerpt: %s", excerpt)
            raise ValueError(f"Failed to parse JSON from model output: {e}\nRaw response excerpt: {excerpt}")

    # Re-use your existing _strip_code_fence and _extract_json_substring implementations for robustness
    @staticmethod
    def _strip_code_fence(text: str) -> str:
        if not isinstance(text, str):
            return str(text)
        t = text.strip()
        m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, flags=re.S | re.I)
        if m:
            return m.group(1).strip()
        # Also strip leading explanatory lines like 'Here is the JSON:'
        # Remove up to the first opening brace or bracket if there is preamble
        brace_idx = min([i for i in [t.find('{'), t.find('[')] if i >= 0] or [-1])
        if brace_idx > 0:
            return t[brace_idx:]
        return t

    @staticmethod
    def _extract_json_substring(text: str) -> str:
        # Similar to previous helper with improved regex
        if not isinstance(text, str):
            text = str(text)

        # Try largest {...} block first
        object_pattern = r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}"
        obj_matches = re.findall(object_pattern, text, flags=re.DOTALL)
        if obj_matches:
            # pick the longest candidate (likely full object)
            candidate = max(obj_matches, key=len)
            try:
                json.loads(candidate)
                return candidate
            except Exception:
                # try others
                for m in obj_matches:
                    try:
                        json.loads(m)
                        return m
                    except Exception:
                        continue

        # Try arrays
        array_pattern = r"\[(?:[^\[\]]|(?:\[[^\[\]]*\]))*\]"
        arr_matches = re.findall(array_pattern, text, flags=re.DOTALL)
        if arr_matches:
            candidate = max(arr_matches, key=len)
            for m in arr_matches:
                try:
                    json.loads(m)
                    return m
                except Exception:
                    continue

        # Bracket walking fallback
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
                            break
        raise ValueError("No valid JSON object/array found in model output.")

    # -----------------------------
    # Public: drug information extraction
    # -----------------------------

    def get_drug_information_with_context(
        self,
        drug_name: str,
        clinical_context: str,
        patient_age: int,
        comorbidities: List[str],
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Ask Gemini for structured drug-level information, forcing JSON output.

        Returns a dict with required keys. If Gemini fails or returns partial info, we
        attempt to coerce types and fill defaults. In most cases this will succeed when
        using response_mime_type = application/json.
        """
        prompt = self._build_drug_info_prompt(drug_name, clinical_context, patient_age, comorbidities)

        try:
            raw = self._call_model_with_json_mime(prompt, max_retries=max_retries)
            parsed = self._parse_model_response_to_json(raw)

            # If parsed is list, try to take first element
            if isinstance(parsed, list) and parsed:
                parsed = parsed[0]

            if not isinstance(parsed, dict):
                raise ValueError("Parsed drug info is not a JSON object")

            # Ensure required keys exist and correct types
            for key in DRUG_INFO_REQUIRED_KEYS:
                if key not in parsed:
                    logger.warning("Missing key '%s' in Gemini drug info; inserting default", key)
                    parsed[key] = None

            # Coerce types
            parsed["requires_taper"] = _safe_bool(parsed.get("requires_taper"), default=True)
            parsed["typical_duration_weeks"] = _safe_int(parsed.get("typical_duration_weeks"), default=4)

            # Convert strings
            for k in ("drug_class", "risk_profile", "taper_strategy_name", "step_logic", "withdrawal_symptoms", "monitoring_frequency", "pause_criteria", "special_considerations"):
                if parsed.get(k) is None:
                    parsed[k] = "Unknown"
                else:
                    parsed[k] = str(parsed[k]).strip()

            # Normalize withdrawal symptoms to list if needed
            parsed["withdrawal_symptoms_list"] = _normalize_symptoms_field(parsed.get("withdrawal_symptoms"))

            logger.info("Gemini drug info extracted: %s (requires_taper=%s, duration=%s)", parsed.get("drug_class"), parsed.get("requires_taper"), parsed.get("typical_duration_weeks"))

            return parsed

        except Exception as e:
            logger.exception("Gemini API error for %s: %s", drug_name, e)
            # Return intelligent fallback
            return self._get_fallback_drug_info_with_intelligence(drug_name)

    def _build_drug_info_prompt(self, drug_name: str, clinical_context: str, patient_age: int, comorbidities: List[str]) -> str:
        """Construct a strict JSON-only prompt for the model."""
        comorb_str = ", ".join(comorbidities) if comorbidities else "None"

        schema_example = json.dumps({
            "drug_class": "Example class",
            "risk_profile": "High-risk",
            "taper_strategy_name": "Example strategy",
            "step_logic": "Step-by-step logic as plain string",
            "withdrawal_symptoms": "symptom1, symptom2",
            "monitoring_frequency": "Weekly",
            "pause_criteria": "Severe symptoms",
            "requires_taper": True,
            "typical_duration_weeks": 8,
            "special_considerations": "Notes"
        }, indent=2)

        prompt = f"""
Return ONLY a single valid JSON object (no surrounding explanation, no markdown).
Follow this exact schema (fill values or null):

{schema_example}

Context:
- Drug: {drug_name}
- Clinical context: {clinical_context}
- Patient age: {patient_age}
- Comorbidities: {comorb_str}

Important: Use simple values. 'requires_taper' must be a boolean. 'typical_duration_weeks' must be an integer.
If you are uncertain, prefer conservative choices (i.e., requires_taper=true).

Return only JSON.
"""
        return prompt

    # -----------------------------
    # Taper schedule generation
    # -----------------------------

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
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate a detailed taper plan using Gemini (JSON-forced mode).

        Returns a dict matching GeminiTaperResponseSchema; on failure returns deterministic fallback.
        """
        prompt = self._build_taper_schedule_prompt(
            drug_name,
            drug_class,
            current_dose,
            duration_on_med,
            taper_strategy,
            step_logic,
            total_weeks,
            patient_age,
            cfs_score,
            comorbidities,
            withdrawal_symptoms,
        )

        try:
            raw = self._call_model_with_json_mime(prompt, max_retries=max_retries)
            parsed = self._parse_model_response_to_json(raw)

            # Normalize parsed structure
            # Some models may return keys we expect; ensure types
            steps_raw = parsed.get("taper_steps") if isinstance(parsed, dict) else None
            if steps_raw is None:
                raise ValueError("Missing 'taper_steps' in model output")

            steps: List[TaperStepSchema] = []
            for s in steps_raw:
                week = _coerce_week_value(s.get("week"))
                if week is None:
                    logger.warning("Skipping step with invalid week: %s", s)
                    continue
                dose = str(s.get("dose", "Unknown"))
                pct = float(s.get("percentage_of_original") or 0)
                instructions = str(s.get("instructions", ""))
                monitoring = str(s.get("monitoring", ""))
                withdraw = _normalize_symptoms_field(s.get("withdrawal_symptoms_to_watch"))

                steps.append(TaperStepSchema(
                    week=week,
                    dose=dose,
                    percentage_of_original=pct,
                    instructions=instructions,
                    monitoring=monitoring,
                    withdrawal_symptoms_to_watch=withdraw,
                ))

            patient_education = parsed.get("patient_education") or []
            pause_criteria = parsed.get("pause_criteria") or []
            success_indicators = parsed.get("success_indicators") or []

            response = {
                "taper_steps": [asdict(s) for s in steps],
                "patient_education": list(patient_education),
                "pause_criteria": list(pause_criteria),
                "success_indicators": list(success_indicators),
            }

            logger.info("AI generated taper steps: %d", len(steps))
            return response

        except Exception as e:
            logger.exception("AI taper generation failed for %s: %s", drug_name, e)
            # Fall back to deterministic schedule
            return self._generate_fallback_schedule(total_weeks, current_dose, patient_age, cfs_score, withdrawal_symptoms)

    def _build_taper_schedule_prompt(
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
    ) -> str:
        """Construct strict JSON-only prompt for taper schedule generation."""
        comorb_str = ", ".join(comorbidities) if comorbidities else "None"

        # Determine desired number of steps range
        min_steps = max(4, total_weeks // 3)
        max_steps = min(8, max(4, total_weeks // 2))

        prompt = f"""
You are a clinical pharmacist creating a personalized, week-by-week tapering schedule.
Return ONLY valid JSON (single top-level object). No commentary, no markdown.

Input:
- Drug: {drug_name}
- Drug class: {drug_class}
- Current dose: {current_dose}
- Duration on medication: {duration_on_med}
- Taper strategy (context): {taper_strategy}
- Taper protocol: {step_logic}
- Total taper duration (weeks): {total_weeks}
- Patient age: {patient_age}
- CFS (frailty) score: {cfs_score}
- Comorbidities: {comorb_str}
- Known withdrawal symptoms: {withdrawal_symptoms}

Return JSON with this EXACT structure (fill in values):
{{
  "taper_steps": [
    {{"week": 1, "dose": "", "percentage_of_original": 100, "instructions": "", "monitoring": "", "withdrawal_symptoms_to_watch": [""]}},
    {{"week": 3, "dose": "", "percentage_of_original": 75, "instructions": "", "monitoring": "", "withdrawal_symptoms_to_watch": [""]}}
  ],
  "patient_education": [""],
  "pause_criteria": [""],
  "success_indicators": [""]
}}

STRICT REQUIREMENTS:
1) "week" must be a SINGLE INTEGER (e.g., 1, 3, 5) not a range.
2) Create between {min_steps} and {max_steps} steps.
3) First step must be week 1 and final step must be week {total_weeks}.
4) Doses must include units where possible.
5) Use simple language for instructions.
6) Include monitoring items relevant to {drug_class}.
7) Adjust reduction speed for frailty (CFS {cfs_score}).
8) Provide practical pause criteria.
9) Return ONLY JSON.

Example of correct minimal output:
{{"taper_steps": [{{"week":1, "dose":"20mg", "percentage_of_original":100, "instructions":"...","monitoring":"...","withdrawal_symptoms_to_watch":["symptom1"]}}, {{"week":4, "dose":"STOP", "percentage_of_original":0, "instructions":"...","monitoring":"...","withdrawal_symptoms_to_watch":["symptom1"]}}], "patient_education": ["..."], "pause_criteria": ["..."], "success_indicators": ["..."]}}

Return only JSON. If uncertain, prefer conservative (slower) taper.
"""
        return prompt

    # -----------------------------
    # Fallback deterministic schedule
    # -----------------------------

    def _generate_fallback_schedule(self, total_weeks: int, current_dose: str, patient_age: int, cfs_score: int, withdrawal_symptoms: Optional[str]) -> Dict[str, Any]:
        """Deterministic fallback schedule used when AI output is unavailable or invalid."""
        frailty_multiplier = 1 + max(0, (cfs_score - 4) * 0.1)
        base_steps = max(4, total_weeks // 2)
        num_steps = math.ceil(base_steps * frailty_multiplier)
        num_steps = max(2, num_steps)
        reduction_per_step = 100 / num_steps

        steps: List[Dict[str, Any]] = []
        for i in range(num_steps):
            percentage = round(max(0, 100 - reduction_per_step * i), 1)
            week = 1 + int(i * (total_weeks / num_steps))
            steps.append({
                "week": week,
                "dose": f"{percentage}% of {current_dose}",
                "percentage_of_original": percentage,
                "instructions": f"Reduce dose to {percentage}% of the original. Take exactly as directed.",
                "monitoring": "Watch for withdrawal symptoms and return of original condition",
                "withdrawal_symptoms_to_watch": _normalize_symptoms_field(withdrawal_symptoms),
            })

        if steps and steps[-1]["percentage_of_original"] > 0:
            steps.append({
                "week": total_weeks,
                "dose": "0 (discontinue)",
                "percentage_of_original": 0,
                "instructions": "Stop the medication entirely. Contact clinician if issues arise.",
                "monitoring": "Monitor for withdrawal and symptom recurrence.",
                "withdrawal_symptoms_to_watch": ["severe withdrawal", "worsening condition"],
            })

        return {
            "taper_steps": steps,
            "patient_education": [
                "Follow the schedule exactly.",
                "If you feel severe symptoms, pause and contact your clinician.",
            ],
            "pause_criteria": ["Severe withdrawal symptoms", "Marked functional decline"],
            "success_indicators": ["Minimal withdrawal symptoms", "Stable functional status"],
        }

    # -----------------------------
    # Monitoring plan generator
    # -----------------------------

    def generate_monitoring_plan(
        self,
        medication_name: str,
        risk_category: str,
        risk_factors: List[str],
        patient_age: int,
        comorbidities: List[str],
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        prompt = self._build_monitoring_prompt(medication_name, risk_category, risk_factors, patient_age, comorbidities)

        try:
            raw = self._call_model_with_json_mime(prompt, max_retries=max_retries)
            parsed = self._parse_model_response_to_json(raw)
            if not isinstance(parsed, dict):
                raise ValueError("Monitoring plan not returned as JSON object")
            return parsed
        except Exception as e:
            logger.exception("Monitoring plan generation failed: %s", e)
            return {
                "monitoring_schedule": {"Week 1-4": ["symptom check", "blood pressure if indicated"], "Monthly": ["clinical review"]},
                "alert_criteria": ["Worsening symptoms", "New concerning signs"],
                "patient_diary_items": ["Daily symptom log", "Medication adherence"],
            }

    def _build_monitoring_prompt(self, medication_name: str, risk_category: str, risk_factors: List[str], patient_age: int, comorbidities: List[str]) -> str:
        comorb_str = ", ".join(comorbidities) if comorbidities else "None"
        risk_factors_str = ", ".join(risk_factors) if risk_factors else "None"
        prompt = f"""
You are a clinical pharmacist. Return ONLY JSON for a practical monitoring plan.

Medication: {medication_name}
Risk category: {risk_category}
Risk factors: {risk_factors_str}
Patient age: {patient_age}
Comorbidities: {comorb_str}

Return JSON like:
{{
  "monitoring_schedule": {{
    "Week 1-2": ["parameter1", "parameter2"],
    "Week 3-4": ["parameter1", "parameter2"],
    "Monthly": ["parameter1"]
  }},
  "alert_criteria": ["string"],
  "patient_diary_items": ["string"]
}}

Return only JSON.
"""
        return prompt

    # -----------------------------
    # Clinical recommendation generator
    # -----------------------------

    def generate_clinical_recommendations(
        self,
        patient_summary: Dict[str, Any],
        red_medications: List[str],
        yellow_medications: List[str],
        interactions: List[Dict[str, Any]],
        max_retries: Optional[int] = None,
    ) -> List[str]:
        prompt = self._build_recommendations_prompt(patient_summary, red_medications, yellow_medications, interactions)
        try:
            raw = self._call_model_with_json_mime(prompt, max_retries=max_retries)
            parsed = self._parse_model_response_to_json(raw)
            # Accept either a list of strings or an object with "recommendations"
            if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                return parsed
            if isinstance(parsed, dict):
                for key in ("recommendations", "clinical_recommendations", "results"):
                    if key in parsed and isinstance(parsed[key], list):
                        return [str(x) for x in parsed[key]]
            raise ValueError("Unexpected response shape for clinical recommendations")
        except Exception as e:
            logger.exception("Clinical recommendation generation failed: %s", e)
            return [
                "Reassess high-risk medications and consider deprescribing.",
                "Evaluate benzodiazepine use especially in frail older adults.",
                "Monitor for herb-drug interactions and adjust therapy as needed.",
                "Review goals of care with patient and family.",
                "Monitor cognition, fall risk and sedation weekly.",
            ]

    def _build_recommendations_prompt(self, patient_summary: Dict[str, Any], red_medications: List[str], yellow_medications: List[str], interactions: List[Dict[str, Any]]) -> str:
        interactions_count = len(interactions) if interactions else 0
        comorb_str = ", ".join(patient_summary.get("comorbidities", [])) if patient_summary.get("comorbidities") else "None"
        prompt = f"""
You are a clinical pharmacist. Return ONLY a JSON array of 5-7 prioritized clinical recommendations (strings).

Patient summary:
- Age: {patient_summary.get('age')}
- Frailty: {patient_summary.get('frailty_status')}
- CFS: {patient_summary.get('cfs_score')}
- Life expectancy: {patient_summary.get('life_expectancy')}
- Comorbidities: {comorb_str}

RED medications: {', '.join(red_medications) if red_medications else 'None'}
YELLOW medications: {', '.join(yellow_medications) if yellow_medications else 'None'}
Herb-drug interactions: {interactions_count}

Return only a JSON array of short actionable recommendations.
"""
        return prompt

    # -----------------------------
    # Intelligent fallback for drug info (pattern matching)
    # -----------------------------

    def _get_fallback_drug_info_with_intelligence(self, drug_name: str) -> Dict[str, Any]:
        drug_lower = drug_name.lower()
        for patterns, info in COMMON_DRUG_PATTERNS.items():
            if any(p in drug_lower for p in patterns):
                # Copy and ensure types
                out = dict(info)
                out["taper_strategy_name"] = out.get("taper_strategy_name", "Evidence-based protocol")
                out["monitoring_frequency"] = out.get("monitoring_frequency", "Weekly")
                out["pause_criteria"] = out.get("pause_criteria", "Severe symptoms") if isinstance(out.get("pause_criteria"), str) else out.get("pause_criteria", [])
                out["requires_taper"] = bool(out.get("requires_taper", True))
                out["typical_duration_weeks"] = _safe_int(out.get("typical_duration_weeks", 4))
                return out

        # Generic default
        return {
            "drug_class": "Unknown",
            "risk_profile": "Standard",
            "taper_strategy_name": "Gradual Reduction",
            "step_logic": "Reduce by 25% every 2 weeks with monitoring",
            "withdrawal_symptoms": "Return of symptoms, general discomfort",
            "monitoring_frequency": "Weekly",
            "pause_criteria": "Severe symptoms or patient distress",
            "requires_taper": True,
            "typical_duration_weeks": 4,
            "special_considerations": "Consult healthcare provider",
        }


# -----------------------------
# Quick self-test / CLI runner
# -----------------------------
"""
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Quick test runner for GeminiTaperService")
    parser.add_argument("--api_key", type=str, default=None, help="Gemini API key (overrides env)")
    parser.add_argument("--test_drug", type=str, default="theophylline", help="Drug name to test")
    parser.add_argument("--age", type=int, default=78)
    parser.add_argument("--cfs", type=int, default=4)
    parser.add_argument("--dose", type=str, default="200mg")
    args = parser.parse_args()

    try:
        svc = GeminiTaperService(api_key=args.api_key)

        print("=== TEST: get_drug_information_with_context ===")
        info = svc.get_drug_information_with_context(
            drug_name=args.test_drug,
            clinical_context="Patient flagged for STOPP/Beers criteria",
            patient_age=args.age,
            comorbidities=["COPD", "Hypertension"],
        )
        print(json.dumps(info, indent=2))

        print("\n=== TEST: generate_detailed_taper_schedule ===")
        schedule = svc.generate_detailed_taper_schedule(
            drug_name=args.test_drug,
            drug_class=info.get("drug_class", "Unknown"),
            current_dose=args.dose,
            duration_on_med="long_term",
            taper_strategy=info.get("taper_strategy_name", "Gradual Reduction"),
            step_logic=info.get("step_logic", "Reduce by 25% every 2 weeks"),
            total_weeks=_safe_int(info.get("typical_duration_weeks", 8)),
            patient_age=args.age,
            cfs_score=args.cfs,
            comorbidities=["COPD"],
            withdrawal_symptoms=info.get("withdrawal_symptoms", "")
        )

        print(json.dumps(schedule, indent=2))

        print("\n=== TEST: generate_monitoring_plan ===")
        mon = svc.generate_monitoring_plan(
            medication_name=args.test_drug,
            risk_category=info.get("risk_profile", "Standard"),
            risk_factors=["age>75"],
            patient_age=args.age,
            comorbidities=["COPD"],
        )
        print(json.dumps(mon, indent=2))

        print("\n=== TEST: generate_clinical_recommendations ===")
        recs = svc.generate_clinical_recommendations(
            patient_summary={
                "age": args.age,
                "frailty_status": "Moderate",
                "cfs_score": args.cfs,
                "life_expectancy": ">1 year",
                "comorbidities": ["COPD", "Hypertension"],
            },
            red_medications=["theophylline"],
            yellow_medications=[],
            interactions=[],
        )
        print(json.dumps(recs, indent=2))

    except Exception as e:
        logger.exception("Self-test failed: %s", e)

"""