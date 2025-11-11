"""
Configuration settings for dataset generation.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
METIS_API_KEY = os.getenv("METIS_API_KEY")
METIS_BASE_URL = "https://api.metisai.ir/openai/v1"
TAPSAGE_BASE_URL = "https://api.tapsage.com/openai/v1"

# Model Configuration
DEFAULT_MODEL = "gpt-5-mini"
AVAILABLE_MODELS = [
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4o",
    "grok-3",
    "gemini-2.5-pro-preview-06-05",
]

# Generation Parameters
TEMPERATURE = 1.0
TOP_P = 0.9
PRESENCE_PENALTY = 0.3
FREQUENCY_PENALTY = 0.4

# Randomness
SEED = 42

# Version
VERSION = "v2.0"

# Data validation
if not METIS_API_KEY:
    raise ValueError("METIS_API_KEY environment variable is not set. Please set it in your .env file.")

