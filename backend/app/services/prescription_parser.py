import google.generativeai as genai
from pathlib import Path
import PyPDF2
import io
from typing import List, Dict
import json


class PrescriptionParser:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def _safe_extract_json(self, raw: str) -> dict:
        """
        Safely extract JSON from messy Gemini responses.

        Handles:
        - ```json ... ```
        - ``` ... ```
        - extra text before/after JSON
        - multiple JSON objects
        - hallucinated comments
        - trailing commas
        """
        import re

        if not raw or not isinstance(raw, str):
            return {}

        text = raw.strip()

        # -----------------------------------------
        # 1. Remove any ```json, ```python, ``` etc.
        # -----------------------------------------
        if "```" in text:
            # Remove ALL code fences
            text = re.sub(r"```(?:json|python|javascript)?", "", text)
            text = text.replace("```", "").strip()

        # -----------------------------------------
        # 2. Extract the FIRST { ... } or [ ... ]
        # -----------------------------------------
        json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if json_match:
            text = json_match.group(1).strip()

        # -----------------------------------------
        # 3. Try direct parse
        # -----------------------------------------
        try:
            return json.loads(text)
        except:
            pass

        # -----------------------------------------
        # 4. Attempt repairs (trailing commas)
        # -----------------------------------------
        repaired = re.sub(r",(\s*[\]}])", r"\1", text)
        try:
            return json.loads(repaired)
        except:
            pass

        # -----------------------------------------
        # 5. Final fallback: detect JSON-like object manually
        # -----------------------------------------
        try:
            # Try to balance braces
            open_braces = text.count("{")
            close_braces = text.count("}")

            if open_braces > close_braces:
                text += "}" * (open_braces - close_braces)

            return json.loads(text)
        except:
            return {}
    
    def extract_from_pdf(self, pdf_bytes: bytes) -> List[Dict]:
        """Extract text from PDF and parse medications"""
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        return self._parse_medication_text(text)
    
    def extract_from_image(self, image_bytes: bytes) -> List[Dict]:
        """Extract medications from prescription image using Gemini Vision"""
        prompt = """
        Analyze this medical prescription or medication image carefully.
        
        Extract ALL medications, supplements, or drugs mentioned.
        
        Return ONLY valid JSON (no markdown formatting, no code blocks):
        {
        "medications": [
            {
            "generic_name": "drug name",
            "brand_name": "brand if mentioned or unknown",
            "dose": "strength with unit",
            "frequency": "how often to take",
            "indication": "what it treats or unknown",
            "duration": "long_term or short_term or unknown",
            "confidence": "high or medium or low"
            }
        ]
        }
        
        IMPORTANT: Return ONLY the JSON object, no explanations, no markdown.
        """
        
        
            
        try:
            import PIL.Image
            image = PIL.Image.open(io.BytesIO(image_bytes))

            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')

            response = self.model.generate_content([prompt, image])
            raw = getattr(response, "text", "") or ""

            print("🤖 Gemini raw output:")
            print(raw)
            print("="*80)

            # Use NEW safe extractor
            parsed = self._safe_extract_json(raw)
            medications = parsed.get("medications", [])

            print(f"✅ Extracted {len(medications)} medications")
            return medications

        except Exception as e:
            print("❌ Error in extract_from_brown_bag:", e)
            return []

    
    def _parse_medication_text(self, text: str) -> List[Dict]:
        """Parse medication details from extracted prescription text using Gemini."""

        prompt = f"""
        Extract EVERY medication mentioned in the following prescription text.

        Text:
        {text}

        Return ONLY valid JSON in this EXACT format:

        {{
        "medications": [
            {{
            "generic_name": "drug name",
            "brand_name": "brand if mentioned or unknown",
            "dose": "strength with unit or unknown",
            "frequency": "how often or unknown",
            "indication": "what it is for or unknown",
            "duration": "short_term or long_term or unknown",
            "confidence": "high or medium or low"
            }}
        ]
        }}

        No commentary, no markdown, no extra text — ONLY JSON.
        """

        try:
            response = self.model.generate_content(prompt)

            raw = getattr(response, "text", None)
            if raw is None:
                raw = str(response)

            print("\n🤖 RAW GEMINI RESPONSE:")
            print(raw)
            print("=" * 80)

            # Use the safe extractor
            parsed = self._safe_extract_json(raw)
            medications = parsed.get("medications", [])

            print(f"✅ Parsed {len(medications)} medications from text")
            return medications

        except Exception as e:
            print("❌ Error in _parse_medication_text:", e)
            return []



    def extract_from_brown_bag(self, image_bytes: bytes) -> List[Dict]:
        """Extract medications from brown bag photo with multiple bottles"""
        prompt = """
        This is a "brown bag review" - a photo of medication bottles, boxes, or blister packs.
        
        Look carefully at EVERY visible medication container and extract:
        - Medication name (generic or brand)
        - Strength/dose if visible
        - Any other readable information
        
        Return ONLY valid JSON (no markdown, no code blocks):
        {
        "medications": [
            {
            "generic_name": "medication name from label",
            "brand_name": "brand if visible",
            "dose": "strength from label or unknown",
            "frequency": "unknown",
            "indication": "unknown",
            "duration": "unknown",
            "confidence": "high or medium or low",
            "notes": "any other visible text"
            }
        ]
        }
        
        IMPORTANT: Return ONLY the JSON object, no markdown code blocks, no explanations.
        """
        
        try:
            import PIL.Image
            image = PIL.Image.open(io.BytesIO(image_bytes))

            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')

            response = self.model.generate_content([prompt, image])
            raw = getattr(response, "text", "") or ""

            print("🤖 Gemini raw output:")
            print(raw)
            print("="*80)

            # Use NEW safe extractor
            parsed = self._safe_extract_json(raw)
            medications = parsed.get("medications", [])

            print(f"✅ Extracted {len(medications)} medications")
            return medications

        except Exception as e:
            print("❌ Error in extract_from_brown_bag:", e)
            return []

def extract_from_brown_bag(self, image_bytes: bytes) -> List[Dict]:
    """Extract medications from brown bag photo with multiple bottles"""
    prompt = """
    This is a "brown bag review" - a photo of medication bottles, boxes, or blister packs.
        
    Look carefully at EVERY visible medication container and extract:
    - Medication name (generic or brand)
    - Strength/dose if visible
    - Any other readable information
        
    Return ONLY valid JSON (no markdown, no code blocks):
    {
    "medications": [
        {
        "generic_name": "medication name from label",
        "brand_name": "brand if visible",
        "dose": "strength from label or unknown",
        "frequency": "unknown",
        "indication": "unknown",
        "duration": "unknown",
        "confidence": "high or medium or low",
        "notes": "any other visible text"
        }
    ]
    }
        
    IMPORTANT: Return ONLY the JSON object, no markdown code blocks, no explanations.
    """
        
    try:
        import PIL.Image
        image = PIL.Image.open(io.BytesIO(image_bytes))

        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')

        response = self.model.generate_content([prompt, image])
        raw = getattr(response, "text", "") or ""

        print("🤖 Gemini raw output:")
        print(raw)
        print("="*80)

            # Use NEW safe extractor
        parsed = self._safe_extract_json(raw)
        medications = parsed.get("medications", [])

        print(f"✅ Extracted {len(medications)} medications")
        return medications

    except Exception as e:
        print("❌ Error in extract_from_brown_bag:", e)
        return []