# Python_WebScarper
### WebScraper to Generate Multimodal Dataset

**Author:** Prashant Mahto

This repository contains a specialized web scraper built with Selenium and the Gemini 2.5 Flash API. Developed for research, this tool is designed to navigate websites, capture both the DOM structure and visual rendering, and generate normalized JSON datasets. These datasets are specifically formatted to fine-tune Transformer-based Vision-Language Models (such as LayoutLM) for complex UI analysis and element detection.

### Features

* **Headless DOM Parsing:** Uses Selenium to interact with web elements and capture metadata (CSS attributes, visibility, click-path depth) across full-page scrolling viewports.
* **Visual Spatial Recognition:** Integrates the cloud-based Gemini 2.5 Flash API to perform in-the-wild document parsing, capturing text from heavily styled, overlapping, or obfuscated UI elements without relying on local GPU OCR constraints.
* **LayoutLM Normalization:** Automatically converts pixel coordinates from raw screenshots into the normalized 0-1000 bounding box scale required by Hugging Face LayoutLM models.

### Prerequisites

* Python 3.9 or higher
* Google Chrome and ChromeDriver
* Python packages: `selenium`, `google-genai`, `pillow`, `python-dotenv`
* GEMINI_API_KEY

### Getting the Gemini API Key

To utilize the cloud vision extraction, you must generate a free API key from Google AI Studio.

1. Navigate to Google AI Studio in your web browser.
2. Sign in with your Google Account.
3. On the left-hand navigation panel or the top-right corner, click on "Get API key".
4. Click the "Create API key" button.
5. Select an existing Google Cloud project or let the studio create a new default project for you.
6. Copy the generated alphanumeric string. Keep this secure and do not share it.

### Environment Setup (.env)

This project uses `python-dotenv` to securely manage credentials. You must create an environment file to store your API key locally so it is never hardcoded into the repository.

1. In the root directory of this project (at the same level as the `src` folder), create a new file named exactly `.env`.
2. Open the `.env` file in your code editor and add the following line, pasting your copied key after the equals sign (do not use quotation marks):
   `GEMINI_API_KEY=your_copied_api_key`
   
[![Anti-Trust-War Machine](https://img.youtube.com/vi/RVGbLSVFtIk/maxresdefault.jpg)](https://www.youtube.com/watch?v=3CM1_Ji6fJ8)  

This video provides a direct, visual walkthrough of navigating Google AI Studio to successfully generate and secure the API key required for your pipeline

### Pipeline Architecture

* **Ingestion:** Selenium opens the target URL, allowing all dynamic JavaScript and pop-ups to fully load.
* **Snapshot Capture:** A high-resolution, full-page screenshot of the body element is taken and saved locally.
* **Visual Extraction:** The screenshot is passed to the Gemini API, which processes the image to extract tokens and raw bounding boxes natively in a [ymin, xmin, ymax, xmax] format.
* **Data Transformation:** The Python orchestrator parses the JSON response, translates the coordinates to the [xmin, ymin, xmax, ymax] 0-1000 scale, and packages it alongside the Selenium CSS data into a master dataset.
