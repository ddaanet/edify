#!/usr/bin/env python3
"""Generate index variants for A/B testing verb form effects.

Parses memory-index.md and produces two variants:   A (control):  /how <bare
imperative>  (current format)   B (treatment): /how to <bare imperative>
(infinitive form)

All non-/how content is preserved identically. /when entries are unchanged.
"""

import argparse
import sys
from pathlib import Path


def generate_variants(index_path: Path) -> tuple[str, str, dict]:
    """Parse index and generate both variants.

    Returns:
        (variant_a_content, variant_b_content, stats)
    """
    content = index_path.read_text()
    lines = content.split("\n")

    variant_a_lines = []
    variant_b_lines = []
    how_count = 0
    when_count = 0

    # Track whether we're past the header (first ## section)
    in_entries = False

    for line in lines:
        if line.startswith("## "):
            in_entries = True
        if in_entries and line.startswith("/how "):
            how_count += 1
            # Variant A: keep as-is (bare imperative)
            variant_a_lines.append(line)
            # Variant B: insert "to" after "/how "
            trigger = line[5:]  # everything after "/how "
            # Split trigger from extras (pipe-separated)
            if "|" in trigger:
                main_trigger, extras = trigger.split("|", 1)
                variant_b_lines.append(
                    f"/how to {main_trigger.strip()} | {extras.strip()}"
                )
            else:
                variant_b_lines.append(f"/how to {trigger}")
        else:
            if line.startswith("/when "):
                when_count += 1
            variant_a_lines.append(line)
            variant_b_lines.append(line)

    stats = {
        "how_entries": how_count,
        "when_entries": when_count,
        "total_lines": len(lines),
    }

    return "\n".join(variant_a_lines), "\n".join(variant_b_lines), stats


def validate_variants(a: str, b: str, stats: dict) -> list[str]:
    """Validate variant equivalence (same entry count, only /how lines
    differ)."""
    errors = []

    a_lines = a.split("\n")
    b_lines = b.split("\n")

    if len(a_lines) != len(b_lines):
        errors.append(f"Line count mismatch: A={len(a_lines)}, B={len(b_lines)}")
        return errors

    # Only check /how lines after first ## (skip header examples)
    a_in_entries = False
    a_how = []
    for l in a_lines:
        if l.startswith("## "):
            a_in_entries = True
        if a_in_entries and l.startswith("/how "):
            a_how.append(l)
    b_in_entries = False
    b_how = []
    for l in b_lines:
        if l.startswith("## "):
            b_in_entries = True
        if b_in_entries and l.startswith("/how "):
            b_how.append(l)

    if len(a_how) != len(b_how):
        errors.append(f"/how count mismatch: A={len(a_how)}, B={len(b_how)}")

    # Every B /how line should start with "/how to "
    for i, line in enumerate(b_how):
        if not line.startswith("/how to "):
            errors.append(f"B line {i} missing 'to': {line[:60]}")

    # Non-/how lines should be identical
    for i, (al, bl) in enumerate(zip(a_lines, b_lines)):
        if not al.startswith("/how ") and al != bl:
            errors.append(f"Non-/how line {i} differs: {al[:40]} vs {bl[:40]}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate A/B index variants")
    parser.add_argument("index", help="Path to memory-index.md")
    parser.add_argument(
        "-o", "--output-dir", required=True, help="Output directory for variants"
    )
    args = parser.parse_args()

    index_path = Path(args.index)
    out_dir = Path(args.output_dir)

    if not index_path.exists():
        print(f"Index not found: {index_path}", file=sys.stderr)
        sys.exit(1)

    variant_a, variant_b, stats = generate_variants(index_path)
    errors = validate_variants(variant_a, variant_b, stats)

    if errors:
        print("Validation errors:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Entries: {stats['how_entries']} /how, {stats['when_entries']} /when")
    print(f"Lines: {stats['total_lines']}")
    print()

    out_dir.mkdir(parents=True, exist_ok=True)
    a_path = out_dir / "memory-index-variant-a.md"
    b_path = out_dir / "memory-index-variant-b.md"
    a_path.write_text(variant_a)
    b_path.write_text(variant_b)

    print(f"Variant A (bare): {a_path}")
    print(f"Variant B (to):   {b_path}")

    # Show sample diffs (skip header examples before first ##)
    a_hows = _extract_how_lines(variant_a)
    b_hows = _extract_how_lines(variant_b)
    print("\nSample (first 5):")
    for a_line, b_line in zip(a_hows[:5], b_hows[:5]):
        print(f"  A: {a_line}")
        print(f"  B: {b_line}")
        print()


def _extract_how_lines(content: str) -> list[str]:
    """Extract /how lines after first ## header."""
    result = []
    in_entries = False
    for line in content.split("\n"):
        if line.startswith("## "):
            in_entries = True
        if in_entries and line.startswith("/how "):
            result.append(line)
    return result


if __name__ == "__main__":
    main()
