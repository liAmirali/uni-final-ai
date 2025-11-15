"""
Utilities for CSV conversion and saving.
"""
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path


def flatten_dict_for_csv(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten a dictionary for CSV export, handling nested structures.
    
    Lists are converted to comma-separated strings.
    Nested dicts are flattened with dot notation.
    
    Args:
        data: Dictionary to flatten
        
    Returns:
        Flattened dictionary
    """
    flattened = {}
    for key, value in data.items():
        if isinstance(value, list):
            # Convert list to comma-separated string
            flattened[key] = ", ".join(str(v) for v in value) if value else ""
        elif isinstance(value, dict):
            # Flatten nested dict with dot notation
            for nested_key, nested_value in value.items():
                flattened[f"{key}.{nested_key}"] = nested_value
        elif value is None:
            flattened[key] = ""
        else:
            flattened[key] = value
    return flattened


def save_to_csv(data: List[Dict], output_path: str, flatten: bool = True) -> None:
    """
    Save a list of dictionaries to a CSV file.
    
    Args:
        data: List of dictionaries to save
        output_path: Path to save CSV file
        flatten: Whether to flatten nested structures (default: True)
    """
    if not data:
        raise ValueError("Cannot save empty data to CSV")
    
    # Flatten if requested
    if flatten:
        flattened_data = [flatten_dict_for_csv(item) for item in data]
    else:
        flattened_data = data
    
    # Convert to DataFrame and save
    df = pd.DataFrame(flattened_data)
    
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV, replacing NaN with empty strings
    df.to_csv(output_path, index=False, encoding='utf-8', na_rep='')

