# Dataset Generation for Iranian Elderly Interview Study

This project generates synthetic interview data from Iranian elderly personas for spiritual health research.

## Project Structure

```
dataset_gen/
├── config.py                    # Configuration and constants
├── models/                      # Data models
│   ├── persona.py              # PersonaDetails dataclass
│   └── enums.py                # SUBJECTS enum
├── generators/                  # Generation logic
│   ├── persona_generator.py    # Persona generation with statistics
│   └── interview_generator.py  # Interview generation
├── utils/                       # Utilities
│   ├── llm_client.py           # LLM API wrapper
│   ├── batch_utils.py          # Batch API utilities
│   └── token_utils.py          # Token counting
├── prompts/                     # Prompt templates
│   ├── persona_prompts.py      # Persona generation prompts
│   └── interview_prompts.py    # Interview prompts
├── scripts/                     # Executable scripts
│   ├── generate_personas.py    # Generate personas
│   └── generate_interviews.py  # Generate interviews
├── notebooks/                   # Jupyter notebooks for exploration
├── questions.py                 # Interview questions
├── data/                        # Generated data
└── knowledge_base/              # Reference data
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
METIS_API_KEY=your_api_key_here
```

## Usage

### Generate Personas

Generate personas with statistical demographics:

```bash
# Generate 50 personas with statistics
python scripts/generate_personas.py --count 50 --with-stats --output personas.json

# Use batch API for large-scale generation
python scripts/generate_personas.py --count 200 --with-stats --batch --batch-size 10
```

Options:
- `--count`: Number of personas to generate (default: 10)
- `--model`: Model to use (default: gpt-5-mini)
- `--with-stats`: Use statistical base demographics
- `--output`: Output file path
- `--batch`: Use batch API
- `--batch-size`: Personas per batch request (default: 10)

### Generate Interviews

Generate interview responses from personas:

```bash
# Generate interviews for all personas in file
python scripts/generate_interviews.py \
    --personas knowledge_base/personas.json \
    --models gpt-5-nano \
    --output-dir data/v2.0 \
    --delay 5.0
```

Options:
- `--personas`: Path to personas file (JSON or JSONL)
- `--models`: Models to use (can specify multiple)
- `--output-dir`: Output directory (default: data/v2.0)
- `--delay`: Delay between API calls in seconds (default: 5.0)

## Programmatic Usage

### Generate Personas

```python
from generators import PersonaGenerator
from utils import LLMClient, create_openai_client

# Create client
client = create_openai_client()
llm_client = LLMClient(client)

# Create generator
persona_generator = PersonaGenerator(llm_client)

# Generate with statistics
personas = persona_generator.generate_with_stats(count=10, model="gpt-5-mini")

# Or generate full personas (LLM chooses all fields)
personas = persona_generator.generate_full_personas(count=10)
```

### Generate Interviews

```python
from generators.interview_generator import DatasetGenerator
from utils import LLMClient, create_openai_client
from questions import INTERVIEW_QUESTIONS

# Load personas
with open("personas.json") as f:
    personas = json.load(f)

# Create dataset generator
client = create_openai_client()
llm_client = LLMClient(client)

dataset_generator = DatasetGenerator(
    personas=personas,
    interview_questions=INTERVIEW_QUESTIONS,
    models=["gpt-5-nano"],
    llm_client=llm_client,
    output_dir="data/output"
)

# Generate
interactions = dataset_generator.generate_dataset(delay=5.0)
```

## Features

### Persona Generation

1. **Statistical Demographics**: Generates age, gender, ethnicity, language, and religion based on Iranian population statistics
2. **Full LLM Generation**: Lets LLM generate all fields
3. **Batch API Support**: For large-scale generation
4. **Synchronous API**: For quick testing

### Interview Generation

1. **Context-Aware**: Maintains conversation history
2. **Multi-Model Support**: Generate with multiple models
3. **Structured Output**: JSONL format per persona-model combination
4. **Error Handling**: Robust error handling with configurable retry

## Configuration

Edit `config.py` to customize:
- API endpoints and keys
- Models available
- Generation parameters (temperature, top_p, etc.)
- Random seed for reproducibility

## Notebooks

Jupyter notebooks in `notebooks/` provide interactive exploration and analysis tools.

## Data Output

Generated files follow the pattern:
```
synthetic_elder_fa_{timestamp}_{model}_{persona_id}.jsonl
```

Each line contains one interaction with:
- `id`: Unique interaction ID
- `question_id`: Reference to question
- `question_type`: "main" or "follow_up"
- `subject`: Subject category
- `question`: The question text
- `answer`: Generated answer
- `model`: Model used
- `persona_id`: Persona identifier

