#!/usr/bin/env python3
"""
Script to generate interview datasets from personas and questions.
"""
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators import InterviewGenerator
from generators.interview_generator import DatasetGenerator
from utils import LLMClient, create_openai_client
from utils.logging_utils import setup_logging, log_model_response, log_progress, log_section
from questions import INTERVIEW_QUESTIONS
from config import DEFAULT_MODEL, VERSION


def load_personas(personas_path: str, logger: logging.Logger):
    """Load personas from file (supports JSON, JSONL, or CSV)."""
    logger.info(f"Loading personas from: {personas_path}")
    logger.debug(f"File extension: {Path(personas_path).suffix}")
    
    try:
        if personas_path.endswith(".csv"):
            logger.debug("Loading from CSV format...")
            df = pd.read_csv(personas_path, encoding="utf-8")
            logger.debug(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            # Convert DataFrame to list of dictionaries
            # Handle comma-separated values in cells (like internalized_moral_traits)
            personas = df.to_dict("records")
            logger.debug("Converting DataFrame to list of dictionaries...")
            # Convert string lists back to lists where needed
            for persona in personas:
                for key, value in persona.items():
                    if isinstance(value, str) and "," in value and key in ["internalized_moral_traits"]:
                        # Split comma-separated strings back to lists
                        persona[key] = [v.strip() for v in value.split(",") if v.strip()]
            logger.info(f"Successfully loaded {len(personas)} personas from CSV")
        elif personas_path.endswith(".jsonl"):
            logger.debug("Loading from JSONL format...")
            personas = []
            with open(personas_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        personas.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse line {line_num}: {e}")
            logger.info(f"Successfully loaded {len(personas)} personas from JSONL")
        else:
            logger.debug("Loading from JSON format...")
            with open(personas_path, "r", encoding="utf-8") as f:
                personas = json.load(f)
            logger.info(f"Successfully loaded {len(personas)} personas from JSON")
        
        if personas:
            logger.debug(f"Sample persona keys: {list(personas[0].keys())}")
        return personas
    except Exception as e:
        logger.error(f"Failed to load personas: {e}", exc_info=True)
        raise


def main():
    parser = argparse.ArgumentParser(description="Generate interview dataset from personas")
    parser.add_argument("--personas", type=str, required=True, help="Path to personas file (JSON, JSONL, or CSV)")
    parser.add_argument("--models", type=str, nargs="+", default=[DEFAULT_MODEL], help="Models to use")
    parser.add_argument("--output-dir", type=str, default=f"data/{VERSION}", help="Output directory")
    parser.add_argument("--delay", type=float, default=5.0, help="Delay between API calls (seconds)")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--log-file", type=str, default=None, help="Path to log file (optional)")
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = args.log_file or f"logs/interview_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = setup_logging(log_level=args.log_level, log_file=log_file, script_name="generate_interviews")
    
    log_section(logger, "INTERVIEW GENERATION SCRIPT STARTED", "INFO")
    logger.info(f"Configuration:")
    logger.info(f"  - Personas file: {args.personas}")
    logger.info(f"  - Models: {', '.join(args.models)}")
    logger.info(f"  - Output directory: {args.output_dir}")
    logger.info(f"  - Delay: {args.delay}s")
    logger.info(f"  - Log file: {log_file}")
    logger.debug(f"Full arguments: {vars(args)}")
    
    # Load personas
    logger.info("Loading personas...")
    try:
        personas = load_personas(args.personas, logger)
        logger.info(f"✓ Loaded {len(personas)} personas")
    except Exception as e:
        logger.error(f"Failed to load personas: {e}", exc_info=True)
        raise
    
    # Create output directory
    output_dir = Path(args.output_dir)
    logger.info(f"Creating output directory: {output_dir}")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Output directory ready: {output_dir.absolute()}")
    except Exception as e:
        logger.error(f"Failed to create output directory: {e}", exc_info=True)
        raise
    
    # Create client and generator
    logger.info("Initializing OpenAI client and LLM client...")
    try:
        client = create_openai_client()
        logger.debug("OpenAI client created")
        llm_client = LLMClient(client)
        logger.debug("LLM client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}", exc_info=True)
        raise
    
    logger.info(f"Interview configuration:")
    logger.info(f"  - Questions: {len(INTERVIEW_QUESTIONS)}")
    logger.debug(f"Question subjects: {[q.get('subject', 'N/A') for q in INTERVIEW_QUESTIONS[:5]]}...")
    
    # Calculate total expected interactions
    total_combos = len(personas) * len(args.models)
    total_interactions = total_combos * len(INTERVIEW_QUESTIONS)  # Rough estimate
    logger.info(f"Expected combinations: {total_combos} (personas × models)")
    logger.info(f"Estimated interactions: ~{total_interactions}")
    
    # Generate dataset
    log_section(logger, "STARTING DATASET GENERATION", "INFO")
    try:
        logger.info("Creating DatasetGenerator...")
        dataset_generator = DatasetGenerator(
            personas=personas,
            interview_questions=INTERVIEW_QUESTIONS,
            models=args.models,
            llm_client=llm_client,
            output_dir=str(output_dir)
        )
        logger.info("DatasetGenerator created successfully")
        logger.debug(f"Session prefix: {dataset_generator.session_prefix}")
        
        logger.info(f"Starting generation with delay of {args.delay}s between API calls...")
        all_interactions = dataset_generator.generate_dataset(delay=args.delay)
        
        logger.info(f"✓ Generation completed successfully")
        logger.info(f"✓ Total interactions generated: {len(all_interactions)}")
        logger.info(f"✓ Files saved in: {output_dir.absolute()}")
        
        # List generated files
        csv_files = list(output_dir.glob("*.csv"))
        if csv_files:
            logger.info(f"Generated {len(csv_files)} CSV file(s):")
            for csv_file in csv_files:
                logger.info(f"  - {csv_file.name}")
        
    except Exception as e:
        logger.error(f"Failed during dataset generation: {e}", exc_info=True)
        raise
    
    log_section(logger, "SCRIPT COMPLETED SUCCESSFULLY", "INFO")


if __name__ == "__main__":
    main()

