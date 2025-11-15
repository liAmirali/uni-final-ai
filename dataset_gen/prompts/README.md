# Prompts Module

## Business Logic & Purpose

The `prompts` module contains the prompt templates that guide LLM behavior when generating personas and interview responses. These prompts are critical for ensuring cultural authenticity, research validity, and data quality.

## Research Context

The prompts are designed to:
1. **Generate culturally authentic personas** that reflect Iranian elderly populations
2. **Maintain research validity** by preserving statistical demographics
3. **Ensure consistent role-playing** in interview responses
4. **Support spiritual health research** through appropriate question framing

## Module Components

### `persona_prompts.py`

**Business Purpose**: Defines how LLMs generate and complete personas.

#### `PERSONA_GENERATION_PROMPT`

**Purpose**: Generate complete personas from scratch (all fields by LLM).

**Business Logic**:
- Used when generating personas without statistical base
- Ensures diversity across all persona dimensions
- Maintains Iranian cultural context
- Covers 7 component categories (demographic, biological, psychological, social, economic, cultural, contextual)

**Key Instructions**:
- All personas must be elderly (65-90)
- Reflect cultural and social realities of Iran
- Maintain internal consistency
- Use values appropriate for Iranian context

#### `CONSTRAINED_PERSONA_PROMPT_TEMPLATE`

**Purpose**: Complete personas with predefined demographic fields.

**Business Logic**:
- **Critical**: Base demographic fields are provided and MUST NOT be changed
- LLM only fills remaining fields (health, psychology, social, etc.)
- Ensures statistical representativeness is preserved
- Fields list is dynamically generated from `BASE_PERSONA_FIELDS` constant

**Key Instructions**:
- Demographic fields (age, gender, ethnicity, etc.) are already provided
- **DO NOT change them** - this is enforced by validation
- Fill remaining fields consistently with provided demographics
- Maintain realism and internal consistency

**Code Implementation**:
- Uses `BASE_PERSONA_FIELDS` from constants (single source of truth)
- Dynamically generates field list in prompt
- Template uses f-string for field list, replace() for persona data

### `interview_prompts.py`

**Business Purpose**: Defines how personas respond to interview questions.

#### `INTERVIEW_SYSTEM_PROMPT_TEMPLATE`

**Purpose**: Instructs LLM to role-play as the persona.

**Business Logic**:
- LLM must respond as the specific persona, not generically
- Maintains persona consistency throughout interview
- Uses Persian language (Farsi)
- Includes all persona attributes and spiritual health indicators

**Key Instructions**:
- Respond only in Persian (no English)
- Use persona's tone, vocabulary, and worldview
- Maintain character consistency
- Responses should be 2-10 sentences, natural and coherent

**Persona Information Included**:
- Basic demographics (age, gender, education, occupation)
- Financial and marital status
- Personality traits and background
- Religion
- **Spiritual health indicators** for each subject area (9 different challenges)

#### `INTERVIEW_ANSWER_PROMPT_TEMPLATE`

**Purpose**: Formats individual questions for the persona.

**Business Logic**:
- Simple question formatting
- Maintains conversation flow
- Clear instruction to respond as the persona

## Design Principles

1. **Cultural Authenticity**: Prompts emphasize Iranian context
2. **Research Validity**: Base fields must be preserved
3. **Consistency**: Personas maintain character throughout
4. **Completeness**: All required fields are specified
5. **Flexibility**: Supports both full and constrained generation

## Prompt Engineering Strategy

### Persona Generation
- **Explicit field definitions**: Clear value sets for each field
- **Cultural constraints**: Iranian context emphasized
- **Diversity requirements**: Ensure representation across dimensions
- **Consistency rules**: Internal coherence required

### Interview Generation
- **Role-playing emphasis**: Clear instruction to be the persona
- **Language requirement**: Persian only
- **Context preservation**: Conversation history maintained
- **Spiritual health focus**: Questions probe spiritual responses to challenges

## Code Structure

```python
# Persona prompts
PERSONA_GENERATION_PROMPT  # Full generation
CONSTRAINED_PERSONA_PROMPT_TEMPLATE  # Completion with base fields

# Interview prompts
INTERVIEW_SYSTEM_PROMPT_TEMPLATE  # Persona role-playing
INTERVIEW_ANSWER_PROMPT_TEMPLATE  # Question formatting

# Helper functions
create_constrained_persona_prompt()  # Formats constrained prompt
format_system_prompt()  # Formats interview system prompt
format_answer_prompt()  # Formats interview question
```

## Usage Example

```python
from prompts import (
    PERSONA_GENERATION_PROMPT,
    create_constrained_persona_prompt,
    format_system_prompt,
    format_answer_prompt
)

# For persona completion
base_personas = [{"age": 72, "gender": "Female", ...}]
prompt = create_constrained_persona_prompt(base_personas)

# For interview generation
system_prompt = format_system_prompt(persona)
answer_prompt = format_answer_prompt("سوال مصاحبه؟")
```

