import re
import warnings
import torch
import time 
from PIL import Image
from transformers import AutoProcessor, AutoModelForImageTextToText

# Suppress the noisy RoPE deprecation warnings from Hugging Face
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.modeling_rope_utils")

class VisionExtractor:
    """
    A Vision-Language wrapper for PaddleOCR-VL-1.5 to extract text and 
    spatial coordinates from UI screenshots for LayoutLM formatting.
    """
    
    def __init__(self, model_id="PaddlePaddle/PaddleOCR-VL-1.5", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Initializing {model_id} on {self.device.upper()}...")
        
        # Load the model completely natively (Using 'dtype' instead of 'torch_dtype')
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_id, 
            dtype=torch.float16 if self.device == "cuda" else torch.float32,
            trust_remote_code=False # Relying 100% on native Hugging Face code
        ).to(self.device).eval()
        
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=False)
        self.box_pattern = re.compile(r'(.*?)(?:<box>|\[)([\d,\s]+)(?:</box>|\])')

    def _normalize_bbox(self, bbox_str, width, height):
        """Converts raw OCR string coordinates into a 0-1000 normalized list."""
        try:
            x1, y1, x2, y2 = [int(coord.strip()) for coord in bbox_str.split(",")]
            return [
                max(0, min(1000, int(1000 * (x1 / width)))),
                max(0, min(1000, int(1000 * (y1 / height)))),
                max(0, min(1000, int(1000 * (x2 / width)))),
                max(0, min(1000, int(1000 * (y2 / height))))
            ]
        except ValueError:
            return None 

    def extract_layout_data(self, image_path):
        
        image = Image.open(image_path).convert("RGB")
        orig_w, orig_h = image.size
        max_pixels = 1280 * 28 * 28 
        
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": "OCR:"}]}]
        
        print("Preprocessing image and tokenizing...")
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True, return_dict=True, 
            return_tensors="pt", images_kwargs={"size": {"shortest_edge": self.processor.image_processor.min_pixels, "longest_edge": max_pixels}}
        ).to(self.device)

        with torch.no_grad():
            print(f"Starting GPU generation for {orig_w}x{orig_h} image...")
            start_time = time.time()
            outputs = self.model.generate(**inputs, max_new_tokens=2048)
            end_time = time.time()
            print(f"GPU generation complete in {end_time - start_time:.2f} seconds.")
            
        raw_output = self.processor.decode(outputs[0][inputs["input_ids"].shape[-1]:-1])
        return self._parse_vlm_output(raw_output, orig_w, orig_h)

    def _parse_vlm_output(self, raw_text, img_w, img_h):
        dataset = {"words": [], "bboxes": []}
        for line in raw_text.split("\n"):
            match = self.box_pattern.search(line)
            if match:
                text_content = match.group(1).strip()
                bbox_content = match.group(2).strip()
                normalized_box = self._normalize_bbox(bbox_content, img_w, img_h)
                
                if text_content and normalized_box:
                    dataset["words"].append(text_content)
                    dataset["bboxes"].append(normalized_box)
        return dataset

