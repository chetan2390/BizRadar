# config.py
# This file stores all settings for BizRadar in one place.
# Every other file imports from here.

# config.py
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# API key now comes from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Fallback business profile
BUSINESS_PROFILE = {
    "name": "Sharma Textiles",
    "industry": "Textiles and Manufacturing",
    "business_type": "MSME",
    "location": "Gujarat, India",
    "sectors": ["Manufacturing", "Export", "GST Registered"],
    "interests": ["GST updates", "export regulations", "MSME schemes", "textile industry news"]
}