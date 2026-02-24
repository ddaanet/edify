# Deliverable Review: when-resolve-fix

**Date:** 2026-02-24
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | +/- | Net |
|------|------|-----|-----|
| Code | src/claudeutils/when/resolver.py | +39/-9 | +30 |
| Test | tests/test_when_resolver.py | +76/-0 | +76 |
| **Total** | **2 files** | **+115/-9** | **+106** |

**Design conformance:** All spec requirements covered. No design.md — problem.md serves as spec (single-function scope).

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**M1 — No explicit score threshold on fuzzy fallback** (resolver.py:315)
- Axis: robustness
- `_find_heading` accepts the top `rank_matches` result without a minimum score check. Relies on `fuzzy.rank_matches` internal filtering (scores > 0.0 only). For heading-length strings, false positive risk is negligible. Consistent with the existing trigger resolution pattern at resolver.py:220 which uses the identical `rank_matches(query, candidates, limit=1)` pattern without threshold.
- Severity rationale: theoretical edge case, no practical risk demonstrated, consistent with existing codebase pattern.

## Gap Analysis

| Spec Requirement | Status | Reference |
|-----------------|--------|-----------|
| Replace exact heading scan with fuzzy matching | Covered | resolver.py:288-323 `_find_heading()` |
| Exact match tried first, fuzzy as fallback | Covered | resolver.py:305-306 exact, 312-319 fuzzy |
| Reuse existing `fuzzy.rank_matches` | Covered | resolver.py:315 |
| Test coverage for fuzzy fallback | Covered | test_when_resolver.py:118-191 (2 tests) |
| `/when` operator tested | Covered | test_when_resolver.py:118-160 |
| `/how` operator tested | Covered | test_when_resolver.py:162-191 (unspecified, justified) |

## Summary

- Critical: 0
- Major: 0
- Minor: 1
