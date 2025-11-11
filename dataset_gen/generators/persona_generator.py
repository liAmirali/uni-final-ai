"""
Persona generation logic with statistical distributions.
"""

import random
from typing import List, Dict, Optional

from prompts import PERSONA_GENERATION_PROMPT, create_constrained_persona_prompt
from utils import LLMClient, BatchProcessor
from config import DEFAULT_MODEL, SEED

# Set seed for reproducibility
random.seed(SEED)


def generate_base_persona() -> (
    Dict[str, any] # pyright: ignore[reportGeneralTypeIssues]
):  
    """
    Generate a base persona with statistically-based demographic fields.
    Returns a dictionary with predefined fields based on Iranian elderly population statistics.
    The LLM will fill in the remaining fields.

    Returns:
        Dictionary with demographic fields
    """
    # Gender distribution (F: 53%, M: 47%)
    gender = random.choices(["Female", "Male"], weights=[53, 47])[0]

    # Age distribution (decaying distribution for elderly)
    age = random.choices(range(65, 95), weights=[25, 20, 15, 15, 10, 10, 5, 3, 2, 1])[0]

    # Marital status distribution
    marital_status = random.choices(
        ["Married", "Single", "Divorced", "Widowed"], weights=[60, 30, 5, 5]
    )[0]

    # Children distribution
    children = random.choices(["None", "1", "2-3", "4+"], weights=[5, 15, 30, 50])[0]

    # Living situation distribution
    living_situation = random.choices(
        ["Living with Family", "Living Alone", "Shared Housing"], weights=[50, 30, 20]
    )[0]

    # Ethnicity distribution (approximate Iranian demographics)
    ethnicity = random.choices(
        [
            "Persian",
            "Azeri",
            "Kurdish",
            "Lur",
            "Baloch",
            "Arab",
            "Turkmen",
            "Gilaki",
            "Mazandarani",
            "Qashqai",
        ],
        weights=[50, 25, 10, 5, 3, 2, 1, 2, 1, 1],
    )[0]

    # Language typically matches ethnicity
    language_map = {
        "Persian": "Persian",
        "Azeri": "Azeri",
        "Kurdish": "Kurdish",
        "Lur": "Luri",
        "Baloch": "Balochi",
        "Arab": "Arabic",
        "Turkmen": "Turkmen",
        "Gilaki": "Gilaki",
        "Mazandarani": "Mazandarani",
        "Qashqai": "Qashqai",
    }
    language = language_map.get(ethnicity, "Persian")

    # Religion distribution
    if ethnicity in ["Persian", "Azeri", "Gilaki", "Mazandarani"]:
        religion = random.choices(["Shia Muslim", "Sunni Muslim"], weights=[95, 5])[0]
    elif ethnicity in ["Kurdish", "Baloch", "Turkmen"]:
        religion = random.choices(["Sunni Muslim", "Shia Muslim"], weights=[80, 20])[0]
    elif ethnicity == "Arab":
        religion = random.choices(["Shia Muslim", "Sunni Muslim"], weights=[70, 30])[0]
    else:
        religion = random.choices(
            ["Shia Muslim", "Sunni Muslim", "Zoroastrian", "Christian", "Jewish"],
            weights=[85, 10, 2, 2, 1],
        )[0]

    return {
        "age": age,
        "gender": gender,
        "marital_status": marital_status,
        "children": children,
        "living_situation": living_situation,
        "ethnicity": ethnicity,
        "language": language,
        "religion_and_sect": religion,
    }


class PersonaGenerator:
    """Generator for creating Iranian elderly personas."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize persona generator.

        Args:
            llm_client: LLM client for generation
        """
        self.llm_client = llm_client

    def generate_full_personas(
        self, count: int, model: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate complete personas using LLM for all fields.

        Args:
            count: Number of personas to generate
            model: Model to use (defaults to config)

        Returns:
            List of persona dictionaries
        """
        messages = [
            {"role": "system", "content": PERSONA_GENERATION_PROMPT},
            {
                "role": "user",
                "content": f"Generate {count} personas. Only give the JSON array with no extra text or formatting. Don't wrap the array in markdown formatting.",
            },
        ]

        response = self.llm_client.generate_simple(messages, model=model)
        content = response.choices[0].message.content

        import json

        personas = json.loads(content)
        return personas

    def complete_personas(
        self, base_personas: List[Dict], model: Optional[str] = None
    ) -> List[Dict]:
        """
        Complete personas with predefined demographic fields.

        Args:
            base_personas: List of dictionaries with demographic fields
            model: Model to use (defaults to config)

        Returns:
            List of completed persona dictionaries
        """
        system_prompt = create_constrained_persona_prompt(base_personas)
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Complete all {len(base_personas)} persona(s) by filling in the missing fields. Return ONLY the JSON array with complete personas, no extra text or markdown formatting.",
            },
        ]

        response = self.llm_client.generate_simple(messages, model=model)
        content = response.choices[0].message.content

        import json

        personas = json.loads(content)
        return personas

    def generate_with_stats(
        self, count: int, model: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate personas with predefined statistics.

        Args:
            count: Number of personas to generate
            model: Model to use (defaults to config)

        Returns:
            List of completed persona dictionaries
        """
        base_personas = [generate_base_persona() for _ in range(count)]
        return self.complete_personas(base_personas, model=model)

    def generate_batch_with_stats(
        self,
        batch_processor: BatchProcessor,
        personas_per_batch: int = 10,
        batch_count: int = 1,
        model: Optional[str] = None,
        batch_file_path: str = "batch_input_personas.jsonl",
    ):
        """
        Generate personas using batch API with predefined statistics.

        Args:
            batch_processor: Batch processor instance
            personas_per_batch: Number of personas per batch request
            batch_count: Number of batch requests
            model: Model to use (defaults to config)
            batch_file_path: Path for batch input file

        Returns:
            Batch object
        """
        messages_list = []

        for _ in range(batch_count):
            # Generate base personas for this batch
            base_personas = [generate_base_persona() for _ in range(personas_per_batch)]

            # Create messages
            system_prompt = create_constrained_persona_prompt(base_personas)
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Complete all {len(base_personas)} persona(s) by filling in the missing fields. Return ONLY the JSON array with complete personas, no extra text or markdown formatting.",
                },
            ]
            messages_list.append(messages)

        return batch_processor.create_batch(
            messages_list,
            model=model or DEFAULT_MODEL,
            batch_file_path=batch_file_path,
            description=f"Batch processing for {batch_count * personas_per_batch} personas with base demographics",
        )
