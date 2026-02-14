import json
from pathlib import Path

class Normalizer:
    def __init__(self, output_file="data/processed/dataset.jsonl"):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def append_to_dataset(self, site_id, vision_data, image_path):
        """
        Transforms PaddleOCR vision data into Hugging Face LayoutLM format.
        Initializes all labels (ner_tags) to 0 (Outside/Clean) for later human-labeling.
        """
        words = vision_data.get("words", [])
        bboxes = vision_data.get("bboxes", [])
        
        if len(words) != len(bboxes):
            print(f"Warning: Mismatch in words and boxes for {site_id}. Skipping.")
            return

        # Initialize all tags to 0 (No dark pattern detected yet)
        ner_tags = [0] * len(words)

        huggingface_record = {
            "id": site_id,
            "words": words,
            "bboxes": bboxes,
            "ner_tags": ner_tags,
            "image_path": str(image_path)
        }

        # Append as a JSON Line (JSONL)
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(huggingface_record) + "\n")
            
        print(f"Normalized data for {site_id} appended to {self.output_file.name}")

