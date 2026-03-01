# Review: UPS Topic Injection — Phase 1 (Cycles 1.1–1.5)

**Scope**: topic_matcher.py (new), index_parser.py (API promotion + frozenset), resolver.py (API promotion), unit tests
**Baseline**: 81604e0e
**Date**: 2026-03-01
**Mode**: review + fix

## Summary

Phase 1 implements the matching pipeline (build_inverted_index, get_candidates, score_and_rank, resolve_entries, format_output) and promotes two private APIs to public. The core logic is correct and the inverted index approach matches D-2. One design compliance defect: extras are discarded at parse time in index_parser.py, making D-7's `trigger | extras` system message format unachievable. Fix: store extras in IndexEntry.description for new-format entries, then reconstruct in format_output. Secondary issues: trivial docstrings, and the parametrized test structure obscures per-case coverage.

**Overall Assessment**: Ready (all issues fixed)

---

## Issues Found

### Critical Issues

None.

### Major Issues

1. **D-7 system message format: trigger extras discarded at parse time**
   - Location: `src/claudeutils/recall/index_parser.py:115`, `src/claudeutils/recall/topic_matcher.py:165`
   - Problem: D-7 requires system message entries in format `"trigger | extras"` (full line minus `/when` prefix). `_parse_new_format_line` sets `description=""` and discards extras. `format_output` can only emit `entry.key` (trigger only). For entries with extras (e.g., `/when using session start hooks | startup, init`), the system message drops the extras, making it less informative and breaking the scraping contract in D-7.
   - Fix: Store extras in `IndexEntry.description` for new-format entries. Update `format_output` to emit `key | description` when description is non-empty.
   - **Status**: FIXED

### Minor Issues

1. **Trivial docstrings in topic_matcher.py restate Args/Returns without adding value**
   - Location: `src/claudeutils/recall/topic_matcher.py:21–34`, `37–57`, `60–85`
   - Note: `build_inverted_index`, `get_candidates`, and `score_and_rank` have full Args/Returns blocks that restate the type annotations. The non-obvious behavior (e.g., union semantics in get_candidates, threshold+cap semantics in score_and_rank) is already captured in the docstring first line. The Args/Returns sections add noise.
   - **Status**: FIXED

2. **`test_resolve_entries` parametrize anti-pattern: if/elif dispatch inside test body**
   - Location: `tests/test_recall_topic_matcher.py:184–270`
   - Note: Three logically distinct test cases (happy path, missing file, missing section) share one test body with `if/elif` dispatch on the `setup_case` string. This makes coverage non-obvious, makes failure messages ambiguous (just shows parameter value), and couples unrelated setups. Separate test functions with descriptive names are clearer.
   - **Status**: FIXED

3. **`format_output` docstring restates structure**
   - Location: `src/claudeutils/recall/topic_matcher.py:143–156`
   - Note: Args/Returns blocks restate type annotations with no additional behavioral context.
   - **Status**: FIXED

---

## Fixes Applied

- `src/claudeutils/recall/index_parser.py:115` — Store extras in `description` for new-format entries (was hardcoded `""`)
- `src/claudeutils/recall/topic_matcher.py:165` — Reconstruct `trigger | extras` in `format_output` when description is non-empty
- `src/claudeutils/recall/topic_matcher.py:21–85` — Remove trivial Args/Returns blocks from `build_inverted_index`, `get_candidates`, `score_and_rank`
- `src/claudeutils/recall/topic_matcher.py:143–156` — Remove trivial Args/Returns from `format_output`
- `tests/test_recall_topic_matcher.py:184–270` — Split parametrized `test_resolve_entries` into three separate test functions
- `tests/test_recall_integration.py:188–190` — Update stale `description == ""` assertion to verify extras are stored in description

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Parse memory-index into keyword lookup (inverted index) | Satisfied | `build_inverted_index()` at topic_matcher.py:21 |
| FR-2: Match prompt against keyword table, rank by score | Satisfied | `get_candidates()` + `score_and_rank()` with D-1 formula via `score_relevance()` |
| FR-3: Resolve matched entries to decision file content, silent skip on miss | Satisfied | `resolve_entries()` at topic_matcher.py:94; OSError caught in `extract_section` |
| FR-6: Entry count cap (max 3) | Satisfied | `max_entries` param in `score_and_rank()`, default `None` (callers must pass 3) |
| FR-7: systemMessage with matched trigger lines + count header | Partial | Format exists but extras dropped (fixed by major issue above) |

**FR-6 note**: The cap is implemented as a parameter with default `None`. The design says "start with 3" — the default should arguably be 3, not None. However, the design also says "calibrate empirically" and caching is Phase 2 — so leaving the default to the hook integration layer is reasonable. Not flagged as an issue given Phase 3 scope.

---

## Positive Observations

- `get_candidates` correctly uses union semantics (set update) — any keyword overlap triggers candidacy, scoring then filters by threshold
- `resolve_entries` correctly implements D-5 try-both-headings (`## When X`, `## How to X`) via `_capitalize_heading`
- `_capitalize_heading` preserves all-caps acronyms, consistent with `_build_heading` in resolver.py
- `frozenset` change on `IndexEntry.keywords` enables hashability (required for `set[IndexEntry]` in `get_candidates`)
- `frozen=True` pydantic config correctly makes `IndexEntry` hashable
- Both private API promotions (`extract_keywords`, `extract_section`) correctly updated all internal callers — no dangling `_` references remain
- Test coverage spans all five pipeline functions with meaningful behavioral assertions

## Recommendations

- Phase 3 hook integration: pass `max_entries=3` explicitly when calling `score_and_rank` to enforce the D-6 cap
- The `format_output` extras reconstruction (this fix) makes the system message format stable for D-10 calibration scraping
