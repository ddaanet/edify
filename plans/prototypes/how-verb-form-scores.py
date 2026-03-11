#!/usr/bin/env python3
"""Measure fuzzy match scores across verb forms for how-class entries."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from claudeutils.when.fuzzy import score_match


HOW_ENTRIES = [
    "format runbook phase headers",
    "split test modules",
    "write init files",
    "output errors to stderr",
    "encode file paths",
    "format token count output",
    "clean markdown before formatting",
    "order markdown processing steps",
    "merge templates safely",
    "configure script entry points",
    "pass model as cli argument",
    "validate migration conformance",
    "format batch edits efficiently",
    "inject context with rule files",
    "review delegation scope template",
    "dispatch corrector from inline skill",
    "compose agents via skills",
    "recall sub-agent memory",
    "name session tasks",
    "chain multiple skills together",
]


def gerund(verb: str) -> str:
    if verb.endswith("e") and not verb.endswith("ee"):
        return verb[:-1] + "ing"
    return verb + "ing"


def main() -> None:
    print("=== Score comparison: query form vs stored bare imperative ===")
    print(f"{'Entry':<40} {'bare':>8} {'to+bare':>8} {'gerund':>8} {'strip=bare':>10}")
    print("-" * 80)

    for entry in HOW_ENTRIES:
        words = entry.split()
        verb = words[0]
        obj = " ".join(words[1:3])

        bare_query = f"{verb} {obj}"
        to_query = f"to {verb} {obj}"
        gerund_query = f"{gerund(verb)} {obj}"

        bare_score = score_match(bare_query, entry)
        to_score = score_match(to_query, entry)
        gerund_score = score_match(gerund_query, entry)

        # After removeprefix("to ") — what resolver actually does
        stripped_score = score_match(to_query.removeprefix("to "), entry)
        same = "yes" if abs(bare_score - stripped_score) < 0.01 else "no"

        print(
            f"{entry:<40} {bare_score:>8.1f} {to_score:>8.1f} {gerund_score:>8.1f} {same:>10}"
        )

    # Cross-entry ranking: does verb form affect which entry ranks #1?
    print("\n=== Cross-entry ranking: does verb form change top match? ===")
    mismatches = 0
    for entry in HOW_ENTRIES:
        words = entry.split()
        verb = words[0]
        obj = " ".join(words[1:3])

        bare_query = f"{verb} {obj}"
        to_query = f"to {verb} {obj}"

        bare_results = [(e, score_match(bare_query, e)) for e in HOW_ENTRIES]
        bare_results.sort(key=lambda x: x[1], reverse=True)
        bare_top = bare_results[0][0]

        # Simulate resolver: strip "to " then match
        stripped_query = to_query.removeprefix("to ")
        to_results = [(e, score_match(stripped_query, e)) for e in HOW_ENTRIES]
        to_results.sort(key=lambda x: x[1], reverse=True)
        to_top = to_results[0][0]

        if bare_top != to_top:
            mismatches += 1
            print(f"  MISMATCH: query='{bare_query}' bare→'{bare_top}' to→'{to_top}'")

    print(f"  Mismatches: {mismatches}/{len(HOW_ENTRIES)}")

    # Raw "to" query WITHOUT stripping — what happens if resolver didn't strip
    print("\n=== What if resolver didn't strip 'to '? ===")
    degraded = 0
    for entry in HOW_ENTRIES:
        words = entry.split()
        verb = words[0]
        obj = " ".join(words[1:3])

        bare_score = score_match(f"{verb} {obj}", entry)
        raw_to_score = score_match(f"to {verb} {obj}", entry)

        if raw_to_score < bare_score:
            degraded += 1
            pct = ((bare_score - raw_to_score) / bare_score * 100) if bare_score else 0
            print(
                f"  {entry:<40} bare={bare_score:.1f} raw_to={raw_to_score:.1f} (-{pct:.0f}%)"
            )

    print(f"  Degraded: {degraded}/{len(HOW_ENTRIES)}")


if __name__ == "__main__":
    main()
