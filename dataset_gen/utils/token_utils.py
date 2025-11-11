"""
Token counting utilities using tiktoken.
"""
import json
import tiktoken
from typing import List, Dict, Any

from config import DEFAULT_MODEL


def num_tokens_from_messages(
    messages: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL
) -> int:
    """
    Return an estimate of the number of tokens used by a list of chat messages.
    
    Uses heuristics commonly used with OpenAI chat models (tokens per message/name),
    falling back to the `cl100k_base` encoding when the model encoding isn't available.
    
    Args:
        messages: List of message dictionaries
        model: Model name
    
    Returns:
        Estimated token count
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


def num_tokens_from_string(s: str, model: str = DEFAULT_MODEL) -> int:
    """
    Return the number of tokens in a string for the given model's tokenizer.
    
    Args:
        s: Input string
        model: Model name
    
    Returns:
        Token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(s))


def estimate_persona_tokens(
    persona_sample: Dict[str, Any],
    persona_count: int,
    model: str = DEFAULT_MODEL
) -> Dict[str, int]:
    """
    Estimate tokens for a single persona JSON and for persona_count copies of it.
    
    Args:
        persona_sample: Sample persona dictionary
        persona_count: Number of personas
        model: Model name
    
    Returns:
        Dictionary with single_persona_tokens and total_personas_tokens
    """
    persona_str = json.dumps(persona_sample, ensure_ascii=False)
    single = num_tokens_from_string(persona_str, model)
    return {
        "single_persona_tokens": single,
        "total_personas_tokens": single * persona_count
    }


def estimate_run_tokens(
    messages: List[Dict[str, Any]],
    response_text: str,
    model: str = DEFAULT_MODEL
) -> Dict[str, int]:
    """
    Estimate input/output tokens for a run.
    
    Args:
        messages: Input messages
        response_text: Response text from LLM
        model: Model name
    
    Returns:
        Dictionary with input_tokens, output_tokens, and total
    """
    input_tokens = num_tokens_from_messages(messages, model)
    output_tokens = num_tokens_from_string(response_text or "", model)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total": input_tokens + output_tokens
    }

