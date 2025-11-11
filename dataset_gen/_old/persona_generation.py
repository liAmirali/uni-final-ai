
from persona_generation_prompt import PROMPT
import json

class PersonaDetails():
    def __init__(self, age, gender, marital_status, children, living_situation, general_health, chronic_disease, mobility, hearing_senses, vision_senses, daily_energy, personality_type, cognitive_status, dominant_emotion, emotional_intelligence, iq, attitude_toward_aging, main_social_role, social_support, social_participation, income, economic_decile, housing, religion_and_sect, internalized_moral_traits, religiosity_level, ethnicity, language, important_personal_experiences, life_satisfaction, meaning_and_purpose_in_old_age):
        self.age = age
        self.gender = gender
        self.marital_status = marital_status
        self.children = children
        self.living_situation = living_situation
        self.general_health = general_health
        self.chronic_disease = chronic_disease
        self.mobility = mobility
        self.hearing_senses = hearing_senses
        self.vision_senses = vision_senses
        self.daily_energy = daily_energy
        self.personality_type = personality_type
        self.cognitive_status = cognitive_status
        self.dominant_emotion = dominant_emotion
        self.emotional_intelligence = emotional_intelligence
        self.iq = iq
        self.attitude_toward_aging = attitude_toward_aging
        self.main_social_role = main_social_role
        self.social_support = social_support
        self.social_participation = social_participation
        self.income = income
        self.economic_decile = economic_decile
        self.housing = housing
        self.religion_and_sect = religion_and_sect
        self.internalized_moral_traits = internalized_moral_traits
        self.religiosity_level = religiosity_level
        self.ethnicity = ethnicity
        self.language = language
        self.important_personal_experiences = important_personal_experiences
        self.life_satisfaction = life_satisfaction
        self.meaning_and_purpose_in_old_age = meaning_and_purpose_in_old_age

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def to_dict(self):
        return self.__dict__
 [markdown]
# # Age Pyramid
 [markdown]
# ## Overview
# 
# This notebook provides two approaches for generating Iranian elderly personas:
# 
# ### 1. **Statistical Base Persona Generation** (New - Recommended)
# Generate personas with demographics based on real Iranian population statistics:
# - **Age distribution**: Follows decaying distribution for elderly (65-95)
# - **Gender distribution**: 53% Female, 47% Male
# - **Ethnicity/Language**: Reflects Iranian ethnic diversity (Persian, Azeri, Kurdish, etc.)
# - **Religion**: Matches ethnicity-based religious distributions
# - **Marital status, Children, Living situation**: Based on Iranian family patterns
# 
# The LLM then fills in psychological, social, economic, and contextual fields that are consistent with these demographics.
# 
# ### 2. **Full LLM Generation** (Original)
# Let the LLM generate all fields from scratch based on the full prompt.
# 
# ---
# 
 [markdown]
# ## Quick Reference
# 
# ### For Statistical Base Persona Generation:
# 
# ```python
# # Synchronous (for testing):
# personas = generate_personas_with_stats_sync(personas_count=10)
# 
# # Asynchronous batch (for large scale):
# batch = call_llm_batch_with_base_personas(
#     model=MODEL_TO_USE,
#     personas_per_batch=10,
#     batch_count=20  # Total: 200 personas
# )
# ```
# 
# ### For Full LLM Generation:
# 
# ```python
# # Original approach:
# batch = call_llm_batch(MODEL_TO_USE, messages(10), 20)
# ```
# 

import random

def generate_base_persona_complete():
    """
    Generate a base persona with statistically-based demographic fields.
    Returns a dictionary with predefined fields based on Iranian elderly population statistics.
    The LLM will fill in the remaining fields.
    """
    # Gender distribution (F: 53%, M: 47%)
    gender = random.choices(["Female", "Male"], weights=[53, 47])[0]
    
    # Age distribution (decaying distribution for elderly)
    age = random.choices(range(65, 95), weights=[25, 20, 15, 15, 10, 10, 5, 3, 2, 1])[0]
    
    # Marital status distribution
    marital_status = random.choices(["Married", "Single", "Divorced", "Widowed"], weights=[60, 30, 5, 5])[0]
    
    # Children distribution
    children = random.choices(["None", "1", "2-3", "4+"], weights=[5, 15, 30, 50])[0]
    
    # Living situation distribution
    living_situation = random.choices(["Living with Family", "Living Alone", "Shared Housing"], weights=[50, 30, 20])[0]
    
    # Ethnicity distribution (approximate Iranian demographics)
    ethnicity = random.choices(
        ["Persian", "Azeri", "Kurdish", "Lur", "Baloch", "Arab", "Turkmen", "Gilaki", "Mazandarani", "Qashqai"],
        weights=[50, 25, 10, 5, 3, 2, 1, 2, 1, 1]
    )[0]
    
    # Language typically matches ethnicity
    language_map = {
        "Persian": "Persian", "Azeri": "Azeri", "Kurdish": "Kurdish",
        "Lur": "Luri", "Baloch": "Balochi", "Arab": "Arabic",
        "Turkmen": "Turkmen", "Gilaki": "Gilaki",
        "Mazandarani": "Mazandarani", "Qashqai": "Qashqai"
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
        religion = random.choices(["Shia Muslim", "Sunni Muslim", "Zoroastrian", "Christian", "Jewish"], 
                                 weights=[85, 10, 2, 2, 1])[0]
    
    return {
        "age": age,
        "gender": gender,
        "marital_status": marital_status,
        "children": children,
        "living_situation": living_situation,
        "ethnicity": ethnicity,
        "language": language,
        "religion_and_sect": religion
    }


# Test the function
base_persona_sample = generate_base_persona_complete()
print("Sample base persona:")
print(json.dumps(base_persona_sample, indent=2, ensure_ascii=False))


def create_constrained_prompt(base_personas: list):
    """
    Create a prompt that asks the LLM to complete personas with predefined demographic fields.
    
    Args:
        base_personas: List of dictionaries containing predefined demographic fields
    
    Returns:
        str: Prompt for the LLM
    """
    
    base_prompt = """You must complete the following Iranian elderly persona(s) by filling in the missing fields.

Rules:
- The demographic fields (age, gender, marital_status, children, living_situation, ethnicity, language, religion_and_sect) are already provided. DO NOT change them.
- Fill in all the remaining fields with realistic values that are consistent with the provided demographic information.
- Ensure diversity in the values you assign, but maintain realism and internal consistency.
- Personas should reflect cultural and social realities of Iran.
- Reactions and attitudes do not need to be "correct" or "moral"; they may be shaped by culture, personal experience, or limitations.
- Personality traits and psychological states should be consistent with the individual's background.

Fields to fill in:
### Biological Component
* **General Health**: ["Good", "Average", "Poor"]
* **Chronic Disease**: [None, "High Blood Pressure", "Cardiovascular Diseases", "Type 2 Diabetes", "Arthritis and Joint Pain", "Osteoporosis", "Alzheimer's and Dementia", "Chronic Kidney Disease", "Chronic Obstructive Pulmonary Disease", "Chronic Depression and Anxiety", "Vision and Hearing Problems", "Chronic Liver Failure", "Parkinson's", "Chronic Sleep Disorders", "Chronic Gastrointestinal Issues"]
* **Mobility**: ["Independent", "With Cane or Walker", "In Wheelchair", "Dependent"]
* **Hearing Senses**: ["Good", "Average", "Poor"]
* **Vision Senses**: ["Good", "Average", "Poor"]
* **Daily Energy**: ["High", "Average", "Low"]

### Psychological Component
* **Personality Type**: ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
* **Cognitive Status**: ["Healthy Memory", "Mild Forgetfulness", "Alzheimer's"]
* **Dominant Emotion**: ["Happy", "Sad", "Anxious", "Calm"]
* **Emotional Intelligence**: ["Low", "Average", "High"]
* **IQ**: ["Low", "Average", "High"]
* **Attitude Toward Aging**: ["Acceptance", "Resistance", "Meaning-Seeking", "Denial"]

### Social Component
* **Main Social Role**: ["Grandfather", "Grandmother", "Retired", "Social Activist"]
* **Social Support**: ["Large Family", "Alone", "Supportive Friends", "Government Support"]
* **Social Participation**: ["Active", "Inactive"]

### Economic Component
* **Income**: ["Independent", "Retirement Pension", "Dependent on Children", "No Income"]
* **Economic Decile**: integer 1–10
* **Housing**: ["Own Home", "Rented", "Nursing Home"]

### Cultural-Value Component
* **Internalized Moral Traits**: list of 2–4 traits (positive or negative)
* **Religiosity Level**: ["Low", "Average", "High"]

### Contextual Component
* **Important Personal Experiences**: ["Immigration", "Career Success", "Loss of Loved Ones", "War Experience", "Economic Hardship", "Educational Achievement", "Battle with Serious Illness (e.g., Cancer, Chronic Disease)"]
* **Life Satisfaction**: ["Satisfied", "Dissatisfied", "Neutral"]
* **Meaning and Purpose in Old Age**: ["Helping Family", "Spiritual Activities", "Waiting for Death", "Pleasure-Seeking"]

Base personas to complete:
"""
    
    personas_str = json.dumps(base_personas, indent=2, ensure_ascii=False)
    
    return base_prompt + personas_str


def messages_with_base(base_personas: list):
    """
    Create messages for the LLM with base personas that need to be completed.
    
    Args:
        base_personas: List of dictionaries containing predefined demographic fields
    
    Returns:
        list: Messages for the LLM API
    """
    return [
        {
            "role": "system",
            "content": create_constrained_prompt(base_personas)
        },
        {
            "role": "user",
            "content": f"Complete all {len(base_personas)} persona(s) by filling in the missing fields. Return ONLY the JSON array with complete personas, no extra text or markdown formatting."
        }
    ]


def call_llm_batch_with_base_personas(model, personas_per_batch=10, batch_count=1, batch_file_path="batch_input.jsonl"):
    """
    Call the OpenAI Batch API with pre-generated base personas.
    
    Args:
        model (str): The model to use.
        personas_per_batch (int): Number of personas per batch request.
        batch_count (int): The number of batch requests to create.
        batch_file_path (str): Path to save the batch input file.
    
    Returns:
        dict: Batch metadata including status and file IDs.
    """
    import json
    import os
    
    # Step 1: Prepare the batch input file
    with open(batch_file_path, "w", encoding="utf-8") as f:
        for i in range(batch_count):
            # Generate base personas for this batch
            base_personas = [generate_base_persona_complete() for _ in range(personas_per_batch)]
            
            # Create messages with these base personas
            batch_messages = messages_with_base(base_personas)
            
            batch_request = {
                "custom_id": f"request-{i+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": batch_messages,
                    "temperature": TEMPERATURE,
                    "top_p": TOP_P,
                    "presence_penalty": PRESENCE_PENALTY,
                    "frequency_penalty": FREQUENCY_PENALTY
                }
            }
            f.write(json.dumps(batch_request, ensure_ascii=False) + "\n")
    
    # Step 2: Upload the batch input file
    batch_input_file = client.files.create(
        file=open(batch_file_path, "rb"),
        purpose="batch"
    )
    
    # Step 3: Create the batch
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": f"Batch processing for {batch_count * personas_per_batch} personas with base demographics"
        }
    )
    
    return batch

 [markdown]
# # Example: Generate Personas with Predefined Statistics
# 
# The new workflow:
# 1. **`generate_base_persona_complete()`** - Generates demographic fields based on Iranian population statistics
# 2. **`messages_with_base()`** - Creates messages that instruct the LLM to complete the persona
# 3. **`call_llm_batch_with_base_personas()`** - Creates batch jobs with statistically-generated base personas
# 
# This approach ensures:
# - Realistic demographic distributions
# - Consistency with Iranian elderly population statistics
# - LLM focuses on filling psychological, social, and contextual fields that are consistent with the demographics
# 

# Example: Test with a small batch
# Generate 3 base personas
test_base_personas = [generate_base_persona_complete() for _ in range(3)]

print("Generated base personas:")
for i, persona in enumerate(test_base_personas, 1):
    print(f"\nPersona {i}:")
    print(json.dumps(persona, indent=2, ensure_ascii=False))

# Show what the messages would look like
print("\n" + "="*80)
print("Sample prompt sent to LLM:")
print("="*80)
test_messages = messages_with_base([test_base_personas[0]])
print(test_messages[0]["content"][:1000] + "...")

 [markdown]
# # Running Batch Jobs with Base Personas
# 
# To generate personas with predefined statistics:
# 

# Example: Generate 200 personas (20 batches of 10 personas each)
# Uncomment to run:
# batch_job = call_llm_batch_with_base_personas(
#     model=MODEL_TO_USE,
#     personas_per_batch=10,  # 10 personas per batch request
#     batch_count=20,          # 20 batch requests = 200 total personas
#     batch_file_path="batch_input_with_stats.jsonl"
# )
# print(f"Batch job created: {batch_job.id}")
# print(f"Status: {batch_job.status}")

# To check status later:
# result = poll_batch_status(batch_job)
# if result:
#     output_path = save_batch_output(batch_job)
#     print(f"Personas saved to: {output_path}")

 [markdown]
# # Comparison: Old vs New Approach
# 
# ## Old Approach (Original `messages()` function)
# - LLM generates ALL fields including demographics
# - Less control over statistical distributions
# - May not accurately reflect Iranian elderly population statistics
# - Usage: `call_llm_batch(MODEL_TO_USE, messages(10), 20)`
# 
# ## New Approach (with `call_llm_batch_with_base_personas()`)
# - Demographics generated with realistic statistical distributions
# - Age, gender, marital status, ethnicity, language, religion follow Iranian population data
# - LLM focuses on psychological, social, and economic fields
# - More realistic and diverse personas
# - Usage: `call_llm_batch_with_base_personas(MODEL_TO_USE, personas_per_batch=10, batch_count=20)`
# 
# Both approaches are available - use the new approach for more statistically accurate personas!
# 

def generate_personas_with_stats_sync(personas_count=10, model=MODEL_TO_USE):
    """
    Synchronously generate personas with predefined statistics (for testing).
    
    Args:
        personas_count (int): Number of personas to generate
        model (str): Model to use
    
    Returns:
        list: List of completed persona dictionaries
    """
    # Generate base personas
    base_personas = [generate_base_persona_complete() for _ in range(personas_count)]
    
    # Create messages
    msgs = messages_with_base(base_personas)
    
    # Call API
    response = client.chat.completions.create(
        model=model,
        messages=msgs,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        presence_penalty=PRESENCE_PENALTY,
        frequency_penalty=FREQUENCY_PENALTY
    )
    
    # Parse response
    content = response.choices[0].message.content
    personas = json.loads(content)
    
    return personas


# Test synchronous generation (uncomment to run)
# print("Generating 2 personas with predefined statistics...")
# completed_personas = generate_personas_with_stats_sync(personas_count=2)
# 
# print(f"\nGenerated {len(completed_personas)} complete personas:")
# for i, persona in enumerate(completed_personas, 1):
#     print(f"\n{'='*80}")
#     print(f"Persona {i}:")
#     print('='*80)
#     print(json.dumps(persona, indent=2, ensure_ascii=False))


import random

def generate_base_persona():
    # This function will generate a base persona using available data

    #Gendeer
    # F: 53%
    # M: 47%

    # Age
    # Should follow decaing distribution of age

    # Code:
    gender = random.choices(["Female", "Male"], weights=[53, 47])[0]
    age = random.choices(range(65, 95), weights=[10, 15, 20, 25, 15, 10, 5, 3, 2, 1])[0]
    marital_status = random.choices(["Married", "Single", "Divorced", "Widowed"], weights=[60, 30, 5, 5])[0]
    children = random.choices(["0", "1", "2", "3+"], weights=[5, 15, 30, 50])[0]
    living_situation = random.choices(["Living with Family", "Living Alone", "Living with Partner"], weights=[50, 30, 20])[0]



    


print(PROMPT)

from openai import OpenAI
import os

BASE_URL = "https://api.metisai.ir/openai/v1"
API_KEY = os.getenv("METIS_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    http_client=None
)

MODEL_TO_USE = "gpt-5-mini"

TEMPERATURE = 1
TOP_P = 0.9
PRESENCE_PENALTY = 0.3
FREQUENCY_PENALTY = 0.4

def messages(persona_count: int):
    return [
        {
            "role": "system",
            "content": PROMPT
        },
        {
            "role": "user",
            "content": f"Generate {persona_count} personas. Only give the JSON array with no extra text or formatting. Don't wrap the array in markdown formatting."
        }
    ]


def call_llm_batch(model, messages, batch_count=1, batch_file_path="batch_input.jsonl"):
    """
    Call the OpenAI Batch API to process requests asynchronously.

    Args:
        model (str): The model to use.
        messages (list): The list of messages to send (single prompt with system and user roles).
        batch_count (int): The number of batches to create.
        batch_file_path (str): Path to save the batch input file.

    Returns:
        dict: Batch metadata including status and file IDs.
    """
    import json
    import os

    # Step 1: Prepare the batch input file
    with open(batch_file_path, "w", encoding="utf-8") as f:
        for i in range(batch_count):
            batch_request = {
                "custom_id": f"request-{i+1}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": model,
                    "messages": messages,
                }
            }
            f.write(json.dumps(batch_request, ensure_ascii=False) + "\n")

    # Step 2: Upload the batch input file
    batch_input_file = client.files.create(
        file=open(batch_file_path, "rb"),
        purpose="batch"
    )

    # Step 3: Create the batch
    batch = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "Batch processing for persona generation"
        }
    )

    return batch

# Token counting helpers using tiktoken
# Requires: pip install tiktoken
import tiktoken
from typing import List, Dict, Any


def num_tokens_from_messages(messages: List[Dict[str, Any]], model: str = MODEL_TO_USE) -> int:
    """Return an estimate of the number of tokens used by a list of chat messages.

    Uses heuristics commonly used with OpenAI chat models (tokens per message/name),
    falling back to the `cl100k_base` encoding when the model encoding isn't available.

    Note: exact token accounting depends on the model's internal tokenization; this
    function gives a good practical estimate for budgeting and monitoring.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        # fallback if model name is unknown to tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")

    # Heuristics from public guidance; adjust if you know exact model rules
    if model in ("gpt-3.5-turbo-0301", "gpt-4-0314"):
        tokens_per_message = 4
        tokens_per_name = -1
    else:
        tokens_per_message = 3
        tokens_per_name = 1

    total_tokens = 0
    for message in messages:
        total_tokens += tokens_per_message
        for key, value in message.items():
            # skip non-string values by converting to string
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            total_tokens += len(encoding.encode(value))
            if key == "name":
                total_tokens += tokens_per_name

    total_tokens += 3  # assistant priming (heuristic)
    return total_tokens


def num_tokens_from_string(s: str, model: str = MODEL_TO_USE) -> int:
    """Return the number of tokens in a string for the given model's tokenizer."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(s))


SAMPLE_PERSONA = {
    "age": 65,
    "gender": "Male",
    "marital_status": "Married",
    "children": "2-3",
    "living_situation": "Living with Family",
    "general_health": "Good",
    "chronic_disease": "High Blood Pressure",
    "mobility": "Independent",
    "hearing_senses": "Good",
    "vision_senses": "Good",
    "daily_energy": "High",
    "personality_type": "ISTJ",
    "cognitive_status": "Healthy Memory",
    "dominant_emotion": "Calm",
    "emotional_intelligence": "High",
    "iq": "Average",
    "attitude_toward_aging": "Acceptance",
    "main_social_role": "Grandfather",
    "social_support": "Large Family",
    "social_participation": "Active",
    "income": "Retirement Pension",
    "economic_decile": 6,
    "housing": "Own Home",
    "religion_and_sect": "Shia Muslim",
    "internalized_moral_traits": ["Respectful", "Reliable", "Generous"],
    "religiosity_level": "Average",
    "ethnicity": "Persian",
    "language": "Persian",
    "important_personal_experiences": "Educational Achievement",
    "life_satisfaction": "Satisfied",
    "meaning_and_purpose_in_old_age": "Helping Family"
}


def estimate_persona_tokens(persona_sample: Dict[str, Any], persona_count: int, model: str = MODEL_TO_USE) -> Dict[str, int]:
    """Estimate tokens for a single persona JSON and for persona_count copies of it.

    Returns a dict with single_persona_tokens and total_personas_tokens.
    """
    persona_str = json.dumps(persona_sample, ensure_ascii=False)
    single = num_tokens_from_string(persona_str, model)
    return {"single_persona_tokens": single, "total_personas_tokens": single * persona_count}


def estimate_run_tokens(persona_count: int, response_text: str, model: str = MODEL_TO_USE) -> Dict[str, int]:
    """Estimate input/output tokens for a run that asks for persona_count personas.

    - input_tokens: tokens consumed by the `messages(persona_count)` payload
    - output_tokens: tokens in the LLM response text
    - total: sum of input + output
    """
    msgs = messages(persona_count)
    input_tokens = num_tokens_from_messages(msgs, model)
    output_tokens = num_tokens_from_string(response_text or "", model)
    return {"input_tokens": input_tokens, "output_tokens": output_tokens, "total": input_tokens + output_tokens}


# Usage examples (uncomment to run):
print(num_tokens_from_messages(messages(1)))
print(estimate_persona_tokens(SAMPLE_PERSONA, 50))
# if 'personas' in globals():
#     print(estimate_run_tokens(50, personas))


from openai.types import Batch

def poll_batch_status(batch: Batch):
    batch_id = batch.id

    resp = client.batches.retrieve(batch_id)

    if resp.status == "completed":
        if resp.output_file_id:
            file_response = client.files.content(resp.output_file_id)
            return file_response
        elif resp.error_file_id:
            file_response = client.files.content(resp.error_file_id)
            return file_response
        else:
            print("Batch completed but no output_file_id")
            return None
    else:
        print(f"Batch status: {resp.status}. Not completed yet.")
        return None


def parse_response(resp):
    contents = []
    if resp:
        answers = resp.text.split("\n")[:-1]

        for batch_answer in answers:
            single_batch_resp = json.loads(batch_answer)

            answer = single_batch_resp['response']['body']['choices'][0]['message']['content']
            contents.append(answer)

    return contents

from time import time

def save_batch_output(batch):
    timestamp = time()

    output_path = f"personas/batch_output_{timestamp}.jsonl"
    result = poll_batch_status(batch)
    if not result:
        print("Batch not completed yet or no output available.")
        return
        
    parsed = parse_response(result)

    with open(output_path, "w", encoding="utf-8") as f:
        for p in parsed:
            f.write(json.dumps(json.loads(p)) + "\n")

    return output_path

test_messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "What is the capital of France?"
    }
]

resp = call_llm_batch(MODEL_TO_USE, test_messages, 2)

result = poll_batch_status(resp)
if result:
    print(parse_response(result))

resp = call_llm_batch(MODEL_TO_USE, messages(10), 20)

result = poll_batch_status(resp)
result

save_batch_output(resp)


