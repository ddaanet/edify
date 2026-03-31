#!/usr/bin/env python3
"""Prototype: IDF-weighted relevance scoring vs flat overlap.

Computes IDF weights from the 363-entry corpus and compares ranked results
(flat overlap vs IDF-weighted) on sample session keyword sets that include
high-frequency terms.

Outputs JSON to stdout for downstream rendering.
"""

import json
import math
import sys
from collections import Counter
from pathlib import Path

# Add src/ to path for project imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from edify.recall.index_parser import IndexEntry, parse_memory_index


def compute_idf(entries: list[IndexEntry]) -> dict[str, float]:
    """Compute IDF weights: log(N / df(keyword)) for each keyword in corpus."""
    n = len(entries)
    df: Counter[str] = Counter()
    for e in entries:
        for kw in e.keywords:
            df[kw] += 1
    return {kw: math.log(n / count) for kw, count in df.items()}


def score_flat(session_keywords: set[str], entry: IndexEntry) -> float:
    """Current production scoring: len(matched) / len(entry.keywords)."""
    if not entry.keywords:
        return 0.0
    matched = session_keywords & entry.keywords
    return len(matched) / len(entry.keywords)


def score_idf(
    session_keywords: set[str], entry: IndexEntry, idf: dict[str, float]
) -> float:
    """IDF-weighted scoring: sum(idf[k] for matched) / sum(idf[k] for entry)."""
    if not entry.keywords:
        return 0.0
    matched = session_keywords & entry.keywords
    if not matched:
        return 0.0
    numerator = sum(idf.get(k, 0.0) for k in matched)
    denominator = sum(idf.get(k, 0.0) for k in entry.keywords)
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def rank_entries(
    session_keywords: set[str],
    entries: list[IndexEntry],
    idf: dict[str, float],
    threshold: float = 0.3,
) -> dict:
    """Score all entries with both methods, return ranked comparison."""
    results = []
    for e in entries:
        flat = score_flat(session_keywords, e)
        weighted = score_idf(session_keywords, e, idf)
        matched = session_keywords & e.keywords
        if flat > 0.0 or weighted > 0.0:
            results.append(
                {
                    "key": e.key,
                    "flat_score": round(flat, 4),
                    "idf_score": round(weighted, 4),
                    "matched_keywords": sorted(matched),
                    "entry_keyword_count": len(e.keywords),
                }
            )

    flat_ranked = sorted(results, key=lambda r: -r["flat_score"])
    idf_ranked = sorted(results, key=lambda r: -r["idf_score"])

    flat_above = [r for r in flat_ranked if r["flat_score"] >= threshold]
    idf_above = [r for r in idf_ranked if r["idf_score"] >= threshold]

    # Rank position changes for entries above threshold in either method
    flat_keys = [r["key"] for r in flat_ranked]
    idf_keys = [r["key"] for r in idf_ranked]

    rank_changes = []
    for r in results:
        if r["flat_score"] >= threshold or r["idf_score"] >= threshold:
            flat_pos = flat_keys.index(r["key"]) + 1
            idf_pos = idf_keys.index(r["key"]) + 1
            rank_changes.append(
                {
                    "key": r["key"],
                    "flat_rank": flat_pos,
                    "idf_rank": idf_pos,
                    "rank_delta": flat_pos - idf_pos,
                    "flat_score": r["flat_score"],
                    "idf_score": r["idf_score"],
                    "matched_keywords": r["matched_keywords"],
                }
            )

    # Sort by absolute rank change descending
    rank_changes.sort(key=lambda r: -abs(r["rank_delta"]))

    return {
        "total_with_any_match": len(results),
        "flat_above_threshold": len(flat_above),
        "idf_above_threshold": len(idf_above),
        "flat_top_10": flat_ranked[:10],
        "idf_top_10": idf_ranked[:10],
        "biggest_rank_changes": rank_changes[:15],
        "flat_only": [r["key"] for r in flat_above if r["idf_score"] < threshold],
        "idf_only": [r["key"] for r in idf_above if r["flat_score"] < threshold],
    }


# Sample session keyword sets — include high-frequency terms
# to test whether IDF weighting reduces their influence
SAMPLE_SESSIONS = {
    "agent-context-design": {
        "description": "Session about agent design with common domain terms",
        "keywords": {"agent", "context", "design", "delegation", "prompt"},
    },
    "test-phase-hook": {
        "description": "Session about testing hooks in TDD phases",
        "keywords": {"test", "phase", "hook", "red", "green", "assertion"},
    },
    "recall-scoring-threshold": {
        "description": "Session about recall relevance scoring (this project)",
        "keywords": {"recall", "scoring", "threshold", "keyword", "relevance", "idf"},
    },
    "worktree-merge-session": {
        "description": "Session about worktree merge workflow",
        "keywords": {"worktree", "merge", "branch", "session", "commit"},
    },
    "skill-plugin-development": {
        "description": "Session about skill and plugin development",
        "keywords": {"skill", "plugin", "command", "agent", "development", "hook"},
    },
}


def analyze_idf_weights(idf: dict[str, float], entries: list[IndexEntry]) -> dict:
    """Summary statistics on IDF weights themselves."""
    df: Counter[str] = Counter()
    for e in entries:
        for kw in e.keywords:
            df[kw] += 1

    weights = sorted(idf.items(), key=lambda x: x[1])
    lowest_idf = [
        {"keyword": kw, "idf": round(w, 4), "df": df[kw]} for kw, w in weights[:20]
    ]
    highest_idf = [
        {"keyword": kw, "idf": round(w, 4), "df": df[kw]} for kw, w in weights[-20:]
    ]
    all_weights = [w for _, w in weights]

    return {
        "total_keywords": len(idf),
        "min_idf": round(all_weights[0], 4),
        "max_idf": round(all_weights[-1], 4),
        "mean_idf": round(sum(all_weights) / len(all_weights), 4),
        "lowest_idf_keywords": lowest_idf,
        "highest_idf_keywords": highest_idf,
    }


def main() -> None:
    root = Path(".")
    index_path = root / "agents" / "memory-index.md"

    entries = parse_memory_index(index_path)
    print(f"Loaded {len(entries)} entries", file=sys.stderr)

    idf = compute_idf(entries)
    print(f"Computed IDF for {len(idf)} unique keywords", file=sys.stderr)

    results = {
        "entry_count": len(entries),
        "idf_summary": analyze_idf_weights(idf, entries),
        "sessions": {},
    }

    for name, session in SAMPLE_SESSIONS.items():
        print(f"Scoring session: {name}", file=sys.stderr)
        comparison = rank_entries(session["keywords"], entries, idf)
        results["sessions"][name] = {
            "description": session["description"],
            "keywords": sorted(session["keywords"]),
            **comparison,
        }

    json.dump(results, sys.stdout, indent=2, default=str)
    print(file=sys.stdout)


if __name__ == "__main__":
    main()
