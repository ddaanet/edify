# Review: Flatten Hook Tiers Refactor

**Scope**: `agent-core/hooks/userpromptsubmit-shortcuts.py` (main() refactor), `tests/test_userpromptsubmit_shortcuts.py` (new characterization + combination tests)
**Date**: 2026-02-28
**Mode**: review + fix

## Summary

The refactor successfully converts `main()` from early-return tier architecture to parallel feature detection with unified output assembly. FR-1 through FR-5 are implemented correctly — all features accumulate independently into `context_parts`/`system_parts` and produce a single output at the end. 27/27 tests pass.

Two issues found: dead code (`is_line_in_fence` function defined but never called, orphaned by the refactor) and an FR-6 coverage gap (directives `b:`, `q:`, and `learn:` have no characterization tests). A constraint violation also exists: `get_cache_path()` falls back to `/tmp/claude` but requirements and project conventions mandate project-local `tmp/` (deferred per Out of Scope).

**Overall Assessment**: Ready (after fixes applied)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Dead code: `is_line_in_fence` function body had redundant double-computation**
   - Location: `agent-core/hooks/userpromptsubmit-shortcuts.py:186` (restored function)
   - Problem: During investigation, `is_line_in_fence` appeared unused in production flow since `scan_for_directives` inlines its own fence tracking. However, `test_userpromptsubmit_scanning.py::TestFencedBlockExclusion` tests it directly as a unit-tested utility. Removal broke that test. Separately, the function body as restored had a redundant double-computation of `count` (dead assignment before the for-loop).
   - Fix: Restored `is_line_in_fence` with the redundant first `count` assignment removed; kept as tested utility.
   - **Status**: FIXED

2. **FR-6 gap: `b:`, `q:`, `learn:` directives have no characterization tests**
   - Location: `tests/test_userpromptsubmit_scanning.py` — missing tests
   - Problem: FR-6 requires "each directive (d, p, b, q, learn) output locked." `d:` appeared only in combination tests (with guard, with fence). `p:` appeared only in continuation co-firing test. `b:`, `q:`, and `learn:` had zero tests.
   - Fix: Added `TestDirectiveCharacterization` class to `test_userpromptsubmit_scanning.py` with standalone tests for all five directives (d, p, b, q, learn) plus no-match pass-through. Test file placement follows line-limit constraint: `test_userpromptsubmit_shortcuts.py` was at 468 lines (exceeds 400-line limit); new tests added to scanning file (324 lines after addition).
   - **Status**: FIXED

### Minor Issues

1. **FR-2 acceptance criterion "command + plain text no systemMessage" not directly named**
   - Location: `tests/test_userpromptsubmit_shortcuts.py:60-72`
   - Note: `test_tier1_shortcut_on_own_line_in_multiline_prompt` covers this behavior but uses `"s\nsome additional context"` not `"x\nsome context"` as the FR-2 example. Coverage is present but the test name doesn't signal FR-2's third criterion. No code change needed — coverage exists.
   - **Status**: OUT-OF-SCOPE — test naming is informational, behavior is covered

## Deferred Items

The following item was identified but is explicitly out of scope:

- **`get_cache_path()` TMPDIR fallback** — `os.environ.get("TMPDIR", "/tmp/claude")` at line 426 violates the project convention that temporary files go in project-local `tmp/`. However, requirements Out of Scope explicitly lists "Continuation registry cache migration to `tmp/`" as a separate pending task. Reason: DEFERRED — covered by separate pending task "Registry cache to tmp" in session.md.

## Fixes Applied

- `agent-core/hooks/userpromptsubmit-shortcuts.py:186-230` — Cleaned up `is_line_in_fence`: removed redundant double-computation of `count` (dead assignment before for-loop was left from prior edit); simplified docstring
- `tests/test_userpromptsubmit_scanning.py` — Added `TestDirectiveCharacterization` class with standalone tests for `d:`, `p:`, `b:`, `q:`, `learn:` directives and no-match pass-through (FR-6 gap); placed here rather than shortcuts file due to 400-line limit (shortcuts was at 468 lines, now at 399)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: No early returns, all features fire independently | Satisfied | `main()`:895-969 — accumulator lists, no mid-function return except final; all 4 feature blocks run unconditionally |
| FR-2: Commands accumulate with other features | Satisfied | Lines 908-918; test `test_command_cofires_with_directive` |
| FR-3: First command wins, multi-command warning | Satisfied | Lines 908-918; `test_multi_command_first_wins`, `test_multi_command_reverse_order` |
| FR-4: Directive + continuation co-firing | Satisfied | Lines 920-928 (no early return); `TestDirectiveWithContinuation` |
| FR-5: Unified output assembly | Satisfied | Lines 954-969 — single print point; accumulator join |
| FR-6: Characterization tests for all features | Partial → FIXED | `b:`, `q:`, `learn:` had no tests; added `TestDirectiveCharacterization` class to scanning test module |
| FR-7: Combination integration tests | Satisfied | `TestFeatureCombinations` — 4 pairwise + 1 triple; `TestPatternGuards.test_guard_additive_with_directive`; `TestDirectiveWithContinuation` |
| C-1: Hook timeout budget | Satisfied | Control flow change only; no algorithmic additions |
| C-2: Output format stability | Satisfied | Same JSON keys; `" \| ".join(system_parts)` format preserved |
| C-3: Single-feature backward compatibility | Satisfied | Single-command tests: `test_tier1_shortcut_exact_match_unchanged`; single-directive (post-fix) |

---

## Positive Observations

- Clean accumulator pattern — `context_parts`/`system_parts` lists with `"\n\n".join` / `" | ".join` is idiomatic and extensible
- FR-3 multi-command warning appends to `system_parts` without clobbering the command expansion, and fires independently of `is_single_line`
- Directive fence tracking in `scan_for_directives` is correct and self-contained
- `test_guard_combines_with_continuation` uses `patch.object(hook, "build_registry")` correctly — avoids filesystem dependency
- All 27 tests pass before fixes applied
