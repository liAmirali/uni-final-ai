# Migration Guide: Old → New Structure

This guide helps you migrate from the old messy structure to the new clean structure.

## What Changed?

### Old Structure (Messy)
```
dataset_gen/
├── persona_generation.py       # 724 lines, duplicated code, test code mixed in
├── data_generation.py          # 323 lines, test code at bottom
├── persona_generation_prompt.py
├── utils.py                    # Single file
├── questions.py
├── persona_generation.ipynb    # In root
├── data_generation.ipynb       # In root
└── persona_analyzer.ipynb      # In root
```

### New Structure (Clean)
```
dataset_gen/
├── config.py                   # All configuration
├── models/                     # Data models
│   ├── persona.py
│   └── enums.py
├── generators/                 # Generation logic (no test code!)
│   ├── persona_generator.py
│   └── interview_generator.py
├── utils/                      # Utilities
│   ├── llm_client.py
│   ├── batch_utils.py
│   └── token_utils.py
├── prompts/                    # All prompts
│   ├── persona_prompts.py
│   └── interview_prompts.py
├── scripts/                    # Runnable scripts
│   ├── generate_personas.py
│   └── generate_interviews.py
├── notebooks/                  # Notebooks (moved here)
│   ├── persona_generation.ipynb
│   ├── data_generation.ipynb
│   ├── persona_analyzer.ipynb
│   └── quick_start.ipynb      # NEW!
├── questions.py               # Kept as is
└── _old/                      # Archived old files
    ├── persona_generation.py
    ├── data_generation.py
    ├── persona_generation_prompt.py
    └── utils.py
```

## Import Changes

### Before (Old)
```python
# Messy imports
from persona_generation import generate_base_persona_complete, PersonaGenerator
from persona_generation_prompt import PROMPT
from utils import SUBJECTS
import data_generation
```

### After (New)
```python
# Clean imports
from generators import PersonaGenerator, generate_base_persona
from prompts import PERSONA_GENERATION_PROMPT
from models import SUBJECTS
from generators.interview_generator import DatasetGenerator
```

## Code Migration Examples

### Example 1: Generate Personas

**Before:**
```python
# Had to navigate messy persona_generation.py with 724 lines
from persona_generation import generate_base_persona_complete, messages_with_base
from openai import OpenAI

client = OpenAI(api_key=os.getenv("METIS_API_KEY"), base_url="...")
# ... manual setup ...
```

**After:**
```python
from generators import PersonaGenerator, generate_base_persona
from utils import create_openai_client, LLMClient

client = create_openai_client()
llm_client = LLMClient(client)
persona_generator = PersonaGenerator(llm_client)

personas = persona_generator.generate_with_stats(count=10)
```

### Example 2: Generate Interviews

**Before:**
```python
# Had to use data_generation.py with test code at bottom
from data_generation import generate_one, DatasetGenerator
# ... complex setup ...
```

**After:**
```python
from generators import InterviewGenerator
from generators.interview_generator import DatasetGenerator
from utils import LLMClient, create_openai_client

client = create_openai_client()
llm_client = LLMClient(client)

interview_generator = InterviewGenerator(llm_client)
response = interview_generator.generate_response(persona, question)
```

### Example 3: Configuration

**Before:**
```python
# Configuration scattered across files
MODEL_TO_USE = "gpt-5-mini"
TEMPERATURE = 1
TOP_P = 0.9
# ... in different files ...
```

**After:**
```python
from config import DEFAULT_MODEL, TEMPERATURE, TOP_P, AVAILABLE_MODELS
```

## Running Scripts

### Before
Had to edit Python files directly or write ad-hoc scripts.

### After
Use dedicated scripts:

```bash
# Generate personas
python scripts/generate_personas.py --count 50 --with-stats

# Generate interviews
python scripts/generate_interviews.py --personas personas.json --models gpt-5-nano
```

## Benefits of New Structure

1. **Separation of Concerns**: Each module has a single responsibility
2. **No Test Code in Libraries**: Test/example code moved to notebooks or scripts
3. **Easy to Import**: Clean, logical import paths
4. **Type Safety**: Uses dataclasses and type hints
5. **Reusable**: Can import and use from other projects
6. **Maintainable**: Easy to find and modify specific functionality
7. **Documented**: README and docstrings throughout
8. **Professional**: Follows Python best practices

## Backward Compatibility

Old files are archived in `_old/` directory. They still work but are not maintained.

## Questions?

See `README.md` for full documentation or check `notebooks/quick_start.ipynb` for examples.

