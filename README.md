# Bird Species Detection and Information System

An end-to-end web application developed with Flask for detecting and classifying bird species from images. The system integrates deep learning models with external APIs to provide comprehensive biological information, additional imagery, and vocalization recordings, functioning as both a detection tool and a digital encyclopedia.

## Core Features

*   Object Detection: Implements a custom-trained YOLO model to accurately locate birds within uploaded images.
*   Species Classification: Utilizes a fine-tuned EfficientNet model to perform high-precision classification of detected individuals.
*   Automated Descriptions: Leverages the Google Gemini API to generate detailed biological descriptions and facts for identified species.
*   Visual Augmentation: Integrates Google Custom Search API to retrieve and display supplementary images of the identified birds.
*   Audio Integration: Connects with the Xeno-Canto API to provide searchable high-quality audio recordings of bird calls and songs.
*   Reference Library: Includes a searchable database of bird species populated from a JSON backend, allowing users to browse ecological information independently of the detection tool.
*   Web Interface: A responsive dashboard for seamless image uploads and library navigation.

## Technical Stack

*   Backend: Python, Flask
*   Machine Learning: PyTorch, Ultralytics YOLO, EfficientNet
*   Computer Vision: OpenCV
*   APIs: Google Gemini API, Google Custom Search API, Xeno-Canto API
*   Dependency Management: pip (venv or Conda recommended)
*   Frontend: HTML, CSS, JavaScript, Jinja2

## Prerequisites

*   Python 3.7+ (Version 3.11+ recommended)
*   Git (for repository cloning)
*   Conda or pip (for environment management)
*   Active Internet connection (for API requests and dependency installation)
*   Google Cloud Platform (GCP) Account: For Google API Key and Custom Search Engine setup.
*   Pre-trained Models: 
    *   Detection model: `backend/best.pt`
    *   Classification model: `backend/efficientnet_b3_bird_classifier.pth`
*   Data File: `backend/static/birds_data.json`

## Installation and Setup

1.  Clone the Repository:
    ```bash
    git clone https://github.com/hfuwcs/birds_classfier_information.git
    cd birds_classfier_information
    ```

2.  Environment Configuration:
    Using venv:
    ```bash
    python -m venv .venv
    # Windows (PowerShell):
    # .\.venv\Scripts\Activate.ps1
    # macOS/Linux:
    # source ./.venv/bin/activate
    ```
    Using Conda:
    ```bash
    conda create -n bird_env python=3.11
    conda activate bird_env
    ```

3.  Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Model and Data Deployment:
    Place the following files in their respective directories:
    *   `best.pt` and `efficientnet_b3_bird_classifier.pth` -> `backend/`
    *   `birds_data.json` -> `backend/static/`

5.  API Configuration:
    *   Obtain a Google API Key via the Google Cloud Console and enable the Custom Search API.
    *   Create a Custom Search Engine at the Google Programmable Search Engine portal to obtain a Search Engine ID (CX).
    *   Obtain a Gemini API Key via Google AI Studio.

6.  Environment Variables:
    Create a `.env` file in the `backend/` directory with the following keys:
    ```dotenv
    GOOGLE_CSE_ID=YOUR_CUSTOM_SEARCH_ENGINE_ID
    GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    ```

7.  Execution:
    Navigate to the backend directory and launch the Flask server:
    ```bash
    cd backend/
    python app.py
    ```
    The application will be accessible at `http://127.0.0.1:5000/`.

## Application Usage

*   Home Page: General overview of the BirdGuide system.
*   Explore Library: Browse the species database with search functionality.
*   Detection Tool: Upload an image to trigger the detection and classification pipeline. Results include species identification, AI-generated descriptions, and audio samples.
*   News and About: Static informational pages regarding project updates and documentation.

## Project Structure
