#!/usr/bin/env python3
"""
Validation script to compare base and final personas.

This script ensures that the LLM does not modify the base demographic fields
that were provided in the base personas.
"""
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logging_utils import setup_logging, log_section
from constants import BASE_PERSONA_FIELDS


def normalize_value(value) -> str:
    """
    Normalize a value for comparison (handle type differences).
    
    Args:
        value: Value to normalize
        
    Returns:
        Normalized string representation
    """
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    # Convert to string and strip whitespace for comparison
    return str(value).strip()


def compare_personas(base: Dict, final: Dict, shared_fields: Set[str]) -> Dict:
    """
    Compare a base persona with its final version.
    
    Args:
        base: Base persona dictionary
        final: Final persona dictionary
        shared_fields: Set of field names to compare
        
    Returns:
        Dictionary with comparison results
    """
    matches = {}
    mismatches = {}
    
    for field in shared_fields:
        base_value = normalize_value(base.get(field))
        final_value = normalize_value(final.get(field))
        
        if base_value == final_value:
            matches[field] = base_value
        else:
            mismatches[field] = {
                "base": base_value,
                "final": final_value
            }
    
    return {
        "matches": matches,
        "mismatches": mismatches,
        "match_count": len(matches),
        "mismatch_count": len(mismatches),
        "total_fields": len(shared_fields)
    }


def load_personas_csv(file_path: str) -> List[Dict]:
    """
    Load personas from CSV file.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of persona dictionaries
    """
    df = pd.read_csv(file_path, encoding="utf-8")
    # Convert DataFrame to list of dictionaries
    personas = df.to_dict("records")
    
    # Handle NaN values - convert to None
    for persona in personas:
        for key, value in persona.items():
            if pd.isna(value):
                persona[key] = None
    
    return personas


def validate_personas(
    base_file: str,
    final_file: str,
    logger
) -> Dict:
    """
    Validate that base persona fields are preserved in final personas.
    
    Args:
        base_file: Path to base personas CSV file
        final_file: Path to final personas CSV file
        logger: Logger instance
        
    Returns:
        Dictionary with validation results
    """
    logger.info(f"Loading base personas from: {base_file}")
    base_personas = load_personas_csv(base_file)
    logger.info(f"Loaded {len(base_personas)} base personas")
    
    logger.info(f"Loading final personas from: {final_file}")
    final_personas = load_personas_csv(final_file)
    logger.info(f"Loaded {len(final_personas)} final personas")
    
    if len(base_personas) != len(final_personas):
        logger.warning(
            f"Mismatch in persona counts: base={len(base_personas)}, "
            f"final={len(final_personas)}"
        )
        min_count = min(len(base_personas), len(final_personas))
        logger.warning(f"Will compare only the first {min_count} personas")
        base_personas = base_personas[:min_count]
        final_personas = final_personas[:min_count]
    
    # Find shared fields (fields that exist in both base and final)
    if base_personas and final_personas:
        base_fields = set(base_personas[0].keys())
        final_fields = set(final_personas[0].keys())
        shared_fields = BASE_PERSONA_FIELDS.intersection(base_fields).intersection(final_fields)
        
        logger.info(f"Base persona fields: {sorted(base_fields)}")
        logger.info(f"Final persona fields: {sorted(final_fields)}")
        logger.info(f"Shared fields to validate: {sorted(shared_fields)}")
        
        if not shared_fields:
            logger.error("No shared fields found between base and final personas!")
            return {
                "total_personas": len(base_personas),
                "shared_fields": [],
                "results": []
            }
    else:
        logger.error("No personas found in files!")
        return {
            "total_personas": 0,
            "shared_fields": [],
            "results": []
        }
    
    # Compare each persona
    results = []
    total_matches = 0
    total_mismatches = 0
    perfect_matches = 0
    personas_with_mismatches = []
    
    logger.info(f"\nComparing {len(base_personas)} personas...")
    
    for idx, (base, final) in enumerate(zip(base_personas, final_personas), 1):
        comparison = compare_personas(base, final, shared_fields)
        results.append({
            "persona_index": idx,
            "comparison": comparison
        })
        
        if comparison["mismatch_count"] == 0:
            perfect_matches += 1
            total_matches += comparison["match_count"]
        else:
            personas_with_mismatches.append(idx)
            total_mismatches += comparison["mismatch_count"]
            total_matches += comparison["match_count"]
            
            logger.warning(f"Persona {idx} has {comparison['mismatch_count']} mismatched field(s):")
            for field, values in comparison["mismatches"].items():
                logger.warning(
                    f"  - {field}: base='{values['base']}' vs final='{values['final']}'"
                )
    
    # Summary statistics
    total_comparisons = len(base_personas) * len(shared_fields)
    match_percentage = (total_matches / total_comparisons * 100) if total_comparisons > 0 else 0
    
    summary = {
        "total_personas": len(base_personas),
        "shared_fields": sorted(shared_fields),
        "total_field_comparisons": total_comparisons,
        "total_matches": total_matches,
        "total_mismatches": total_mismatches,
        "match_percentage": match_percentage,
        "perfect_matches": perfect_matches,
        "personas_with_mismatches": len(personas_with_mismatches),
        "persona_indices_with_mismatches": personas_with_mismatches,
        "results": results
    }
    
    return summary


def print_summary(summary: Dict, logger):
    """
    Print validation summary.
    
    Args:
        summary: Validation summary dictionary
        logger: Logger instance
    """
    log_section(logger, "VALIDATION SUMMARY", "INFO")
    
    logger.info(f"Total personas compared: {summary['total_personas']}")
    logger.info(f"Shared fields validated: {len(summary['shared_fields'])}")
    logger.info(f"  Fields: {', '.join(summary['shared_fields'])}")
    logger.info("")
    logger.info(f"Total field comparisons: {summary['total_field_comparisons']}")
    logger.info(f"Matches: {summary['total_matches']}")
    logger.info(f"Mismatches: {summary['total_mismatches']}")
    logger.info(f"Match percentage: {summary['match_percentage']:.2f}%")
    logger.info("")
    logger.info(f"Perfect matches (all fields match): {summary['perfect_matches']}/{summary['total_personas']}")
    logger.info(f"Personas with mismatches: {summary['personas_with_mismatches']}")
    
    if summary['persona_indices_with_mismatches']:
        logger.warning(f"⚠ Persona indices with mismatches: {summary['persona_indices_with_mismatches']}")
    else:
        logger.info("✓ All personas match perfectly!")
    
    # Field-level statistics
    if summary['results']:
        logger.info("\nField-level mismatch analysis:")
        field_mismatches = {}
        for result in summary['results']:
            for field, values in result['comparison']['mismatches'].items():
                if field not in field_mismatches:
                    field_mismatches[field] = 0
                field_mismatches[field] += 1
        
        if field_mismatches:
            for field, count in sorted(field_mismatches.items(), key=lambda x: x[1], reverse=True):
                logger.warning(f"  - {field}: {count} mismatch(es)")
        else:
            logger.info("  ✓ No field-level mismatches found")


def find_persona_files(directory: str) -> Tuple[str, str]:
    """
    Find base and final persona files in a directory.
    
    Args:
        directory: Directory path to search
        
    Returns:
        Tuple of (base_file, final_file) paths
    """
    dir_path = Path(directory)
    base_files = list(dir_path.glob("base_personas_*.csv"))
    final_files = list(dir_path.glob("final_personas_*.csv"))
    
    if not base_files:
        raise FileNotFoundError(f"No base persona files found in {directory}")
    if not final_files:
        raise FileNotFoundError(f"No final persona files found in {directory}")
    
    # Use the most recent files if multiple exist
    base_file = max(base_files, key=lambda p: p.stat().st_mtime)
    final_file = max(final_files, key=lambda p: p.stat().st_mtime)
    
    return str(base_file), str(final_file)


def main():
    parser = argparse.ArgumentParser(
        description="Validate that base persona fields are preserved in final personas"
    )
    parser.add_argument(
        "--base",
        type=str,
        default=None,
        help="Path to base personas CSV file (optional if --dir is provided)"
    )
    parser.add_argument(
        "--final",
        type=str,
        default=None,
        help="Path to final personas CSV file (optional if --dir is provided)"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Directory containing base and final persona files (auto-detects files)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save validation report JSON (optional)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (optional)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    from datetime import datetime
    log_file = args.log_file or f"logs/validate_personas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = setup_logging(log_level=args.log_level, log_file=log_file, script_name="validate_personas")
    
    log_section(logger, "PERSONA VALIDATION SCRIPT STARTED", "INFO")
    
    # Determine file paths
    if args.dir:
        logger.info(f"Searching for persona files in directory: {args.dir}")
        base_file, final_file = find_persona_files(args.dir)
        logger.info(f"Found base personas file: {base_file}")
        logger.info(f"Found final personas file: {final_file}")
    elif args.base and args.final:
        base_file = args.base
        final_file = args.final
    else:
        logger.error("Either --dir or both --base and --final must be provided")
        parser.print_help()
        sys.exit(1)
    
    logger.info(f"Log file: {log_file}")
    
    # Validate
    try:
        summary = validate_personas(base_file, final_file, logger)
        
        # Print summary
        print_summary(summary, logger)
        
        # Save report if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"\nValidation report saved to: {output_path}")
        
        # Exit code based on results
        if summary['total_mismatches'] > 0:
            logger.warning("\n⚠ Validation found mismatches! LLM modified base persona fields.")
            sys.exit(1)
        else:
            logger.info("\n✓ Validation passed! All base persona fields are preserved.")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

