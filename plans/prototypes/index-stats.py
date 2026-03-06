#!/usr/bin/env python3
"""Measure memory-index entry distribution and token sizes."""

from pathlib import Path


def count_entries_per_section(index_path: Path) -> dict[str, int]:
    content = index_path.read_text()
    sections: dict[str, int] = {}
    current = None
    for line in content.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = 0
        elif current and line.startswith(("/when ", "/how ")):
            sections[current] += 1
    return sections


def measure_tokens(path: Path) -> int:
    """Approximate token count (1 token ~ 4 chars)."""
    return len(path.read_text()) // 4


def main() -> None:
    index_path = Path("agents/memory-index.md")
    decisions_dir = Path("agents/decisions")

    # Entry distribution
    sections = count_entries_per_section(index_path)
    print("=== Entry Distribution ===")
    for section, count in sorted(sections.items(), key=lambda x: -x[1]):
        print(f"{count:3d}  {section}")
    print(f"\nTotal: {sum(sections.values())} entries in {len(sections)} sections")

    # Token sizes
    print("\n=== Token Sizes ===")
    index_tokens = measure_tokens(index_path)
    print(f"memory-index.md: ~{index_tokens} tokens")

    print("\nDecision files:")
    total = 0
    for f in sorted(decisions_dir.glob("*.md")):
        t = measure_tokens(f)
        total += t
        print(f"{t:6d} tok  {f.name}")
    print(f"\nTotal decision files: ~{total} tokens")


if __name__ == "__main__":
    main()
