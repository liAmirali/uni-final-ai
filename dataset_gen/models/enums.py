"""
Enum definitions for dataset generation.
"""
from enum import Enum


class SUBJECTS(Enum):
    """Interview subject categories for elderly spiritual health assessment."""
    
    LOSS_OF_INDEPENDENCE = "loss_of_independence"
    LOSS_OF_SOCIAL_ACTIVITY = "loss_of_social_activity"
    PHYSICAL_HEALTH_AND_SEXUAL_ISSUES = "physical_health_and_sexual_issues"
    LOSS_OF_CLOSE_ONES_AND_FEAR_OF_DEATH = "loss_of_close_ones_and_fear_of_death"
    LOSS_OF_FAMILY_CONNECTIONS = "loss_of_family_connections"
    LIFESTYLE_CHANGES = "lifestyle_changes"
    LOSS_OF_INCOME = "loss_of_income"
    LOSS_OF_ASPIRATION = "loss_of_aspiration"
    LIFE_INTEGRITY = "life_integrity"

