"""
Constants for dataset generation.

This module provides a single source of truth for persona field definitions
and other constants used across the codebase.
"""

# Base persona fields that are generated statistically and must be preserved
# These fields should NOT be modified by the LLM when completing personas
BASE_PERSONA_FIELDS = {
    "age",
    "gender",
    "marital_status",
    "children",
    "living_situation",
    "ethnicity",
    "language",
    "religion_and_sect",
}

