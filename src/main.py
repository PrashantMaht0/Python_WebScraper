import os
from src.scraper import Scraper
from src.vision import VisionExtractor
from src.normalizer import Normalizer

def run_pipeline(urls_to_scrape):
    print("Initializing Pipeline Modules...")
    scraper = Scraper(output_dir="data/raw")
    vision_extractor = VisionExtractor()
    normalizer = Normalizer(output_file="data/processed/dark_pattern_dataset.jsonl")

    success_count = 0

    try:
        for idx, url in enumerate(urls_to_scrape):
            site_id = f"site_{idx:04d}"
            print(f"\n--- Processing [{site_id}]: {url} ---")
            
            try:
                # 1. Selenium Phase: Navigate, extract CSS, and take a screenshot
                screenshot_path, _ = scraper.scrape_site(site_id, url)
                
                # 2. Vision Phase: Pass the screenshot to PaddleOCR-VL-1.5
                print(f"Running Vision Extractor on {screenshot_path.name}...")
                vision_data = vision_extractor.extract_layout_data(str(screenshot_path))
                
                # 3. Normalization Phase: Convert to 0-1000 scale and save to JSONL
                if vision_data and len(vision_data["words"]) > 0:
                    normalizer.append_to_dataset(site_id, vision_data, screenshot_path)
                    success_count += 1
                else:
                    print(f"Warning: No text detected by Vision model for {site_id}.")
                    
            except Exception as e:
                print(f"Failed to process {url}. Error: {e}")
                continue 

    finally:
        scraper.close()
        print(f"\nPipeline Complete. Successfully processed {success_count}/{len(urls_to_scrape)} sites.")

if __name__ == "__main__":
    test_urls = [
        "https://www.transportforireland.ie/",        
        "https://www.dailymail.co.uk/"         
    ]
    
    run_pipeline(test_urls)