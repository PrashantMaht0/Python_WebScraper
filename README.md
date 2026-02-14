## Python_WebScarper
### WebScraper to Generate Multimodal Dataset

This repository contains a specialized web scraper built with Selenium and PaddleOCR-VL-1.5. It is designed to navigate websites, capture both the DOM structure and visual rendering, and generate normalized JSONL datasets. These datasets are specifically formatted to fine-tune Transformer-based Vision-Language Models (like LayoutLM).

### Features: 

- Headless DOM Parsing: Uses Selenium to interact with web elements and capture metadata (CSS attributes, visibility, click-path depth).

- Visual Spatial Recognition: Integrates PaddleOCR-VL-1.5 to perform in-the-wild document parsing, capturing text from heavily styled, overlapping, or obfuscated UI elements.

- LayoutLM Normalization: Automatically converts pixel coordinates from raw screenshots into the normalized 0-1000 bounding box scale required by Hugging Face LayoutLM models.

- Regulatory Focus: Built to support pre-labeling for specific GDPR violations such as 'Confirmshaming', 'Interface Interference', and 'Forced Action'.

### Prerequisites
- Python 3.9 or higher
- Google Chrome and ChromeDriver
- CUDA toolkit (Highly recommended for running PaddleOCR efficiently)

### Pipeline Architecture
- Ingestion: Selenium opens the target URL, allowing all dynamic JavaScript and pop-ups to fully load.
- Snapshot Capture: A high-resolution screenshot is taken and saved locally.
- Visual Extraction: PaddleOCR processes the image to extract tokens and raw bounding boxes $(xmin, ymin, xmax, ymax)$.
- Data Transformation: The spatial coordinates are normalized to a 0-1000 scale and merged with the Selenium CSS data.