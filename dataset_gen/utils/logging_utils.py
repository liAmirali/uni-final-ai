"""
Logging utilities for dataset generation scripts.
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    script_name: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for scripts.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional path to log file
        script_name: Name of the script for identification
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger_name = script_name or "dataset_gen"
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler (INFO and above, simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Debug console handler (DEBUG level, detailed format)
    debug_handler = logging.StreamHandler(sys.stderr)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(detailed_formatter)
    # Only show DEBUG on stderr if level is DEBUG
    if log_level.upper() == "DEBUG":
        logger.addHandler(debug_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_model_response(logger: logging.Logger, model: str, response_content: str, max_length: int = 500):
    """
    Log model response in a readable format.
    
    Args:
        logger: Logger instance
        model: Model name
        response_content: Response content from model
        max_length: Maximum length to display (rest will be truncated)
    """
    if len(response_content) > max_length:
        preview = response_content[:max_length] + "..."
        logger.info(f"Model '{model}' response preview ({len(response_content)} chars):\n{preview}")
        logger.debug(f"Full response from '{model}':\n{response_content}")
    else:
        logger.info(f"Model '{model}' response:\n{response_content}")


def log_progress(logger: logging.Logger, current: int, total: int, item_name: str = "items"):
    """
    Log progress information.
    
    Args:
        logger: Logger instance
        current: Current item number
        total: Total number of items
        item_name: Name of the items being processed
    """
    percentage = (current / total * 100) if total > 0 else 0
    logger.info(f"Progress: {current}/{total} {item_name} ({percentage:.1f}%)")


def log_section(logger: logging.Logger, title: str, level: str = "INFO"):
    """
    Log a section header for better readability.
    
    Args:
        logger: Logger instance
        title: Section title
        level: Log level (INFO, DEBUG, etc.)
    """
    separator = "=" * 80
    getattr(logger, level.lower())(f"\n{separator}\n{title}\n{separator}")

