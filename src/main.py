import os
import json
import time
from pathlib import Path

# Import your newly refactored classes
from src.scraper import Scraper
from src.vision import VisionExtractor

def build_dataset(urls, output_dir="data/processed"):
    """
    Orchestrates the scraping and Gemini vision extraction to build 
    a LayoutLM-ready dataset.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(" Initializing Pipeline Modules...")
    scraper = Scraper(output_dir="data/raw")
    vision_extractor = VisionExtractor()
    
    final_dataset = []

    try:
        for idx, url in enumerate(urls):
            site_id = f"site_{idx:03d}"
            print(f"\n[{idx+1}/{len(urls)}] Processing: {url}")
            
            # Step 1: Scrape and Screenshot
            screenshot_path, css_json_path = scraper.scrape_site(site_id, url)
            
            # Step 2: Gemini OCR & Bounding Box Extraction
            if screenshot_path and screenshot_path.exists():
                print("   -> Sending image to Gemini API for layout extraction...")
                start_time = time.time()
                layout_data = vision_extractor.extract_layout_data(str(screenshot_path))
                end_time = time.time()
                print(f"   -> Gemini extraction complete in {end_time - start_time:.2f} seconds.")
                
                # Step 3: Package the data for LayoutLM
                record = {
                    "id": site_id,
                    "url": url,
                    "image_path": str(screenshot_path),
                    "css_data_path": str(css_json_path), # Keeping CSS data for future feature engineering
                    "layoutlm_data": layout_data         # Contains "words" and "bboxes" (0-1000 scale)
                }
                final_dataset.append(record)
                
                record_path = output_path / f"{site_id}_layout.json"
                with open(record_path, "w", encoding="utf-8") as f:
                    json.dump(record, f, indent=4)
            else:
                print(f"   -> Error: Screenshot not found for {url}. Skipping vision extraction.")

    except Exception as e:
        print(f"\n Pipeline crashed during execution: {e}")
    
    finally:
        print("\nCleaning up web drivers...")
        scraper.close()
        
        dataset_path = "data/processed_dataset/dataset.json"
        with open(dataset_path, "w", encoding="utf-8") as f:
            json.dump(final_dataset, f, indent=4)
        
        print(f" Pipeline complete! {len(final_dataset)} records saved to {dataset_path}")

if __name__ == "__main__":
    # For testing, you can replace this list with a few known URLs that have distinct layouts and dark patterns. The pipeline will process these and save the outputs in the specified directories.
    test_urls = [
        "https://www.amazon.ie/",
        "https://www.dailymail.co.uk/home/index.html", 
    ]
    
    build_dataset(test_urls)