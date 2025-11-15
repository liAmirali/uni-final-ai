# Utils Module

## Business Logic & Purpose

The `utils` module provides infrastructure and helper functions that support the dataset generation pipeline. These utilities handle LLM communication, batch processing, data formatting, and logging.

## Module Components

### `llm_client.py`

**Business Purpose**: Abstracts LLM API communication with model-specific parameter handling.

**Key Features**:
- **Model-Aware Parameters**: Automatically handles models that don't support certain parameters
- **Unified Interface**: Works with both langchain messages and simple dicts
- **Parameter Filtering**: Only sends supported parameters to each model

**Business Logic**:
- Different LLM models have different capabilities
- Some models (like `gpt-5-mini`) don't support `top_p`, `presence_penalty`, `frequency_penalty`
- The client automatically filters parameters based on model capabilities
- Ensures API calls succeed regardless of model choice

**Code Structure**:
- `LLMClient`: Main client class
- `generate()`: For langchain messages
- `generate_simple()`: For dict messages
- Uses `model_params.build_generation_params()` for parameter filtering

### `model_params.py`

**Business Purpose**: Centralized model capability management.

**Key Features**:
- **Model Registry**: Defines which parameters each model supports
- **Parameter Builder**: Constructs API parameters based on model capabilities
- **Single Source of Truth**: All model capabilities in one place

**Business Logic**:
- Models have varying parameter support
- Need to avoid API errors from unsupported parameters
- Centralized configuration makes it easy to add new models

**Code Structure**:
- `MODEL_CAPABILITIES`: Dictionary mapping models to supported parameters
- `build_generation_params()`: Filters and builds parameter dict
- `get_supported_params()`: Returns supported parameters for a model

### `batch_utils.py`

**Business Purpose**: Handles OpenAI Batch API for large-scale asynchronous processing.

**Key Features**:
- **Batch Creation**: Prepares batch input files
- **Status Polling**: Checks batch completion status
- **Result Parsing**: Extracts responses from batch output
- **CSV Export**: Saves batch results to CSV

**Business Logic**:
- Batch API allows processing many requests asynchronously
- Useful for generating hundreds of personas
- Reduces API rate limit issues
- Results are saved as CSV for easy analysis

**Code Structure**:
- `BatchProcessor`: Main class for batch operations
- `create_batch()`: Creates batch job from message list
- `poll_batch_status()`: Checks if batch completed
- `save_batch_output()`: Saves results to CSV

### `csv_utils.py`

**Business Purpose**: Handles CSV conversion and saving.

**Key Features**:
- **Nested Structure Handling**: Flattens lists and nested dicts
- **Type Conversion**: Handles None/NaN values
- **UTF-8 Support**: Proper encoding for Persian text

**Business Logic**:
- Personas contain nested structures (e.g., `internalized_moral_traits` as list)
- CSV format requires flat structure
- Lists are converted to comma-separated strings
- Nested dicts use dot notation

**Code Structure**:
- `flatten_dict_for_csv()`: Converts nested dict to flat structure
- `save_to_csv()`: Saves list of dicts to CSV file

### `logging_utils.py`

**Business Purpose**: Provides structured logging for scripts.

**Key Features**:
- **Multi-Handler**: Console (INFO) + File (DEBUG)
- **Progress Tracking**: Helper functions for progress logging
- **Section Headers**: Visual separation of script phases

**Business Logic**:
- Researchers need to track generation progress
- Debug logs help troubleshoot issues
- File logs provide audit trail
- Progress indicators show script status

**Code Structure**:
- `setup_logging()`: Configures logging system
- `log_model_response()`: Logs LLM outputs
- `log_progress()`: Shows progress percentages
- `log_section()`: Creates visual section headers

### `token_utils.py`

**Business Purpose**: Estimates token usage for cost tracking and budgeting.

**Key Features**:
- **Token Counting**: Estimates tokens for messages and strings
- **Cost Estimation**: Helps budget API usage
- **Model-Aware**: Uses correct tokenizer for each model

**Business Logic**:
- API costs depend on token usage
- Need to estimate costs before large-scale generation
- Helps researchers plan generation runs

## Design Principles

1. **Model Abstraction**: Hide model-specific differences
2. **Error Prevention**: Filter unsupported parameters automatically
3. **Data Integrity**: Proper CSV handling with encoding support
4. **Observability**: Comprehensive logging for debugging
5. **Scalability**: Batch processing for large datasets

## Usage Patterns

```python
# LLM Client
from utils import LLMClient, create_openai_client
client = create_openai_client()
llm_client = LLMClient(client)
response = llm_client.generate_simple(messages, model="gpt-5-mini")

# Batch Processing
from utils import BatchProcessor
batch_processor = BatchProcessor(client)
batch = batch_processor.create_batch(messages_list, model="gpt-5-mini")
results = batch_processor.save_batch_output(batch, output_dir="outputs")

# CSV Utilities
from utils import save_to_csv
save_to_csv(personas, "output.csv")
```

