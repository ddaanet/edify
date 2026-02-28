# Deliverable Review: flatten-hook-tiers

**Date:** 2026-02-28
**Methodology:** agents/decisions/deliverable-review.md
**Conformance baseline:** plans/flatten-hook-tiers/requirements.md (no design.md — Tier 2 task, design skipped)

## Inventory

| Type | File | + | - | Net |
|------|------|---|---|-----|
| Code | agent-core/hooks/userpromptsubmit-shortcuts.py | +25 | -52 | -27 |
| Test | tests/test_userpromptsubmit_scanning.py | +60 | -0 | +60 |
| Test | tests/test_userpromptsubmit_shortcuts.py | +159 | -0 | +159 |
| **Total** | **3 files** | **+244** | **-52** | **+192** |

Layer 1 skipped (< 500 lines). Layer 2 full review performed.

Design conformance: requirements.md specifies 7 FRs + 3 constraints. All 3 deliverables are specified (code refactor + two categories of tests). No unspecified deliverables.

## Critical Findings

None.

## Major Findings

1. **FR-7 AC gap: two combination tests omit systemMessage verification**
   - `tests/test_userpromptsubmit_shortcuts.py:361-367` — `test_command_plus_pattern_guard`: asserts `additionalContext` contains both `[#status]` and `claude-code-guide`, but does not assert `systemMessage` content
   - `tests/test_userpromptsubmit_shortcuts.py:369-380` — `test_command_plus_continuation`: asserts `additionalContext` contains both `[#status]` and `CONTINUATION`, but does not assert `systemMessage` content
   - **Axis violated:** Coverage (Test)
   - **Requirement:** FR-7 AC explicitly states "Each test verifies both additionalContext content and systemMessage content"
   - **Impact:** These tests would pass even if the systemMessage assembly regressed for these combinations. The command in multi-line mode does NOT add to system_parts (by design — FR-2), so for `test_command_plus_pattern_guard` the systemMessage should contain the CCG guard summary only. For `test_command_plus_continuation`, systemMessage should be absent (continuation adds nothing to system_parts, multi-line command adds nothing).
   - **Severity rationale:** Major not critical — the underlying behavior is correct (verified by reading the code), but the test coverage gap means a future regression could pass undetected

## Minor Findings

**Documentation:**
- Module docstring (`agent-core/hooks/userpromptsubmit-shortcuts.py:2-13`) lists Tier 1, Tier 2, Tier 2.5 but omits Tier 3 (continuation parsing). The inline comment at line 927 documents it, but the module-level overview is incomplete.

**Test structure:**
- `call_hook()` helper is duplicated identically in both test files (scanning:24-51, shortcuts:24-54). Could be extracted to a shared `conftest.py` fixture. Low priority — the duplication is small and both files already import the hook module independently.

**Test naming:**
- `test_tier1_shortcut_on_own_line_in_multiline_prompt` covers FR-2's third AC ("command + plain text, no other feature match → no systemMessage") but the test name doesn't signal FR-2 traceability. Coverage present, naming informational only. (Also noted in corrector review.)

## Gap Analysis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Parallel feature detection | Covered | `main()`:877-934 — accumulator lists, all 4 blocks run unconditionally, no early returns |
| FR-2: Commands accumulate with other features | Covered | Lines 882-900; `test_command_cofires_with_directive`, `test_tier1_shortcut_on_own_line_in_multiline_prompt` |
| FR-3: First command wins, multi-command warning | Covered | Lines 890-900; `test_multi_command_first_wins`, `test_multi_command_reverse_order`, `test_single_command_no_warning` |
| FR-4: Directive + continuation co-firing | Covered | Lines 902-934 (no directive early-return block); `test_directive_cofires_with_continuation` |
| FR-5: Unified output assembly | Covered | Lines 936-951 — single print point; `"\n\n".join(context_parts)`, `" \| ".join(system_parts)` |
| FR-6: Characterization tests | Covered | All 10 commands: s, x, xc, r, h, hc, ci, c, y, ?. All 5 directives: d, p, b, q, learn. All 3 pattern guards. Continuation. No-match. |
| FR-7: Combination tests | **Partial** | 5 combinations tested (cmd+dir, cmd+guard, cmd+cont, dir+cont, cmd+dir+guard). 2 of 5 miss systemMessage assertion (Major #1) |
| C-1: Hook timeout budget | Covered | Control flow change only; no algorithmic additions |
| C-2: Output format stability | Covered | JSON structure unchanged; same keys, same assembly format |
| C-3: Single-feature backward compatibility | Covered | `test_tier1_shortcut_exact_match_unchanged`, directive characterization tests, pattern guard isolation tests |

## Summary

- **Critical:** 0
- **Major:** 1 (FR-7 systemMessage coverage gap in 2 tests)
- **Minor:** 3 (docstring, test duplication, test naming)

The refactor is functionally correct. The accumulator pattern cleanly replaces 3 early-return blocks with parallel detection. The corrector review (pre-existing `reports/review.md`) caught and fixed the more impactful FR-6 gap and dead code issues. The remaining Major finding is a test coverage gap, not a behavioral defect.
