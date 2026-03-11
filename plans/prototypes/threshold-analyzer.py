#!/usr/bin/env python3
"""Measure threshold-relevant distributions across memory-index entries.

Analyzes the 366-entry dataset for 5 threshold dimensions:
1. Keyword count per entry
2. Content words per trigger (title words after prefix)
3. Pairwise keyword overlap (asymmetric)
4. Keyword discrimination (IDF-like)
5. Fuzzy match scores (entry key vs semantic headers)

Outputs JSON to stdout for flexible downstream rendering.
"""

import json
import sys
from collections import Counter
from pathlib import Path

# Add src/ to path for project imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from claudeutils.recall.index_parser import (
    IndexEntry,
    extract_keywords,
    parse_memory_index,
)
from claudeutils.validation.memory_index_helpers import collect_semantic_headers
from claudeutils.when.fuzzy import score_match


def percentiles(values: list[float]) -> dict[str, float]:
    """Compute percentile breakdown."""
    if not values:
        return {}
    s = sorted(values)
    n = len(s)

    def p(pct: float) -> float:
        idx = int(pct / 100 * (n - 1))
        return round(s[idx], 4)

    return {
        "count": n,
        "min": round(s[0], 4),
        "max": round(s[-1], 4),
        "mean": round(sum(s) / n, 4),
        "median": p(50),
        "p10": p(10),
        "p25": p(25),
        "p75": p(75),
        "p90": p(90),
    }


def histogram(values: list[float], bucket_count: int = 10) -> list[dict]:
    """Create histogram buckets."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if lo == hi:
        return [{"range": f"{lo}", "count": len(values)}]
    width = (hi - lo) / bucket_count
    buckets = [0] * bucket_count
    for v in values:
        idx = min(int((v - lo) / width), bucket_count - 1)
        buckets[idx] += 1
    return [
        {
            "range": f"{round(lo + i * width, 2)}-{round(lo + (i + 1) * width, 2)}",
            "count": buckets[i],
        }
        for i in range(bucket_count)
    ]


def analyze_keyword_counts(entries: list[IndexEntry]) -> dict:
    """Distribution of keyword count per entry."""
    counts = [len(e.keywords) for e in entries]
    return {
        "stats": percentiles([float(c) for c in counts]),
        "histogram": histogram([float(c) for c in counts], bucket_count=15),
        "extremes": {
            "zero_keywords": [e.key for e in entries if len(e.keywords) == 0],
            "high_keywords": sorted(
                [(e.key, len(e.keywords)) for e in entries if len(e.keywords) > 10],
                key=lambda x: -x[1],
            )[:20],
            "low_keywords": sorted(
                [(e.key, len(e.keywords)) for e in entries if 0 < len(e.keywords) <= 2],
                key=lambda x: x[1],
            ),
        },
    }


def analyze_content_words(entries: list[IndexEntry]) -> dict:
    """Distribution of content words in trigger titles (after prefix)."""
    word_counts = []
    details = []
    for e in entries:
        words = e.key.split()
        # Strip prefix: "When X" -> words after "When", "How to X" -> words after "How to"
        key_lower = e.key.lower()
        if key_lower.startswith("how to "):
            content = words[2:]
        elif key_lower.startswith("when "):
            content = words[1:]
        else:
            content = words
        word_counts.append(len(content))
        details.append({"key": e.key, "content_words": len(content)})

    return {
        "stats": percentiles([float(c) for c in word_counts]),
        "histogram": histogram([float(c) for c in word_counts], bucket_count=10),
        "extremes": {
            "very_short": [d for d in details if d["content_words"] < 2],
            "very_long": sorted(
                [d for d in details if d["content_words"] > 6],
                key=lambda x: -x["content_words"],
            )[:20],
        },
    }


def analyze_pairwise_overlap(entries: list[IndexEntry]) -> dict:
    """Pairwise keyword overlap between entries.

    Computes asymmetric overlap: |A ∩ B| / |A| for each ordered pair.
    Only reports pairs with overlap > 0.2 to keep output tractable.
    """
    high_pairs = []
    overlap_scores = []

    for i, a in enumerate(entries):
        if not a.keywords:
            continue
        for j, b in enumerate(entries):
            if i == j or not b.keywords:
                continue
            intersection = a.keywords & b.keywords
            overlap = len(intersection) / len(a.keywords)
            if overlap > 0.2:
                overlap_scores.append(overlap)
                if overlap > 0.4:
                    high_pairs.append(
                        {
                            "entry_a": a.key,
                            "entry_b": b.key,
                            "overlap_a_to_b": round(overlap, 4),
                            "shared_keywords": sorted(intersection),
                            "a_keywords": len(a.keywords),
                            "b_keywords": len(b.keywords),
                        }
                    )

    # Sort by overlap descending
    high_pairs.sort(key=lambda x: -x["overlap_a_to_b"])

    return {
        "stats_above_0_2": percentiles(overlap_scores),
        "top_pairs": high_pairs[:30],
        "total_pairs_above_0_2": len(overlap_scores),
        "total_pairs_above_0_4": len(high_pairs),
    }


def analyze_discrimination(entries: list[IndexEntry]) -> dict:
    """Keyword discrimination analysis (IDF-like).

    For each unique keyword: how many entries contain it?
    High count = low discrimination (common word).
    Low count = high discrimination (specific word).
    """
    keyword_counts: Counter[str] = Counter()
    for e in entries:
        for kw in e.keywords:
            keyword_counts[kw] += 1

    counts = [float(c) for c in keyword_counts.values()]

    most_common = keyword_counts.most_common(20)
    least_common = sorted(
        [(kw, c) for kw, c in keyword_counts.items() if c == 1],
        key=lambda x: x[0],
    )

    return {
        "unique_keywords": len(keyword_counts),
        "stats": percentiles(counts),
        "histogram": histogram(counts, bucket_count=15),
        "least_discriminating": [
            {"keyword": kw, "entry_count": c} for kw, c in most_common
        ],
        "most_discriminating_count": len(least_common),
        "most_discriminating_sample": [
            {"keyword": kw, "entry_count": c} for kw, c in least_common[:20]
        ],
    }


def analyze_fuzzy_scores(entries: list[IndexEntry], root: Path) -> dict:
    """Fuzzy match score distribution: entry keys vs semantic headers."""
    headers = collect_semantic_headers(root)
    header_titles = list(headers.keys())

    best_scores = []
    low_matches = []
    no_matches = []

    for e in entries:
        best = 0.0
        best_header = ""
        for ht in header_titles:
            s = score_match(e.key, ht)
            if s > best:
                best = s
                best_header = ht

        best_scores.append(best)
        if best == 0.0:
            no_matches.append(e.key)
        elif best < 50.0:
            low_matches.append(
                {
                    "entry_key": e.key,
                    "best_score": round(best, 2),
                    "best_header": best_header,
                }
            )

    return {
        "stats": percentiles(best_scores),
        "histogram": histogram(best_scores, bucket_count=15),
        "no_match_count": len(no_matches),
        "no_match_keys": no_matches[:20],
        "low_match": sorted(low_matches, key=lambda x: x["best_score"])[:20],
    }


def main() -> None:
    root = Path(".")
    index_path = root / "agents" / "memory-index.md"

    entries = parse_memory_index(index_path)
    print(f"Loaded {len(entries)} entries", file=sys.stderr)

    results = {
        "entry_count": len(entries),
        "keyword_counts": analyze_keyword_counts(entries),
        "content_words": analyze_content_words(entries),
        "pairwise_overlap": analyze_pairwise_overlap(entries),
        "discrimination": analyze_discrimination(entries),
        "fuzzy_scores": analyze_fuzzy_scores(entries, root),
    }

    json.dump(results, sys.stdout, indent=2, default=str)
    print(file=sys.stdout)


if __name__ == "__main__":
    main()
