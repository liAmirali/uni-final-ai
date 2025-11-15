#!/usr/bin/env python3
"""
Script to generate personas with optional statistics-based demographics.
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators import PersonaGenerator, generate_base_persona
from utils import LLMClient, create_openai_client, BatchProcessor, save_to_csv
from utils.logging_utils import setup_logging, log_section
from config import DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(description="Generate Iranian elderly personas")
    parser.add_argument("--count", type=int, default=10, help="Number of personas to generate")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--with-stats", action="store_true", help="Use statistical base demographics")
    parser.add_argument("--output-dir", type=str, default="outputs/personas", help="Output directory for generated personas")
    parser.add_argument("--output", type=str, default=None, help="Output file name (optional, auto-generated if not provided)")
    parser.add_argument("--batch", action="store_true", help="Use batch API")
    parser.add_argument("--batch-size", type=int, default=10, help="Personas per batch request")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level")
    parser.add_argument("--log-file", type=str, default=None, help="Path to log file (optional)")
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = args.log_file or f"logs/persona_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = setup_logging(log_level=args.log_level, log_file=log_file, script_name="generate_personas")
    
    log_section(logger, "PERSONA GENERATION SCRIPT STARTED", "INFO")
    
    # Create output directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base_dir = Path(args.output_dir)
    output_dir = output_base_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir.absolute()}")
    
    logger.info(f"Configuration:")
    logger.info(f"  - Count: {args.count}")
    logger.info(f"  - Model: {args.model}")
    logger.info(f"  - With statistics: {args.with_stats}")
    logger.info(f"  - Batch mode: {args.batch}")
    logger.info(f"  - Batch size: {args.batch_size if args.batch else 'N/A'}")
    logger.info(f"  - Output directory: {output_dir}")
    logger.info(f"  - Log file: {log_file}")
    logger.debug(f"Full arguments: {vars(args)}")
    
    # Create client and generator
    logger.info("Initializing OpenAI client and persona generator...")
    try:
        client = create_openai_client()
        logger.debug("OpenAI client created successfully")
        llm_client = LLMClient(client)
        logger.debug("LLM client initialized")
        persona_generator = PersonaGenerator(llm_client)
        logger.info("Persona generator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}", exc_info=True)
        raise
    
    if args.batch:
        log_section(logger, "BATCH GENERATION MODE", "INFO")
        # Batch generation
        logger.info("Initializing batch processor...")
        batch_processor = BatchProcessor(client)
        batch_count = (args.count + args.batch_size - 1) // args.batch_size
        logger.info(f"Will create {batch_count} batch(es) with {args.batch_size} personas each")
        
        if args.with_stats:
            logger.info("Generating base personas for batch...")
            try:
                batch = persona_generator.generate_batch_with_stats(
                    batch_processor,
                    personas_per_batch=args.batch_size,
                    batch_count=batch_count,
                    model=args.model
                )
                logger.info(f"Batch created successfully: {batch.id}")
                logger.info(f"Batch status: {batch.status}")
                logger.debug(f"Batch metadata: {batch.metadata}")
            except Exception as e:
                logger.error(f"Failed to create batch: {e}", exc_info=True)
                raise
        else:
            logger.error("Batch mode without stats is not implemented")
            raise NotImplementedError("Batch mode without stats not yet implemented")
        
        logger.info("\nTo check status and retrieve results, use:")
        logger.info(f"  batch_processor.poll_batch_status(batch)")
        logger.info(f"  batch_processor.save_batch_output(batch, output_dir='personas')")
        
    else:
        log_section(logger, "SYNCHRONOUS GENERATION MODE", "INFO")
        # Synchronous generation
        personas = []
        base_personas = []
        base_output_path = None
        
        try:
            if args.with_stats:
                logger.info("Generating base personas with statistical demographics...")
                base_personas = [generate_base_persona() for _ in range(args.count)]
                logger.info(f"Generated {len(base_personas)} base personas")
                logger.debug(f"Sample base persona: {json.dumps(base_personas[0], indent=2, ensure_ascii=False)}")
                
                # Save base personas
                base_output_file = f"base_personas_{timestamp}.csv"
                base_output_path = output_dir / base_output_file
                logger.info(f"Saving {len(base_personas)} base personas to {base_output_path.name}...")
                try:
                    save_to_csv(base_personas, str(base_output_path))
                    logger.info(f"✓ Saved base personas to: {base_output_path}")
                except Exception as e:
                    logger.error(f"Failed to save base personas: {e}", exc_info=True)
                    raise
                
                logger.info(f"Completing personas using model '{args.model}'...")
                logger.info("Sending request to LLM...")
                personas = persona_generator.complete_personas(base_personas, model=args.model)
                logger.info(f"Received response from model '{args.model}'")
                logger.debug(f"Response contains {len(personas)} personas")
                
                # Log first persona as sample
                if personas:
                    logger.info("Sample completed persona:")
                    logger.info(json.dumps(personas[0], indent=2, ensure_ascii=False))
            else:
                logger.info(f"Generating {args.count} full personas using model '{args.model}'...")
                logger.info("Sending request to LLM...")
                personas = persona_generator.generate_full_personas(args.count, model=args.model)
                logger.info(f"Received {len(personas)} personas from model '{args.model}'")
                
                # Log first persona as sample
                if personas:
                    logger.info("Sample generated persona:")
                    logger.info(json.dumps(personas[0], indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to generate personas: {e}", exc_info=True)
            raise
        
        # Save final personas
        final_output_file = f"final_personas_{timestamp}.csv"
        final_output_path = output_dir / final_output_file
        logger.info(f"Saving {len(personas)} final personas to {final_output_path.name}...")
        try:
            save_to_csv(personas, str(final_output_path))
            logger.info(f"✓ Saved final personas to: {final_output_path}")
        except Exception as e:
            logger.error(f"Failed to save final personas: {e}", exc_info=True)
            raise
        
        logger.info(f"✓ Generated {len(personas)} personas")
        logger.info(f"✓ Output directory: {output_dir.absolute()}")
        if args.with_stats and base_personas and base_output_path:
            logger.info(f"✓ Base personas saved to: {base_output_path.name}")
        logger.info(f"✓ Final personas saved to: {final_output_path.name}")
    
    log_section(logger, "SCRIPT COMPLETED SUCCESSFULLY", "INFO")


if __name__ == "__main__":
    main()

