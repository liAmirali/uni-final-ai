"""
Model parameter configuration and filtering utilities.

This module provides a centralized way to handle model-specific parameter support,
avoiding code duplication and making it easy to add new models.
"""
from typing import Dict, Set, Any, Optional
from config import TEMPERATURE, TOP_P, PRESENCE_PENALTY, FREQUENCY_PENALTY


# Model capabilities registry
# Maps model names to sets of supported parameters
MODEL_CAPABILITIES: Dict[str, Set[str]] = {
    # Full-featured models (support all parameters)
    "gpt-5": {"temperature", "top_p", "presence_penalty", "frequency_penalty"},
    "gpt-4o": {"temperature", "top_p", "presence_penalty", "frequency_penalty"},
    "grok-3": {"temperature", "top_p", "presence_penalty", "frequency_penalty"},
    "gemini-2.5-pro-preview-06-05": {"temperature", "top_p", "presence_penalty", "frequency_penalty"},
    
    # Limited models (only support temperature)
    "gpt-5-mini": {"temperature"},
    "gpt-5-nano": {"temperature"},
}

# Default parameter values
DEFAULT_PARAMS = {
    "temperature": TEMPERATURE,
    "top_p": TOP_P,
    "presence_penalty": PRESENCE_PENALTY,
    "frequency_penalty": FREQUENCY_PENALTY,
}


def get_supported_params(model: str) -> Set[str]:
    """
    Get the set of supported parameters for a given model.
    
    Args:
        model: Model name
        
    Returns:
        Set of supported parameter names
    """
    return MODEL_CAPABILITIES.get(model, {"temperature"})


def build_generation_params(
    model: str,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Build generation parameters dictionary, filtering out unsupported parameters.
    
    Args:
        model: Model name
        temperature: Temperature value (uses default if None)
        top_p: Top-p value (uses default if None)
        presence_penalty: Presence penalty value (uses default if None)
        frequency_penalty: Frequency penalty value (uses default if None)
        **kwargs: Additional parameters to include
        
    Returns:
        Dictionary of supported parameters for the model
    """
    supported = get_supported_params(model)
    params: Dict[str, Any] = {}
    
    # Add parameters only if they're supported
    if "temperature" in supported:
        params["temperature"] = temperature if temperature is not None else DEFAULT_PARAMS["temperature"]
    
    if "top_p" in supported:
        if top_p is not None:
            params["top_p"] = top_p
        elif "top_p" in DEFAULT_PARAMS:
            params["top_p"] = DEFAULT_PARAMS["top_p"]
    
    if "presence_penalty" in supported:
        penalty_value = presence_penalty if presence_penalty is not None else DEFAULT_PARAMS["presence_penalty"]
        # Only add if non-zero to avoid unnecessary parameters
        if penalty_value:
            params["presence_penalty"] = penalty_value
    
    if "frequency_penalty" in supported:
        penalty_value = frequency_penalty if frequency_penalty is not None else DEFAULT_PARAMS["frequency_penalty"]
        # Only add if non-zero to avoid unnecessary parameters
        if penalty_value:
            params["frequency_penalty"] = penalty_value
    
    # Add any additional kwargs that are in the supported set
    for key, value in kwargs.items():
        if key in supported:
            params[key] = value
    
    return params


def add_model_capabilities(model: str, supported_params: Set[str]) -> None:
    """
    Add or update model capabilities.
    
    Args:
        model: Model name
        supported_params: Set of supported parameter names
    """
    MODEL_CAPABILITIES[model] = supported_params

