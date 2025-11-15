# Scripts Module

## Business Logic & Purpose

The `scripts` module provides command-line interfaces for the dataset generation pipeline. These scripts enable researchers to generate personas and interviews at scale, with proper logging, validation, and output management.

### Research Workflow

The scripts support the complete research pipeline:

1. **Persona Generation** → Create diverse Iranian elderly personas
2. **Validation** → Ensure LLM preserves base demographic fields
3. **Interview Generation** → Generate spiritual health interviews

## Scripts Overview

### `generate_personas.py`

**Business Goal**: Generate synthetic Iranian elderly personas for research.

**Key Features**:
- **Statistical Demographics**: Uses Iranian population statistics for base fields
- **Two-Phase Generation**: Base personas (statistics) + LLM completion
- **Output Management**: Automatically creates timestamped directories
- **Dual Output**: Saves both base and final personas separately

**Business Logic**:
- Base personas ensure demographic representativeness
- Final personas add psychological, social, and contextual depth
- Separate files allow validation that LLM didn't modify base fields

**Usage**:
```bash
# Generate 20 personas with statistical base
python scripts/generate_personas.py --count 20 --with-stats --model gpt-5-mini

# Output structure:
# outputs/personas/20250115_143022/
#   ├── base_personas_20250115_143022.csv
#   └── final_personas_20250115_143022.csv
```

**Code Flow**:
1. Parse arguments and setup logging
2. Create timestamped output directory
3. Generate base personas (if `--with-stats`)
4. Save base personas to CSV
5. Complete personas with LLM
6. Save final personas to CSV

### `generate_interviews.py`

**Business Goal**: Generate interview responses from personas for spiritual health research.

**Key Features**:
- **Multi-Model Support**: Generate with different LLMs for comparison
- **Context Preservation**: Maintains conversation history
- **Structured Output**: CSV files per persona-model combination
- **Progress Tracking**: Detailed logging of generation progress

**Business Logic**:
- Each persona answers questions about spiritual health challenges
- Questions cover 9 subject areas (loss of independence, social activity, etc.)
- Follow-up questions probe deeper into each topic
- Multiple models allow comparison of response patterns

**Usage**:
```bash
# Generate interviews for personas
python scripts/generate_interviews.py \
    --personas outputs/personas/20250115_143022/final_personas_20250115_143022.csv \
    --models gpt-5-mini gpt-5-nano \
    --output-dir data/v2.0 \
    --delay 5.0
```

**Code Flow**:
1. Load personas from CSV/JSON/JSONL
2. Initialize LLM client and dataset generator
3. For each persona-model combination:
   - Generate full interview (all questions + follow-ups)
   - Save to CSV file
4. Report completion statistics

### `validate_personas.py`

**Business Goal**: Ensure data integrity by validating that LLM preserves base persona fields.

**Key Features**:
- **Field Comparison**: Compares base vs final personas field-by-field
- **Mismatch Detection**: Identifies any modifications to base fields
- **Detailed Reporting**: Shows which personas and fields were changed
- **Exit Codes**: Returns error code if mismatches found

**Business Logic**:
- Base persona fields (age, gender, ethnicity, etc.) must remain unchanged
- This ensures statistical representativeness is preserved
- Validation is critical for research validity

**Usage**:
```bash
# Validate using directory (auto-detects files)
python scripts/validate_personas.py --dir outputs/personas/20250115_143022/

# Or specify files explicitly
python scripts/validate_personas.py \
    --base outputs/personas/20250115_143022/base_personas_20251115_162854.csv \
    --final outputs/personas/20250115_143022/final_personas_20251115_162854.csv
```

**Code Flow**:
1. Load base and final persona files
2. Match personas by index
3. Compare shared fields (from `BASE_PERSONA_FIELDS`)
4. Report matches/mismatches
5. Generate summary statistics

## Output Structure

### Persona Generation Output
```
outputs/personas/
└── YYYYMMDD_HHMMSS/
    ├── base_personas_YYYYMMDD_HHMMSS.csv    # Statistical demographics
    └── final_personas_YYYYMMDD_HHMMSS.csv   # Completed personas
```

### Interview Generation Output
```
data/v2.0/
└── synthetic_elder_fa_YYYYMMDD_HHMMSS_{model}_{persona_id}.csv
```

## Logging

All scripts support comprehensive logging:
- **Console output**: Real-time progress (INFO level)
- **File logging**: Detailed logs with timestamps (DEBUG level)
- **Progress tracking**: Shows what's being processed
- **Model outputs**: Displays generated content

Use `--log-level DEBUG` for detailed debugging information.

