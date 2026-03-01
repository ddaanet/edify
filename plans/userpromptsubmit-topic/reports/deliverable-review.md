# Deliverable Review: userpromptsubmit-topic

**Date:** 2026-03-01
**Methodology:** agents/decisions/deliverable-review.md
**Conformance baseline:** plans/userpromptsubmit-topic/outline.md + plans/userpromptsubmit-topic/requirements.md (no design.md — Moderate classification routed directly to runbook)

## Inventory

| Type | File | Lines (+/-) |
|------|------|-------------|
| Code | src/claudeutils/recall/topic_matcher.py | +299 (new) |
| Code | agent-core/hooks/userpromptsubmit-shortcuts.py | +21 |
| Code | src/claudeutils/recall/index_parser.py | +10/-5 |
| Code | src/claudeutils/when/resolver.py | +3/-3 |
| Test | tests/test_recall_topic_matcher.py | +313 (new) |
| Test | tests/test_ups_topic_integration.py | +166 (new) |
| Test | tests/test_recall_topic_cache.py | +94 (new) |
| Test | tests/test_recall_calculation.py | +4/-4 |
| Test | tests/test_recall_index_parser.py | +1/-1 |
| Test | tests/test_recall_integration.py | +4/-8 |
| Test | tests/test_recall_relevance.py | +12/-12 |

**Not this plan (same branch, inline-tdd-dispatch):** `agents/decisions/orchestration-execution.md` (+4), `agent-core/skills/inline/SKILL.md` (+3/-1). Excluded from review.

**Design conformance:** All 7 FRs implemented. All specified deliverable files produced. Test suite: 14/14 pass, full suite 1378/1379 (1 xfail unrelated).

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**M-1: get_or_build_index missing precondition guard** (robustness)
- `topic_matcher.py:261`: Public API sets `source_mtime=0.0` for non-existent `index_path`, then proceeds to `parse_memory_index(index_path)` which may raise `FileNotFoundError`. The hook caller checks `index_path.exists()` before calling `match_topics`, but the function's contract doesn't document or enforce this precondition.
- Fix: Add early return `([], {})` when `not index_path.exists()`, or document the precondition in docstring.

**M-2: _capitalize_heading duplicates resolver logic** (modularity)
- `topic_matcher.py:72-75` and `resolver.py:300-301`: Identical capitalization pattern `w if w.isupper() else w.capitalize()`. Trivial one-liner, so duplication risk is low, but a shared utility in the recall package would prevent future divergence.

**M-3: Loose OR assertion in integration test** (test specificity)
- `test_ups_topic_integration.py:69-72`: `assert "test decision content" in additional_context or "hook" in additional_context.lower()`. The second branch (`"hook"`) matches the hook infrastructure itself, not just topic injection content. Could produce false-positive test passes if topic resolution fails but hook machinery mentions "hook" in its output.
- Fix: Remove the OR branch, use only the specific assertion on the resolved decision content.

## Gap Analysis

| Design Requirement | Status | Reference |
|--------------------|--------|-----------|
| FR-1: Keyword table from memory-index | Covered | `topic_matcher.py:build_inverted_index()` |
| FR-2: Prompt matching and ranking | Covered | `topic_matcher.py:get_candidates()`, `score_and_rank()` |
| FR-3: Content resolution + additionalContext | Covered | `topic_matcher.py:resolve_entries()`, `format_output()` |
| FR-4: Cache with mtime invalidation | Covered | `topic_matcher.py:get_or_build_index()`, cache read/write |
| FR-5: Hook integration (parallel detector) | Covered | `userpromptsubmit-shortcuts.py:935-949` (Tier 2.75) |
| FR-6: Entry count cap | Covered | `match_topics(max_entries=3)` |
| FR-7: systemMessage trigger feedback | Covered | `format_output()` dual-channel output |
| D-1: Entry coverage scoring | Covered | `score_relevance("hook", ...)` with threshold=0.3 |
| D-2: Inverted index candidates | Covered | `build_inverted_index()` + `get_candidates()` |
| D-3: Additive with all features | Covered | Appends to `context_parts`/`system_parts` accumulators |
| D-4: Cache in project tmp/ | Covered | `tmp/topic-index-{hash}.json` with mtime check |
| D-5: Section extraction via heading | Covered | `resolve_entries()` tries When/How patterns |
| D-6: Cap at 3 entries | Covered | `max_entries=3` default |
| D-7: Dual-channel output format | Covered | `TopicMatchResult.context` + `.system_message` |
| Unit tests | Covered | `test_recall_topic_matcher.py` (8 tests) |
| Integration tests | Covered | `test_ups_topic_integration.py` (3 tests) |
| Cache tests (unspecified) | Justified | `test_recall_topic_cache.py` (3 tests, FR-4 depth) |

**Missing deliverables:** None.
**Unspecified deliverables:** `test_recall_topic_cache.py` — justified (FR-4 test depth). API promotions (`extract_keywords`, `extract_section`) — noted in design as needed.

## Cross-Cutting Verification

- **Path consistency:** All module paths match between outline, requirements, and implementation ✓
- **API contract alignment:** `topic_matcher` → `index_parser` (extract_keywords, IndexEntry), `relevance` (score_relevance), `resolver` (extract_section) — all imports verified, signatures compatible ✓
- **frozenset migration:** IndexEntry.keywords `set[str]` → `frozenset[str]` + `Config.frozen=True` — enables set operations in `get_candidates`. All 7 existing test files updated consistently ✓
- **Naming conventions:** snake_case functions, PascalCase dataclasses, consistent with recall/ package ✓
- **Hook integration pattern:** Matches Tier 2/2.5/3 accumulator pattern. Import with fallback (`try/except ImportError`). Silent failure (`except Exception: pass`) per FR-3 requirement ✓
- **Heading matching:** `extract_section` → `_heading_matches` is case-insensitive. `_capitalize_heading` cosmetic only ✓
- **Cache deduplication:** Inverted index stores entries under multiple keywords; deserialized entries are structurally equal. `frozen=True` provides `__hash__` for set deduplication in `get_candidates` ✓
- **Recall context alignment:** Design matches recalled decisions (embedding knowledge in context, hook output channels, memory-index trigger format) ✓

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 3 |
