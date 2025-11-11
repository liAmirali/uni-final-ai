"""
Persona data model.
"""
import json
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class PersonaDetails:
    """
    Data class representing an elderly Iranian persona with demographic,
    biological, psychological, social, economic, cultural, and contextual attributes.
    """
    
    # Demographic Information
    age: int
    gender: str
    marital_status: str
    children: str
    living_situation: str
    
    # Biological Component
    general_health: str
    chronic_disease: Optional[str]
    mobility: str
    hearing_senses: str
    vision_senses: str
    daily_energy: str
    
    # Psychological Component
    personality_type: str
    cognitive_status: str
    dominant_emotion: str
    emotional_intelligence: str
    iq: str
    attitude_toward_aging: str
    
    # Social Component
    main_social_role: str
    social_support: str
    social_participation: str
    
    # Economic Component
    income: str
    economic_decile: int
    housing: str
    
    # Cultural-Value Component
    religion_and_sect: str
    internalized_moral_traits: List[str]
    religiosity_level: str
    ethnicity: str
    language: str
    
    # Contextual Component
    important_personal_experiences: str
    life_satisfaction: str
    meaning_and_purpose_in_old_age: str
    
    def to_dict(self) -> dict:
        """Convert persona to dictionary."""
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert persona to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: dict) -> "PersonaDetails":
        """Create PersonaDetails instance from dictionary."""
        return cls(**data)

