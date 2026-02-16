import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class Scraper:
    def __init__(self, output_dir="data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,4000")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_site(self, site_id, url):
        print(f"Scraping {url}...")
        self.driver.get(url)
        time.sleep(4) # Wait for heavy JavaScript and banners to load

        screenshot_path = self.output_dir / f"{site_id}.png"
        # 1. Capture a full-page screenshot of the body element to ensure coordinates match the CSS data
        body_element = self.driver.find_element(By.TAG_NAME, "body")
        body_element.screenshot(str(screenshot_path))
        
        # 2. Extract DOM and CSS properties relative to the body
        text_elements = body_element.find_elements(By.XPATH, ".//*[text() and not(self::script) and not(self::style)]")

        css_data = []
        for el in text_elements:
            if el.is_displayed():
                text = el.text.strip()
                if not text:
                    continue
                
                loc = el.location
                size = el.size
                
                # Because we screenshotted the body, x and y are exactly 1:1 with the image coordinates
                bbox = [loc['x'], loc['y'], loc['x'] + size['width'], loc['y'] + size['height']]

                css_data.append({
                    "text": text,
                    "bbox": bbox,
                    "color": el.value_of_css_property("color"),
                    "background_color": el.value_of_css_property("background-color"),
                    "font_size": el.value_of_css_property("font-size"),
                    "z_index": el.value_of_css_property("z-index")
                })

        json_path = self.output_dir / f"{site_id}_css.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(css_data, f, indent=4)
            
        print(f"Saved full page snapshot and {len(css_data)} CSS records for {site_id}.")
        return screenshot_path, json_path

    def close(self):
        self.driver.quit()
