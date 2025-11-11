#!/usr/bin/env python3
"""
Script to generate personas with optional statistics-based demographics.
"""
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators import PersonaGenerator
from utils import LLMClient, create_openai_client, BatchProcessor
from config import DEFAULT_MODEL


def main():
    parser = argparse.ArgumentParser(description="Generate Iranian elderly personas")
    parser.add_argument("--count", type=int, default=10, help="Number of personas to generate")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--with-stats", action="store_true", help="Use statistical base demographics")
    parser.add_argument("--output", type=str, default="personas_output.json", help="Output file path")
    parser.add_argument("--batch", action="store_true", help="Use batch API")
    parser.add_argument("--batch-size", type=int, default=10, help="Personas per batch request")
    
    args = parser.parse_args()
    
    # Create client and generator
    client = create_openai_client()
    llm_client = LLMClient(client)
    persona_generator = PersonaGenerator(llm_client)
    
    print(f"Generating {args.count} personas...")
    print(f"Model: {args.model}")
    print(f"With statistics: {args.with_stats}")
    print(f"Batch mode: {args.batch}")
    print()
    
    if args.batch:
        # Batch generation
        batch_processor = BatchProcessor(client)
        batch_count = (args.count + args.batch_size - 1) // args.batch_size
        
        if args.with_stats:
            batch = persona_generator.generate_batch_with_stats(
                batch_processor,
                personas_per_batch=args.batch_size,
                batch_count=batch_count,
                model=args.model
            )
        else:
            raise NotImplementedError("Batch mode without stats not yet implemented")
        
        print(f"Batch created: {batch.id}")
        print(f"Status: {batch.status}")
        print()
        print("To check status and retrieve results, use:")
        print(f"  batch_processor.poll_batch_status(batch)")
        print(f"  batch_processor.save_batch_output(batch, output_dir='personas')")
        
    else:
        # Synchronous generation
        if args.with_stats:
            personas = persona_generator.generate_with_stats(args.count, model=args.model)
        else:
            personas = persona_generator.generate_full_personas(args.count, model=args.model)
        
        # Save output
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(personas, f, ensure_ascii=False, indent=2)
        
        print(f"Generated {len(personas)} personas")
        print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()

