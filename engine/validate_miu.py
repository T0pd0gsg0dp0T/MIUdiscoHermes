#!/usr/bin/env python3
"""Validate miu.json against schema and report statistics.

Exit codes:
    0 - Validation passed
    1 - Validation failed (schema error, missing file, etc.)
    2 - Usage error (invalid arguments)
"""

import argparse
import sys
from pathlib import Path

from engine.parser import DataParser, DataParserError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate miu.json world data against JSON Schema",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "json_file",
        nargs="?",
        default="miu.json",
        help="Path to miu.json file to validate",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output, only exit code indicates result",
    )
    parser.add_argument(
        "--stats",
        "-s",
        action="store_true",
        help="Print world statistics after validation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: File not found: {json_path}", file=sys.stderr)
        return 1

    try:
        parser = DataParser(str(json_path))
    except DataParserError as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Validation passed: {json_path}")

    if args.stats or not args.quiet:
        print(f"Locations: {len(parser.locations)}")
        print(f"Entities: {len(parser.entities)}")
        print(f"Types: {parser.get_types()}")
        print(f"Tags: {len(parser.get_tags())} total")
        for attr in ("Intellect", "Psyche", "Physique", "Motorics"):
            skills = parser.get_skills_by_attribute(attr)
            if skills:
                print(f"  Skills by {attr}: {[s['name'] for s in skills]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
