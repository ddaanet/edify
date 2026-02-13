# Cycle 7.2: Generate candidate triggers (word-drop algorithm)

**Timestamp:** 2026-02-13 00:32 UTC
**Commit:** cac6ef7

## Status

GREEN_VERIFIED

## Test Command

`pytest tests/test_when_compress_key.py::test_generate_candidates -v`

## RED Result

FAIL as expected: `ImportError: cannot import name 'generate_candidates'`

## GREEN Result

PASS: Function implemented and all assertions satisfied

## Regression Check

Full suite: 801/802 passed, 1 xfail (no new failures)

## Refactoring

- Applied formatter (ruff format) — no changes needed by developer
- Fixed import location (moved from function to top-level) per PLC0415 linting rule
- All linting passed

## Files Modified

- `src/claudeutils/when/compress.py` — Added `generate_candidates()` function
- `tests/test_when_compress_key.py` — Added `test_generate_candidates()` test

## Stop Condition

None

## Decision Made

Implemented word-drop algorithm with word combination generation via itertools.combinations. Added singularization support (trailing 's' removal) to generate plural variants of candidates. Candidates sorted by word count ascending for consistent ordering.
