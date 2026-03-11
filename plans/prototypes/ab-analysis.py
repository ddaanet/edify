#!/usr/bin/env python3
"""Analyze A/B test results for verb form effects.

Statistical analysis:
  - McNemar's test on paired binary outcomes (primary)
  - Per-entry recognition breakdown (which entries flip?)
  - Effect size calculation
  - Instance-level sensitivity (ProSA-inspired)

Usage:
  ./ab-analysis.py                    # analyze from tmp/ab-results.json
  ./ab-analysis.py path/to/results.json
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def load_results(path: Path) -> dict:
    return json.loads(path.read_text())


def build_paired_matrix(results: dict) -> dict:
    """Build per-(task, entry) paired binary matrix.

    Returns dict with structure:
      entry -> task_id -> {"A": bool, "B": bool}
    """
    matrix: dict[str, dict[str, dict[str, bool]]] = defaultdict(
        lambda: defaultdict(lambda: {"A": False, "B": False})
    )

    for obs in results["observations"]:
        task_id = obs["task_id"]
        variant = obs["variant"]
        for entry in obs["matched_entries"]:
            # Normalize entry for cross-variant matching
            # Variant B has "/how to ..." — strip "to " for alignment
            normalized = entry
            if entry.startswith("/how to "):
                normalized = "/how " + entry[8:]
            matrix[normalized][task_id][variant] = True

    return dict(matrix)


def mcnemar_test(matrix: dict) -> dict:
    """McNemar's test on discordant pairs.

    Discordant pairs: entry recognized under one variant but not the other.
      b = recognized in A only (format change lost recognition)
      c = recognized in B only (format change gained recognition)

    H0: b = c (no format effect)
    Test statistic: chi2 = (b - c)^2 / (b + c)
    """
    # Count all (task, entry) pairs
    b_count = 0  # A yes, B no
    c_count = 0  # A no, B yes
    concordant_yes = 0  # both yes
    concordant_no = 0  # both no
    total_pairs = 0

    all_entries = set()
    all_tasks = set()

    for entry, tasks in matrix.items():
        all_entries.add(entry)
        for task_id, recognition in tasks.items():
            all_tasks.add(task_id)

    # We need the full cross product — entries not mentioned are "not recognized"
    # But we only have entries that were recognized in at least one variant
    # For the full matrix we need all entries × all tasks

    # Get all task IDs from observations
    observations = []  # will be rebuilt from raw data
    return _mcnemar_from_raw(matrix, all_entries, all_tasks)


def _mcnemar_from_raw(matrix: dict, all_entries: set, all_tasks: set) -> dict:
    """Compute McNemar's from the paired matrix."""
    b = 0  # A=yes, B=no
    c = 0  # A=no, B=yes
    concordant_yes = 0
    concordant_no = 0

    for entry in all_entries:
        tasks_data = matrix.get(entry, {})
        for task_id in all_tasks:
            recognition = tasks_data.get(task_id, {"A": False, "B": False})
            a_rec = recognition.get("A", False)
            b_rec = recognition.get("B", False)

            if a_rec and not b_rec:
                b += 1
            elif not a_rec and b_rec:
                c += 1
            elif a_rec and b_rec:
                concordant_yes += 1
            # concordant_no is the vast majority (not tracked — too large)

    total_discordant = b + c

    # McNemar's chi-squared (with continuity correction for small samples)
    if total_discordant == 0:
        chi2 = 0.0
        p_value = 1.0
    else:
        # Without continuity correction
        chi2 = (b - c) ** 2 / (b + c)
        # With continuity correction (better for small samples)
        chi2_corrected = (abs(b - c) - 1) ** 2 / (b + c) if b + c > 0 else 0
        # Approximate p-value from chi2(1) distribution
        # For chi2 > 3.84, p < 0.05; chi2 > 6.63, p < 0.01
        p_value = _chi2_p_value(chi2_corrected)

    return {
        "b_a_only": b,
        "c_b_only": c,
        "concordant_yes": concordant_yes,
        "total_discordant": total_discordant,
        "chi2": chi2,
        "chi2_corrected": chi2_corrected if total_discordant > 0 else 0,
        "p_value_approx": p_value,
        "direction": "B>A" if c > b else ("A>B" if b > c else "equal"),
    }


def _chi2_p_value(chi2: float) -> float:
    """Approximate p-value for chi-squared with 1 df.

    Uses the survival function approximation. For exact values, use scipy.
    """
    import math

    if chi2 <= 0:
        return 1.0
    # Approximation via normal distribution: sqrt(chi2) ~ N(0,1)
    z = math.sqrt(chi2)
    # Complementary error function approximation
    p = math.erfc(z / math.sqrt(2))
    return p


def per_entry_analysis(matrix: dict, all_tasks: set) -> list[dict]:
    """Per-entry breakdown: which entries are format-sensitive?"""
    entry_stats = []

    for entry in sorted(matrix.keys()):
        tasks_data = matrix[entry]
        a_count = 0
        b_count = 0
        both_count = 0

        for task_id in all_tasks:
            recognition = tasks_data.get(task_id, {"A": False, "B": False})
            a_rec = recognition.get("A", False)
            b_rec = recognition.get("B", False)
            if a_rec:
                a_count += 1
            if b_rec:
                b_count += 1
            if a_rec and b_rec:
                both_count += 1

        # Sensitivity score: how much does format matter for this entry?
        total_recognized = a_count + b_count - both_count
        if total_recognized > 0:
            sensitivity = abs(a_count - b_count) / total_recognized
        else:
            sensitivity = 0.0

        entry_stats.append(
            {
                "entry": entry,
                "a_recognized": a_count,
                "b_recognized": b_count,
                "both_recognized": both_count,
                "sensitivity": sensitivity,
                "direction": "B>A"
                if b_count > a_count
                else ("A>B" if a_count > b_count else "="),
            }
        )

    # Sort by sensitivity (most format-sensitive first)
    entry_stats.sort(key=lambda x: x["sensitivity"], reverse=True)
    return entry_stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze A/B test results")
    parser.add_argument("results", help="Path to ab-results.json")
    parser.add_argument("-o", "--output", help="Output analysis JSON path")
    args = parser.parse_args()

    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Not found: {results_path}", file=sys.stderr)
        sys.exit(1)

    results = load_results(results_path)
    metadata = results.get("metadata", {})
    observations = results.get("observations", [])

    print(f"Model: {metadata.get('model', 'unknown')}")
    print(f"Tasks: {metadata.get('tasks', '?')}")
    print(
        f"Entries A: {metadata.get('entries_a', '?')}, B: {metadata.get('entries_b', '?')}"
    )
    print(f"Observations: {len(observations)}")
    print()

    # Aggregate stats
    a_obs = [o for o in observations if o["variant"] == "A"]
    b_obs = [o for o in observations if o["variant"] == "B"]

    print("=== Aggregate Recognition ===")
    a_total = sum(o["matched_count"] for o in a_obs)
    b_total = sum(o["matched_count"] for o in b_obs)
    a_avg = a_total / len(a_obs) if a_obs else 0
    b_avg = b_total / len(b_obs) if b_obs else 0
    print(f"  Variant A (bare):  {a_total} total, {a_avg:.1f} avg per task")
    print(f"  Variant B (to):    {b_total} total, {b_avg:.1f} avg per task")
    print()

    # Build paired matrix
    matrix = build_paired_matrix(results)
    all_tasks = {o["task_id"] for o in observations}

    # McNemar's test
    print("=== McNemar's Test (paired binary outcomes) ===")
    mcnemar = mcnemar_test(matrix)
    print(f"  Discordant pairs: {mcnemar['total_discordant']}")
    print(f"    A-only (lost in B): {mcnemar['b_a_only']}")
    print(f"    B-only (gained in B): {mcnemar['c_b_only']}")
    print(f"  Concordant (both recognized): {mcnemar['concordant_yes']}")
    print(f"  Chi-squared: {mcnemar['chi2']:.3f}")
    print(f"  Chi-squared (corrected): {mcnemar['chi2_corrected']:.3f}")
    print(f"  p-value (approx): {mcnemar['p_value_approx']:.4f}")
    print(f"  Direction: {mcnemar['direction']}")

    sig = "SIGNIFICANT" if mcnemar["p_value_approx"] < 0.05 else "NOT significant"
    print(f"  Result: {sig} at alpha=0.05")
    print()

    # Per-entry analysis
    print("=== Per-Entry Format Sensitivity (ProSA-inspired) ===")
    entry_stats = per_entry_analysis(matrix, all_tasks)

    sensitive = [e for e in entry_stats if e["sensitivity"] > 0]
    print(f"  Format-sensitive entries: {len(sensitive)}/{len(entry_stats)}")
    print()

    if sensitive:
        print("  Top format-sensitive entries:")
        for e in sensitive[:15]:
            trigger = e["entry"]
            if len(trigger) > 50:
                trigger = trigger[:47] + "..."
            print(
                f"    {trigger:<52} A={e['a_recognized']:>2} B={e['b_recognized']:>2} "
                f"sens={e['sensitivity']:.2f} {e['direction']}"
            )

    # Write full analysis
    analysis = {
        "aggregate": {
            "a_total": a_total,
            "b_total": b_total,
            "a_avg": a_avg,
            "b_avg": b_avg,
        },
        "mcnemar": mcnemar,
        "per_entry": entry_stats,
    }
    out_path = (
        Path(args.output) if args.output else results_path.with_name("ab-analysis.json")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(analysis, indent=2))
    print(f"\nFull analysis written to: {out_path}")


if __name__ == "__main__":
    main()
