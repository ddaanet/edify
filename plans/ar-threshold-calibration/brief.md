# Problem: Calibrate Active Recall Validation Thresholds

## Context

The active recall system uses several numeric thresholds for relevance scoring and entry validation. Current values are either hardcoded defaults (0.3 keyword overlap) or ungrounded magic numbers (50.0 fuzzy match). Per the no-confabulation rule, these need empirical calibration against the actual dataset.

## Current Thresholds

Five thresholds govern recall quality:

1. **Keyword overlap %** (`src/edify/recall/relevance.py:22`) — 0.3 default. Fraction of entry keywords matching session keywords. Controls which entries surface as "relevant."

2. **Fuzzy match threshold** (`src/edify/validation/memory_index.py:127`, `memory_index_checks.py:222`) — 50.0. Score threshold for matching index entry keys to semantic headers. Controls orphan detection and collision checking.

3. **Keyword count** — No explicit threshold. `extract_keywords()` in `index_parser.py` produces variable-size keyword sets per entry. Entries with very few or very many keywords behave differently in overlap scoring (1-keyword entry: binary match; 20-keyword entry: diluted signal).

4. **Content words** (`src/edify/validation/learnings.py:147`) — Minimum 2 content words after prefix in decision headings. Controls specificity floor for trigger titles.

5. **Discriminating keyword count** — No explicit threshold. Some keywords appear in many entries (low discrimination), others in few (high discrimination). Overlap scoring treats all keywords equally, but discrimination power varies.

## Dataset

- `agents/memory-index.md`: 366 entries across multiple decision files
- Each entry has: key, description, referenced file, section, extracted keywords (via `extract_keywords()`)

## Problem Statement

Calibrate all 5 thresholds empirically:
- Measure actual distributions across the 366-entry dataset
- Identify natural breakpoints (clusters, gaps, inflection points)
- Set thresholds at empirically justified values
- Make thresholds user-configurable with calibrated defaults
- Design feedback pipeline for ongoing calibration as the dataset grows

## Human Judgment Requirements

Two validation dimensions require labeled data:
- **Duplicate detection**: "Is this entry truly a duplicate of that entry?" — needed to calibrate fuzzy match and keyword overlap thresholds
- **Specificity assessment**: "Is this trigger over-specific or under-specific?" — needed to calibrate content word and keyword count thresholds

## Scope

This is calibration infrastructure for the existing recall system. It does not change the recall architecture (FR-1 through FR-11 in active-recall requirements). It grounds the numeric parameters that the architecture relies on.

## References

- `src/edify/recall/relevance.py` — relevance scoring
- `src/edify/recall/index_parser.py` — keyword extraction, IndexEntry model
- `src/edify/validation/memory_index.py` — index validation with fuzzy matching
- `src/edify/validation/memory_index_checks.py` — collision and duplicate checks
- `src/edify/validation/learnings.py` — content word validation
- `plans/active-recall/requirements.md` — parent system requirements
