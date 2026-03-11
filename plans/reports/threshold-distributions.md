# Threshold Distribution Analysis

**Dataset:** 363 entries from `agents/memory-index.md` (parsed via `parse_memory_index()`)
**Date:** 2026-03-09
**Raw data:** `tmp/threshold-data.json`

## 1. Keyword Count Per Entry

How many keywords does `extract_keywords()` produce per entry?

| Stat | Value |
|------|-------|
| Min | 3 |
| Max | 16 |
| Mean | 7.4 |
| Median | 8 |
| p10/p25/p75/p90 | 3 / 4 / 9 / 11 |

**Distribution shape:** Bimodal. Two clusters:
- Cluster A: 3-4 keywords (112 entries, 31%) — short triggers like "output errors to stderr"
- Cluster B: 7-11 keywords (186 entries, 51%) — compound triggers with extra keywords via `| extras`
- Gap at 5 keywords (only 3 entries) — natural breakpoint

**No entries have zero keywords.** Minimum is 3 (from 3-word triggers after stopword removal).

**High-keyword entries (>12):** 11 entries. All are compound triggers with pipe-delimited extras. Highest: "delegating TDD cycles to test-driver" (16 keywords).

**Relevance scoring impact:** An entry with 3 keywords has binary-like overlap scoring (each keyword = 33% of score). An entry with 16 keywords requires 5+ matches to reach the current 0.3 threshold. The keyword count directly scales the denominator of `len(matched) / len(entry.keywords)`.

## 2. Content Words Per Trigger

Word count of `entry.key` after stripping When/How to prefix.

| Stat | Value |
|------|-------|
| Min | 2 |
| Max | 8 |
| Mean | 4.2 |
| Median | 4 |
| p10/p25/p75/p90 | 3 / 3 / 5 / 6 |

**Distribution:** Unimodal, centered on 3-5 words.
- 2 words: 5 entries (floor — current minimum enforced by learnings.py)
- 3 words: 90 entries (25%)
- 4 words: 139 entries (38%) — mode
- 5 words: 86 entries (24%)
- 6 words: 37 entries (10%)
- 7-8 words: 6 entries (2%)

**Current threshold (min 2) validated.** Only 5 entries at the floor. No entries below it.

**Specificity observation:** 3-word triggers ("output errors to stderr") tend to be action-specific. 6+ word triggers ("phase files contain h2 headers in code blocks") tend to be situation-specific with more context.

## 3. Pairwise Keyword Overlap

Asymmetric overlap: `|A ∩ B| / |A|` for all ordered entry pairs.

| Stat | Value (pairs >0.2) |
|------|-------|
| Count | 2,438 pairs |
| Min | 0.21 |
| Max | 0.75 |
| Mean | 0.28 |
| Median | 0.25 |
| p75/p90 | 0.33 / 0.33 |

**Scale:** 363 entries = 131,406 ordered pairs. Only 2,438 (1.9%) have overlap >0.2. Only 110 pairs (0.08%) have overlap >0.4.

**Current threshold (0.3) context:** At 0.3, an entry is "relevant" when 30% of its keywords match session keywords. The pairwise data shows entry-to-entry overlap rarely exceeds 0.33 — most entries share at most 1/3 of keywords with any other entry.

### Top Overlap Pairs (candidates for duplicate labeling)

| Overlap | Entry A | Entry B | Shared |
|---------|---------|---------|--------|
| 0.75 | resolve agent ids to sessions | extract agent ids from sessions | agent, ids, sessions |
| 0.75 | writing red phase assertions | writing test descriptions in prose | phase, red, writing |
| 0.75 | selecting model for design guidance | selecting model for prose artifact edits | design, model, selecting |
| 0.67 | output errors to stderr | mapping hook output channel audiences | output, stderr |
| 0.67 | placing helper functions | extracting git helper functions | functions, helper |
| 0.67 | extract session titles | format session titles | session, titles |
| 0.67 | using hooks in subagents | using session start hooks | hooks, using |
| 0.67 | skill is already loaded | context already loaded for delegation | already, loaded |
| 0.67 | evolving markdown processing | order markdown processing steps | markdown, processing |
| 0.67 | split test modules | tdd cycles grow shared test file | split, test |
| 0.67 | assessing orchestration tier | tier boundary is capacity vs orchestration complexity | orchestration, tier |
| 0.67 | format runbook outlines | format runbook phase headers | format, runbook |
| 0.67 | format runbook outlines | simplifying runbook outlines | outlines, runbook |
| 0.67 | handoff precedes commit | commit precedes review delegation | commit, precedes |
| 0.67 | handoff precedes commit | end workflow with handoff and commit | commit, handoff |
| 0.63 | delegation requires commit instruction | commit precedes review delegation | agents, commit, delegation, dirty, tree |
| 0.63 | haiku GREEN phase skips lint | green phase verification includes lint | check, green, lint, phase, verification |
| 0.60 | scoping vet for cross-cutting invariants | adding verification scope to vet context | cross, cutting, grep, scope, verification, vet |

**Observation:** The 0.75 pairs are NOT true duplicates — they describe distinct decisions (resolve vs extract, design guidance vs prose edits). The high overlap comes from entries with few keywords (3-4) sharing 2-3 of them. This is a keyword-count denominator effect, not semantic duplication.

## 4. Keyword Discrimination

Per-keyword analysis: how many entries contain each unique keyword?

| Stat | Value |
|------|-------|
| Unique keywords | 1,167 |
| Median entry count | 1 |
| p75/p90 | 2 / 5 |

**Distribution:** Heavily right-skewed.
- 673 keywords (58%) appear in exactly 1 entry — perfect discrimination
- 890 keywords (76%) appear in 1-2 entries — strong discrimination
- 20 keywords appear in 10+ entries — low discrimination

**Least discriminating keywords (top-10):**

| Keyword | Entry Count |
|---------|------------|
| agent | 28 |
| context | 27 |
| review | 24 |
| agents | 21 |
| design | 21 |
| phase | 20 |
| task | 19 |
| skill | 18 |
| test | 18 |
| recall | 17 |

These are domain-vocabulary words — ubiquitous in this codebase. They provide minimal discrimination for relevance scoring but are valid keywords (not stopwords).

**Impact on relevance scoring:** When a session involves "agent" + "context" topics, 28 and 27 entries respectively contain those keywords. A 2-keyword overlap from these common keywords can push many entries past the 0.3 threshold.

## 5. Fuzzy Match Scores

Best fuzzy match score for each entry key against all semantic headers.

| Stat | Value |
|------|-------|
| Min | 293 |
| Max | 1,166 |
| Mean | 689 |
| Median | 674 |
| p10/p25/p75/p90 | 504 / 584 / 775 / 905 |

**All entries have matches.** Zero entries with no match. Zero entries below 50.0 (current threshold).

**Distribution:** Roughly normal, centered around 640-700. The current 50.0 threshold is far below any observed score — it has no discriminating effect on this dataset.

**Implication:** The 50.0 fuzzy threshold in `memory_index.py` and `memory_index_checks.py` is effectively a no-op. All entries match at scores 293+, two orders of magnitude above the threshold. The threshold would only trigger for entries with zero character overlap with any header — which doesn't happen in practice because entries are derived from headers.

## Summary: Threshold Status

| Threshold | Current | Status |
|-----------|---------|--------|
| Keyword overlap % | 0.3 | **Needs calibration** — denominator effect from variable keyword counts means 0.3 has different semantic meaning for 3-keyword vs 16-keyword entries |
| Fuzzy match | 50.0 | **Effectively no-op** — minimum observed score is 293. Current threshold discriminates nothing. |
| Content words min | 2 | **Floor validated** — 5 entries at minimum, none below. Threshold is functional. |
| Keyword count | (none) | **No threshold needed** — no zero-keyword entries exist. Bimodal distribution at 3-4 and 7-11. |
| Discrimination | (none) | **Observation only** — 20 keywords appear in 10+ entries, diluting overlap scoring. Consider IDF weighting rather than threshold. |

## Recommendations for Human Review

1. **The 0.75-overlap pairs are NOT duplicates** (verified above). The high overlap is a small-denominator artifact. No labeling needed for duplicate detection — the current dataset has no true keyword-level duplicates.

2. **The fuzzy match threshold (50.0) can be raised significantly** — the gap between threshold and minimum observed score (293 vs 50) is enormous. But: this threshold exists for a different purpose (catching entries with zero header matches), not for discrimination within the current dataset. Raising it has no effect unless new entries have poor header alignment.

3. **The real calibration need is IDF-weighted relevance scoring** — the keyword overlap metric treats "agent" (28 entries) the same as "absolute" (1 entry). The discrimination data shows 76% of keywords appear in ≤2 entries, meaning most keywords are already discriminating. The problem is the 20 high-frequency keywords that inflate false relevance matches.

4. **Content word minimum (2) is correctly calibrated** — it's a floor, and only 5 entries sit at it. No change needed.
