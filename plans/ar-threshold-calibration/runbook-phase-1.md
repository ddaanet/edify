# Phase 1: Threshold Distribution Measurement

**Type:** general
**Model:** sonnet
**Artifact destination:** exploration (plans/prototypes/) + investigation (plans/reports/)

## Objective

Measure actual distributions for all 5 threshold dimensions across the 366-entry dataset. Produce a report with distributions, percentiles, and near-duplicate identification for human review.

## Step 1.1: Build measurement script

Write `plans/prototypes/threshold-analyzer.py`.

**Inputs:**
- `agents/memory-index.md` — parsed via `parse_memory_index()` from `src/edify/recall/index_parser.py`
- `src/edify/recall/relevance.py` — `score_relevance()` for pairwise overlap
- `src/edify/when/fuzzy.py` — `score_match()` for fuzzy matching
- `src/edify/recall/index_parser.py` — `extract_keywords()` for keyword analysis

**Measurements to compute:**

1. **Keyword count per entry** — `len(entry.keywords)` distribution
2. **Content words per trigger** — word count of `entry.key` after stripping When/How prefix
3. **Pairwise keyword overlap** — for all entry pairs: `len(a.keywords & b.keywords) / len(a.keywords)` (asymmetric — compute both directions). Focus on high-overlap pairs (>0.2).
4. **Keyword discrimination** — for each unique keyword across all entries: count how many entries contain it. High count = low discrimination. Compute distribution of per-keyword entry counts.
5. **Fuzzy match scores** — for each entry key against all semantic headers (reuse `score_match()`). Distribution of best-match scores.

**Output format:** JSON to stdout (structured data for flexible rendering).

**Script structure:**
- Import from project modules (add `src/` to path)
- `analyze_keyword_counts(entries) -> dict`
- `analyze_content_words(entries) -> dict`
- `analyze_pairwise_overlap(entries) -> dict` — include top-N highest overlap pairs
- `analyze_discrimination(entries) -> dict`
- `analyze_fuzzy_scores(entries, root) -> dict`
- `main()` — parse index, run all analyses, output JSON

**No hardcoded thresholds in the analyzer** — it measures distributions, it doesn't classify.

## Step 1.2: Run analysis and produce report

Run the analyzer script against the actual dataset.

```bash
python plans/prototypes/threshold-analyzer.py > tmp/threshold-data.json
```

Then write `plans/reports/threshold-distributions.md` summarizing:
- Per-dimension: count, min, max, mean, median, p10/p25/p50/p75/p90
- Keyword count: histogram buckets
- Content words: histogram buckets
- Pairwise overlap: list of top-20 highest overlap pairs (candidates for human duplicate labeling)
- Discrimination: most/least discriminating keywords (top-10 each)
- Fuzzy scores: distribution of best-match scores, entries with low best-match (potential orphans)

**Verification:** Script runs without error. Report contains all 5 dimensions with actual measured values.

## Human Gate

After this phase completes, the report goes to the user for:
1. Review of distributions — do they match intuition?
2. Labeling of high-overlap pairs — true duplicate or distinct?
3. Assessment of keyword count extremes — over/under-specific?
4. Decision on threshold values at natural breakpoints

Phases 3-4 (configurable implementation + feedback pipeline) proceed after human input.
