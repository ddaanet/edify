# Review: Cycle 4.2 Test Quality

**Scope**: tests/test_session_handoff.py — new tests: test_overwrite_status_line, test_overwrite_status_line_idempotent
**Date**: 2026-03-16T16:41:29Z
**Mode**: review + fix

## Summary

Two tests were added for `overwrite_status` (Cycle 4.2 RED phase), but `pipeline.py` already contains a complete implementation of `overwrite_status`. Both tests pass immediately, violating the RED phase requirement. Additionally, the spec requires `test_overwrite_status_line_multiline` but the implementation provides `test_overwrite_status_line_idempotent` instead — the idempotent test is a reasonable behavioral check but the multiline case from the spec is absent. A section banner comment was also introduced.

**Overall Assessment**: Needs Significant Changes (one UNFIXABLE — see Critical Issues)

## Issues Found

### Critical Issues

1. **RED phase not red — implementation already exists**
   - Location: `src/claudeutils/session/handoff/pipeline.py:9-38`, tests both pass immediately
   - Problem: `overwrite_status` is fully implemented in `pipeline.py`. The TDD RED phase requires tests to fail with `AttributeError` (function doesn't exist) before implementation. Both tests pass on the first run, skipping the RED→GREEN cycle entirely.
   - Fix: Remove `overwrite_status` from `pipeline.py` before committing the RED test step. Implementation belongs in the GREEN step.
   - **Status**: UNFIXABLE (U-ARCH)
   - **Investigation:**
     1. Scope OUT: not listed
     2. Design deferral: not found
     3. Codebase patterns: no pattern for retroactively removing implementation within a TDD cycle
     4. Conclusion: The corrector cannot delete the implementation — that would break the GREEN phase if it has already been committed or is part of the same commit. The orchestrator must decide whether to delete the implementation from `pipeline.py` before the RED commit lands, or to accept that RED was skipped and proceed. This is a sequencing decision (which commit carries the implementation), not a test content fix.

### Major Issues

1. **Missing test_overwrite_status_line_multiline**
   - Location: step spec line 21 and 28; `tests/test_session_handoff.py` (absent)
   - Problem: Spec explicitly names `test_overwrite_status_line_multiline` and specifies the assertion: "When status text has multiple lines, each line preserved between heading and first `##`". The test `test_overwrite_status_line_idempotent` was added instead. The idempotent behavior (no-append on double call) is valuable but is not a substitute for the multiline assertion.
   - Fix: Add `test_overwrite_status_line_multiline` with a multiline status text and assert all lines appear between the heading and the first `##` section.
   - **Status**: FIXED

### Minor Issues

1. **Section banner comment**
   - Location: `tests/test_session_handoff.py:27` — `# --- Cycle 4.1: parse handoff stdin ---` and `tests/test_session_handoff.py:59` — `# --- Cycle 4.2: status line overwrite ---`
   - Note: Section banner comments with `---` decorators are narration comments (restating structure visible from test names). Project code quality rules prohibit them.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_session_handoff.py:27,59` — Removed `# --- Cycle 4.1 ---` and `# --- Cycle 4.2 ---` banner comments; replaced with plain comments without decorators.
- `tests/test_session_handoff.py` — Added `test_overwrite_status_line_multiline` covering multiline status text with preservation assertion and section boundary check.

## Positive Observations

- `test_overwrite_status_line` correctly checks both the presence of new text and absence of old text — not just a presence check.
- `test_overwrite_status_line_idempotent` adds `content.count("**Status:**") == 1` which is the strongest form of the no-append assertion (count, not just absence of first value).
- Fixture `SESSION_FIXTURE` includes multiple sections (`## Completed This Session`, `## In-tree Tasks`), making the "other sections preserved" assertions meaningful.
- Import of `overwrite_status` from the correct module path (`handoff.pipeline`) is consistent with the package structure established in Cycle 4.1.
