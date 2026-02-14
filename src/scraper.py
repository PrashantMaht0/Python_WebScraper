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
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        # Add a user-agent to prevent bot-blockers from hiding the cookie banner
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        self.driver = webdriver.Chrome(options=chrome_options)

        # Common GDPR / Cookie Banner / Modal selectors used across the web
        self.banner_selectors = [
            "#onetrust-consent-sdk",      # OneTrust (Amazon, DailyMail, etc.)
            "#usercentrics-root",         # Usercentrics
            "#CybotCookiebotDialog",      # Cookiebot
            "[id*='cookie-banner']", 
            "[class*='cookie-banner']",
            "[id*='cookie']",
            "[class*='cookie']",
            "div[role='dialog']"          # Generic popups and forced-action modals
        ]

    def _find_overlay_element(self):
        """Attempts to find a cookie banner or modal overlay in the DOM."""
        for selector in self.banner_selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                # Ensure the element is visible and actually has substance
                if el.is_displayed() and el.size['width'] > 50 and el.size['height'] > 30:
                    return el
        return None

    def scrape_site(self, site_id, url):
        print(f"Scraping {url}...")
        self.driver.get(url)
        time.sleep(4) # Wait for heavy JavaScript and banner animations to load

        # 1. Target the Specific Component
        target_container = self._find_overlay_element()
        screenshot_path = self.output_dir / f"{site_id}.png"
        
        if target_container:
            print("Found target overlay! Capturing element-level screenshot...")
            # Take a screenshot of JUST the popup
            target_container.screenshot(str(screenshot_path))
            
            # Scope our CSS extraction to ONLY inside the popup
            text_elements = target_container.find_elements(By.XPATH, ".//*[text() and not(self::script) and not(self::style)]")
        else:
            print("No popup detected. Defaulting to viewport screenshot...")
            self.driver.save_screenshot(str(screenshot_path))
            text_elements = self.driver.find_elements(By.XPATH, "//*[text() and not(self::script) and not(self::style)]")

        # 2. Extract DOM and CSS properties
        css_data = []
        for el in text_elements:
            if el.is_displayed():
                text = el.text.strip()
                if not text:
                    continue
                
                loc = el.location
                size = el.size
                
                # RECALCULATE COORDINATES: 
                # If we cropped the image, the LayoutLM coordinates must be shifted 
                # to be relative to the top-left corner of the popup, not the whole page.
                if target_container:
                    container_loc = target_container.location
                    x0 = max(0, loc['x'] - container_loc['x'])
                    y0 = max(0, loc['y'] - container_loc['y'])
                else:
                    x0, y0 = loc['x'], loc['y']
                
                bbox = [x0, y0, x0 + size['width'], y0 + size['height']]

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
            
        print(f"Saved snapshot and {len(css_data)} CSS records for {site_id}.")
        return screenshot_path, json_path

    def close(self):
        self.driver.quit()

