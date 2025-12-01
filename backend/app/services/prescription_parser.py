import google.generativeai as genai
from pathlib import Path
import PyPDF2
import io
from typing import List, Dict
import json


class PrescriptionParser:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        Analyze this prescription image and extract ALL medications mentioned.
        
        For each medication, provide:
        - generic_name (the active ingredient)
        - brand_name (if mentioned)
        - dose (e.g., "5 mg", "500 mg")
        - frequency (e.g., "OD", "BD", "TDS", "once daily")
        - indication (why it's prescribed, if mentioned)
        - duration (e.g., "short_term", "long_term", or "unknown")
        
        Return ONLY valid JSON in this format:
        {
          "medications": [
            {
              "generic_name": "metformin",
              "brand_name": "Glucophage",
              "dose": "500 mg",
              "frequency": "BD",
              "indication": "diabetes",
              "duration": "long_term",
              "confidence": "high"
            }
          ]
        }
        
        If you cannot read a field, use "unknown" and set confidence to "low".
        """
        
        # Upload image to Gemini
        from PIL import Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Keep your original call site; assume model accepts list with prompt+image
        response = self.model.generate_content([prompt, image])
        
        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            text = getattr(response, "text", None)
            if text is None:
                # fallback: try to stringify the whole response
                text = str(response)
            
            text = text.strip()
            # If there's a ```json ... ``` block, extract the inner content
            if "```json" in text:
                # take content between ```json and the next ```
                try:
                    text = text.split("```json", 1)[1].split("```", 1)[0].strip()
                except Exception:
                    # fallback to everything after the marker
                    text = text.split("```json", 1)[1].strip()
            elif "```" in text:
                # take content between the first pair of triple backticks
                try:
                    text = text.split("```", 1)[1].split("```", 1)[0].strip()
                except Exception:
                    text = text.split("```", 1)[1].strip()
            
            result = json.loads(text)
            return result.get("medications", [])
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return []
    
    def _parse_medication_text(self, text: str) -> List[Dict]:
        """Use Gemini to parse extracted text"""
        prompt = f"""
        Extract ALL medications from this prescription text:
        
        {text}
        
        Return ONLY valid JSON in this exact format:
        {{
          "medications": [
            {{
              "generic_name": "drug name",
              "brand_name": "brand if mentioned",
              "dose": "strength with unit",
              "frequency": "how often",
              "indication": "condition",
              "duration": "short_term or long_term or unknown",
              "confidence": "high or medium or low"
            }}
          ]
        }}
        """
        
        response = self.model.generate_content(prompt)
        
        try:
            text = getattr(response, "text", None)
            if text is None:
                text = str(response)
            text = text.strip()
            if "```json" in text:
                try:
                    text = text.split("```json", 1)[1].split("```", 1)[0].strip()
                except Exception:
                    text = text.split("```json", 1)[1].strip()
            elif "```" in text:
                try:
                    text = text.split("```", 1)[1].split("```", 1)[0].strip()
                except Exception:
                    text = text.split("```", 1)[1].strip()
            result = json.loads(text)
            return result.get("medications", [])
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return []
    def extract_from_brown_bag(self, image_bytes: bytes) -> List[Dict]:
        """Extract medications from brown bag photo with multiple bottles"""
        prompt = """
        This is a "brown bag review" - a photo of multiple medication bottles/boxes.
        
        Identify EACH visible medication container and extract:
        - Position/number (if labeled 1, 2, 3... or just describe location)
        - generic_name
        - brand_name (from label)
        - dose/strength
        - Any visible instructions
        
        Return ONLY valid JSON:
        {
        "medications": [
            {
            "position": "1" or "top-left",
            "generic_name": "...",
            "brand_name": "...",
            "dose": "...",
            "frequency": "unknown",
            "indication": "unknown",
            "duration": "unknown",
            "confidence": "high or medium or low",
            "notes": "any additional visible info"
            }
        ]
        }
        """
        
        import PIL.Image
        image = PIL.Image.open(io.BytesIO(image_bytes))
        response = self.model.generate_content([prompt, image])
        
        try:
            text = response.text
            if "```json" in text:
                text = text.split("``````")[0].strip()
            result = json.loads(text)
            return result.get("medications", [])
        except:
            return []
        

def extract_from_brown_bag(self, image_bytes: bytes) -> List[Dict]:
    """Extract medications from brown bag photo with multiple bottles"""
    prompt = """
    This is a "brown bag review" - a photo of multiple medication bottles/boxes.
    
    Identify EACH visible medication container and extract:
    - Position/number (if labeled 1, 2, 3... or just describe location)
    - generic_name
    - brand_name (from label)
    - dose/strength
    - Any visible instructions
    
    Return ONLY valid JSON:
    {
      "medications": [
        {
          "position": "1" or "top-left",
          "generic_name": "...",
          "brand_name": "...",
          "dose": "...",
          "frequency": "unknown",
          "indication": "unknown",
          "duration": "unknown",
          "confidence": "high or medium or low",
          "notes": "any additional visible info"
        }
      ]
    }
    """
    
    import PIL.Image
    image = PIL.Image.open(io.BytesIO(image_bytes))
    response = self.model.generate_content([prompt, image])
    
    try:
        text = response.text
        if "```json" in text:
            text = text.split("``````")[0].strip()
        result = json.loads(text)
        return result.get("medications", [])
    except:
        return []

