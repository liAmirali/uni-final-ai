"""
Dataset Generation Package for Iranian Elderly Interview Study.

This package provides tools for generating synthetic interview data
from Iranian elderly personas for spiritual health research.
"""

__version__ = "2.0.0"
__author__ = "Amirali Lotfi"

# Make key classes available at package level
from .models import PersonaDetails, SUBJECTS
from .generators import PersonaGenerator, InterviewGenerator, generate_base_persona
from .utils import LLMClient, create_openai_client, BatchProcessor
from .questions import INTERVIEW_QUESTIONS

__all__ = [
    "PersonaDetails",
    "SUBJECTS",
    "PersonaGenerator",
    "InterviewGenerator",
    "generate_base_persona",
    "LLMClient",
    "create_openai_client",
    "BatchProcessor",
    "INTERVIEW_QUESTIONS",
]

