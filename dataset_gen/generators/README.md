# Generators Module

## Business Logic & Purpose

The `generators` module contains the core business logic for creating synthetic Iranian elderly personas and generating interview responses. This module is central to the research goal of understanding spiritual health in elderly Iranian populations through AI-generated interview data.

### Research Context

This project generates synthetic interview datasets for **spiritual health research** focusing on Iranian elderly (ages 65-95). The personas represent diverse cultural, geographical, and social backgrounds within Iran, allowing researchers to study how different demographic factors influence spiritual health responses to various life challenges.

### Key Concepts

**Persona**: A fictional but realistic representation of an Iranian elderly person with:
- **Demographic attributes**: Age, gender, ethnicity, language, religion
- **Biological characteristics**: Health status, mobility, sensory functions
- **Psychological profile**: Personality type, cognitive status, emotional state
- **Social context**: Family role, support systems, social participation
- **Economic situation**: Income sources, housing, economic decile
- **Cultural values**: Religiosity, moral traits, cultural background
- **Life experiences**: Significant personal events, life satisfaction, purpose

**Interview**: A structured conversation where a persona responds to questions about spiritual health challenges, maintaining conversation history and persona consistency.

## Module Structure

### `persona_generator.py`

**Business Logic**: Generates personas using a two-phase approach:

1. **Base Persona Generation** (`generate_base_persona()`):
   - Creates statistically-based demographic fields using Iranian population data
   - Ensures realistic distribution of age, gender, ethnicity, religion, etc.
   - These fields are **immutable** - the LLM cannot modify them

2. **Persona Completion** (`complete_personas()`):
   - Takes base personas with demographic fields
   - Uses LLM to fill remaining fields (health, psychology, social, economic, etc.)
   - Ensures consistency between demographic base and generated attributes

**Key Functions**:
- `generate_base_persona()`: Creates base demographic fields with statistical distributions
- `generate_full_personas()`: LLM generates all fields from scratch
- `generate_with_stats()`: Combines base generation + LLM completion
- `complete_personas()`: Completes base personas with LLM

**Code Flow**:
```
Base Persona (statistics) → LLM Completion → Full Persona
```

### `interview_generator.py`

**Business Logic**: Generates interview responses by role-playing personas:

1. **Response Generation** (`generate_response()`):
   - Takes a persona and question
   - Builds conversation history (maintains context)
   - Formats system prompt with persona details
   - LLM responds as the persona

2. **Full Interview** (`generate_full_interview()`):
   - Processes all questions sequentially
   - Maintains conversation history throughout
   - Generates main question + follow-up responses
   - Ensures persona consistency across all responses

3. **Dataset Generation** (`DatasetGenerator`):
   - Orchestrates interview generation for multiple personas and models
   - Creates CSV files per persona-model combination
   - Tracks progress and handles errors

**Code Flow**:
```
Persona + Questions → Interview Generator → LLM (role-playing) → Interview Responses → CSV Files
```

## Design Principles

1. **Statistical Fidelity**: Base personas reflect real Iranian demographic distributions
2. **Cultural Authenticity**: All generated content respects Iranian cultural context
3. **Consistency**: Personas maintain character throughout interviews
4. **Diversity**: Represents various ethnicities, religions, and social backgrounds
5. **Validation**: Base persona fields must remain unchanged by LLM

## Usage Example

```python
from generators import PersonaGenerator, generate_base_persona
from utils import LLMClient, create_openai_client

# Generate base persona with statistics
base = generate_base_persona()
# Returns: {"age": 72, "gender": "Female", "ethnicity": "Persian", ...}

# Complete with LLM
client = create_openai_client()
llm_client = LLMClient(client)
generator = PersonaGenerator(llm_client)
full_persona = generator.complete_personas([base], model="gpt-5-mini")
```

