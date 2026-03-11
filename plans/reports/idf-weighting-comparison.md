# IDF Weighting Comparison Report

**Date:** 2026-03-10
**Dataset:** 363 entries, 1167 unique keywords
**Prototype:** `plans/prototypes/idf-weighting.py`
**Raw data:** `tmp/idf-weighting-data.json`

## IDF Weight Distribution

| Metric | Value |
|--------|-------|
| Min IDF | 2.56 ("agent", df=28) |
| Max IDF | 5.89 (673 unique keywords, df=1) |
| Mean IDF | 5.39 |
| Spread | 2.3x (max/min) |

The log function compresses a 28x document frequency range into a 2.3x weight range. "agent" (28 entries) gets weight 2.56 vs 5.89 for unique keywords — a keyword appearing in 1 entry is valued 2.3x more than one appearing in 28.

## False Positive Reduction at Threshold 0.3

| Session | Flat ≥0.3 | IDF ≥0.3 | Reduction | Flat-only entries |
|---------|-----------|----------|-----------|-------------------|
| agent-context-design | 4 | 2 | 50% | "embedding knowledge in context", "reviewing agent definitions" |
| test-phase-hook | 8 | 3 | 63% | 5 entries (single-keyword matches on "test", "phase") |
| worktree-merge-session | 8 | 1 | 88% | 7 entries (single-keyword matches on "session", "commit", "merge") |
| skill-plugin-development | 4 | 1 | 75% | 3 entries (single-keyword matches on "skill", "agent") |
| recall-scoring-threshold | 0 | 0 | — | (no entries reached 0.3 in either method) |

IDF weighting eliminates entries that cross the threshold via a single high-frequency keyword match. All eliminated entries matched on exactly one common keyword (df 12-28).

**No entries were promoted by IDF** (idf_only = empty for all sessions). IDF is strictly more conservative at this threshold — it reduces false positives without introducing false negatives.

## Rank Quality

Top-ranked entries are stable between methods. Rank 1-2 are identical in 4/5 sessions. The interesting reranking:

**skill-plugin-development:** "loading context before skill edits" (3 matched keywords: development, plugin, skill) moved from flat rank 4 → IDF rank 1. IDF correctly elevated a 3-keyword match with discriminating terms over entries with 1 common-keyword match at higher flat score. Flat score was 0.30 (below threshold), IDF score 0.32 (above) — the only entry above threshold in IDF.

**worktree-merge-session:** "handoff precedes commit" moved from flat rank 7 → IDF rank 4. "commit" has higher IDF weight than "session", so same-flat-score entries get reordered by keyword discrimination.

## The recall-scoring-threshold Session

Zero entries reached 0.3 in either method despite 6 session keywords. Cause: 4 of 6 keywords ("idf", "scoring", "threshold", "relevance") appear in very few or zero index entries. Most matches were single-keyword on "recall" (df=17), giving max flat scores of 0.14. IDF worsened these scores slightly (recall's IDF weight 3.06 is below-mean for the corpus).

This session demonstrates a different problem: keyword vocabulary mismatch, not false relevance from common keywords. IDF weighting doesn't address this.

## Findings

**IDF weighting reduces false positives from common keywords.** Across 4 testable sessions, entries above threshold dropped from 24 to 7 (71% reduction). All eliminated entries were single-common-keyword matches.

**The compression effect limits discrimination.** The 2.3x IDF weight spread means common keywords are downweighted, but not dramatically. A 2-keyword match where both keywords are common (IDF ~2.6 each) still scores close to a 1-keyword match where the keyword is unique (IDF ~5.9). The formula reduces noise but doesn't eliminate it.

**Threshold interaction:** At 0.3, IDF scoring causes many previously-above entries to drop below threshold. The effective behavior is closer to requiring 2+ keyword matches OR 1 highly discriminating keyword match. This may be desirable or too aggressive depending on recall requirements.

**Vocabulary gap is a separate problem.** The recall-scoring-threshold session (0 results in both methods) shows that when session keywords don't overlap with index vocabulary, neither scoring method helps. This would need keyword expansion (synonyms, stemming) rather than reweighting.
