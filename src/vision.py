import os
import json
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv() 
#loading API key from .env file

class VisionExtractor:
    """
    A Cloud-based Vision-Language wrapper using the Gemini API to extract 
    text and spatial coordinates from UI screenshots for LayoutLM formatting.
    """
    
    def __init__(self, api_key=None):
        # Automatically grabs from your .env or environment variables if not passed
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Please set your GEMINI_API_KEY in the .env file.")
            
        self.client = genai.Client(api_key=self.api_key)
        
        self.model_id = "gemini-2.5-flash"

    def extract_layout_data(self, image_path):
        """Processes an image via Gemini and returns LayoutLM formatted data."""
        image = Image.open(image_path).convert("RGB")
        
        prompt = """
        Analyze this UI screenshot. Extract every distinct piece of text.
        Return a JSON array of objects. Each object must have:
        1. "text": The exact string of text.
        2. "box_2d": The bounding box in [ymin, xmin, ymax, xmax] format, normalized to a 0-1000 scale.
        
        Return ONLY the raw JSON array. Do not include markdown formatting like ```json.
        """
        #add you custom prompt here to get the desired output from Gemini. 
        # This prompt is designed to instruct Gemini to return the text and bounding box information in a specific format that can be easily parsed later on.
        
        print("Sending image to Gemini API...")
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                temperature=0.0, # Deterministic output for consistent bounding boxes
            )
        )
        
        return self._parse_gemini_output(response.text)

    def _parse_gemini_output(self, raw_text):
        """Parses the JSON and maps it to LayoutLM dictionaries."""
        dataset = {"words": [], "bboxes": []}
        
        try:
            clean_json = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            elements = json.loads(clean_json)
            
            for el in elements:
                text_content = el.get("text")
                bbox = el.get("box_2d")
                
                if text_content and bbox and len(bbox) == 4:
                    # Gemini outputs [ymin, xmin, ymax, xmax].
                    # LayoutLM expects [xmin, ymin, xmax, ymax].
                    ymin, xmin, ymax, xmax = bbox
                    normalized_box = [xmin, ymin, xmax, ymax]
                    
                    dataset["words"].append(text_content)
                    dataset["bboxes"].append(normalized_box)
                    
            return dataset
            
        except json.JSONDecodeError:
            print("Error: Gemini returned improperly formatted JSON.")
            return dataset
