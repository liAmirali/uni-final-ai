#!/usr/bin/env python3
"""
Script to generate interview datasets from personas and questions.
"""
import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators import InterviewGenerator
from generators.interview_generator import DatasetGenerator
from utils import LLMClient, create_openai_client
from questions import INTERVIEW_QUESTIONS
from config import DEFAULT_MODEL, VERSION


def load_personas(personas_path: str):
    """Load personas from file."""
    with open(personas_path, "r", encoding="utf-8") as f:
        if personas_path.endswith(".jsonl"):
            personas = []
            for line in f:
                personas.append(json.loads(line))
            return personas
        else:
            return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Generate interview dataset from personas")
    parser.add_argument("--personas", type=str, required=True, help="Path to personas file (JSON or JSONL)")
    parser.add_argument("--models", type=str, nargs="+", default=[DEFAULT_MODEL], help="Models to use")
    parser.add_argument("--output-dir", type=str, default=f"data/{VERSION}", help="Output directory")
    parser.add_argument("--delay", type=float, default=5.0, help="Delay between API calls (seconds)")
    
    args = parser.parse_args()
    
    # Load personas
    print(f"Loading personas from: {args.personas}")
    personas = load_personas(args.personas)
    print(f"Loaded {len(personas)} personas")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create client and generator
    client = create_openai_client()
    llm_client = LLMClient(client)
    
    print()
    print(f"Generating interviews...")
    print(f"Models: {', '.join(args.models)}")
    print(f"Questions: {len(INTERVIEW_QUESTIONS)}")
    print(f"Output directory: {output_dir}")
    print(f"Delay: {args.delay}s")
    print()
    
    # Generate dataset
    dataset_generator = DatasetGenerator(
        personas=personas,
        interview_questions=INTERVIEW_QUESTIONS,
        models=args.models,
        llm_client=llm_client,
        output_dir=str(output_dir)
    )
    
    all_interactions = dataset_generator.generate_dataset(delay=args.delay)
    
    print()
    print(f"Total interactions generated: {len(all_interactions)}")
    print(f"Files saved in: {output_dir}")


if __name__ == "__main__":
    main()

