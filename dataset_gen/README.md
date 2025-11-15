# Dataset Generation for Iranian Elderly Interview Study

## Project Overview

This project generates **synthetic interview datasets** from AI-created Iranian elderly personas for **spiritual health research**. The system creates realistic personas representing diverse Iranian populations and generates interview responses about spiritual health challenges in old age.

## Research Goals

### Primary Objective
Generate high-quality synthetic interview data to study **spiritual health** in Iranian elderly populations (ages 65-95) across different demographic, cultural, and social contexts.

### Research Questions
- How do different demographic factors influence spiritual health responses?
- How do personas with different backgrounds respond to common elderly challenges?
- What patterns emerge in spiritual health across ethnic, religious, and social groups?

### Key Research Areas (9 Subjects)
1. Loss of Independence
2. Loss of Social Activity
3. Physical Health and Sexual Issues
4. Loss of Close Ones and Fear of Death
5. Loss of Family Connections
6. Lifestyle Changes
7. Loss of Income
8. Loss of Aspiration
9. Life Integrity

## Business Logic

### Two-Phase Persona Generation

**Phase 1: Statistical Base Generation**
- Creates demographic fields using Iranian population statistics
- Ensures realistic distribution of age, gender, ethnicity, religion
- Fields: age, gender, marital_status, children, living_situation, ethnicity, language, religion_and_sect
- **These fields are immutable** - LLM cannot modify them

**Phase 2: LLM Completion**
- Takes base personas with demographic fields
- LLM fills remaining fields (health, psychology, social, economic, cultural, contextual)
- Maintains consistency with demographic base
- Creates complete, realistic personas

### Interview Generation

**Role-Playing Approach**:
- LLM acts as the persona throughout interview
- Maintains conversation history
- Responds in Persian (Farsi)
- Covers all 9 spiritual health subject areas
- Includes follow-up questions for depth

**Output Structure**:
- One CSV file per persona-model combination
- Each row is one question-answer interaction
- Maintains conversation context

## Data Quality Assurance

### Validation System
- **Field Preservation**: Ensures LLM doesn't modify base demographic fields
- **Consistency Checks**: Validates persona consistency
- **Statistical Validity**: Preserves demographic distributions

### Logging & Monitoring
- Comprehensive logging at all stages
- Progress tracking for long-running operations
- Model output visibility for quality control

## Project Structure

```
dataset_gen/
├── config.py                    # Configuration and API settings
├── constants.py                 # Single source of truth for persona fields
├── models/                      # Data models and enums
│   ├── persona.py              # PersonaDetails dataclass
│   └── enums.py                # SUBJECTS enum (9 spiritual health areas)
├── generators/                  # Core generation logic
│   ├── persona_generator.py    # Persona generation with statistics
│   └── interview_generator.py  # Interview generation
├── utils/                       # Infrastructure utilities
│   ├── llm_client.py           # LLM API wrapper (model-aware)
│   ├── batch_utils.py          # Batch API utilities
│   ├── csv_utils.py            # CSV conversion and saving
│   ├── logging_utils.py        # Logging infrastructure
│   ├── model_params.py         # Model capability management
│   └── token_utils.py          # Token counting
├── prompts/                     # Prompt templates
│   ├── persona_prompts.py      # Persona generation prompts
│   └── interview_prompts.py    # Interview prompts (Persian)
├── scripts/                     # Executable scripts
│   ├── generate_personas.py    # Generate personas (saves base + final)
│   ├── generate_interviews.py  # Generate interviews
│   └── validate_personas.py    # Validate field preservation
├── notebooks/                   # Jupyter notebooks for exploration
├── questions.py                 # Interview questions (9 subjects)
├── outputs/                     # Generated personas (timestamped)
│   └── personas/
├── data/                        # Generated interview data
└── knowledge_base/              # Reference data and statistics
```

See individual README files in each directory for detailed explanations.

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
# Generate 50 personas with statistics (saves both base and final)
python scripts/generate_personas.py --count 50 --with-stats --model gpt-5-mini

# Output: outputs/personas/YYYYMMDD_HHMMSS/
#   ├── base_personas_YYYYMMDD_HHMMSS.csv
#   └── final_personas_YYYYMMDD_HHMMSS.csv

# Use batch API for large-scale generation
python scripts/generate_personas.py --count 200 --with-stats --batch --batch-size 10
```

Options:
- `--count`: Number of personas to generate (default: 10)
- `--model`: Model to use (default: gpt-5-mini)
- `--with-stats`: Use statistical base demographics
- `--output-dir`: Output directory (default: outputs/personas)
- `--batch`: Use batch API
- `--batch-size`: Personas per batch request (default: 10)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file`: Custom log file path

### Generate Interviews

Generate interview responses from personas:

```bash
# Generate interviews for all personas in file
python scripts/generate_interviews.py \
    --personas outputs/personas/20250115_143022/final_personas_20250115_143022.csv \
    --models gpt-5-mini gpt-5-nano \
    --output-dir data/v2.0 \
    --delay 5.0
```

Options:
- `--personas`: Path to personas file (JSON, JSONL, or CSV)
- `--models`: Models to use (can specify multiple)
- `--output-dir`: Output directory (default: data/v2.0)
- `--delay`: Delay between API calls in seconds (default: 5.0)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file`: Custom log file path

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
3. **Structured Output**: CSV format per persona-model combination
4. **Error Handling**: Robust error handling with configurable retry
5. **Progress Tracking**: Detailed logging of generation progress

### Validation

1. **Field Preservation**: Validates that base persona fields remain unchanged
2. **Match Reporting**: Shows exact match counts and mismatches
3. **Detailed Analysis**: Field-level mismatch reporting
4. **Exit Codes**: Returns error code if validation fails

## Configuration

Edit `config.py` to customize:
- API endpoints and keys
- Models available
- Generation parameters (temperature, top_p, etc.)
- Random seed for reproducibility

## Notebooks

Jupyter notebooks in `notebooks/` provide interactive exploration and analysis tools.

## Data Output

### Persona Output

Personas are saved in timestamped directories:
```
outputs/personas/YYYYMMDD_HHMMSS/
├── base_personas_YYYYMMDD_HHMMSS.csv    # Statistical demographics
└── final_personas_YYYYMMDD_HHMMSS.csv   # Completed personas
```

### Interview Output

Interview files follow the pattern:
```
data/v2.0/synthetic_elder_fa_{timestamp}_{model}_{persona_id}.csv
```

Each CSV file contains interview interactions with columns:
- `id`: Unique interaction ID
- `question_id`: Reference to question
- `question_type`: "main" or "follow_up"
- `subject`: Subject category
- `question`: The question text (in Persian)
- `answer`: Generated answer (in Persian)
- `model`: Model used
- `persona_id`: Persona identifier

## Validation

Use the validation script to ensure data integrity:

```bash
# Validate that base persona fields are preserved
python scripts/validate_personas.py --dir outputs/personas/20250115_143022/
```

This ensures the LLM didn't modify the statistical demographic fields.

