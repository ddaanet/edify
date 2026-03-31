# Problem: IDF-Weighted Relevance Scoring Prototype

## Context

Threshold distribution analysis (`plans/reports/threshold-distributions.md`) found that flat keyword overlap scoring treats high-frequency keywords ("agent" in 28 entries) identically to unique keywords ("absolute" in 1 entry). 20 keywords appear in 10+ entries, inflating false relevance matches. 76% of keywords already discriminate well (≤2 entries).

## Current scoring

`src/edify/recall/relevance.py` — `score_relevance()` uses `len(matched) / len(entry.keywords)`. All keywords weighted equally.

## Task

Prototype IDF-weighted relevance scoring. Exploration work — `plans/prototypes/`, no production changes.

- Compute IDF weights from the 363-entry corpus: `log(N / df(keyword))` where `df` = number of entries containing keyword
- Replace flat overlap with weighted overlap: `sum(idf[k] for k in matched) / sum(idf[k] for k in entry.keywords)`
- Compare ranked results: flat vs IDF-weighted on 3-5 sample session keyword sets that include high-frequency terms (agent, context, design)
- Report whether IDF weighting reduces false relevance from common keywords

## References

- `plans/reports/threshold-distributions.md` — distribution data, discrimination analysis (§4)
- `src/edify/recall/relevance.py` — current scoring implementation
- `src/edify/recall/index_parser.py` — `extract_keywords()`, `IndexEntry` model
- `plans/prototypes/threshold-analyzer.py` — reusable analysis patterns
