# Cycle 1.1: Parse `/when trigger | extras` format

**Timestamp:** 2026-02-12 22:58 UTC

## Execution Summary

| Phase | Status | Result |
|-------|--------|--------|
| RED | VERIFIED | Test failed as expected — ModuleNotFoundError |
| GREEN | VERIFIED | Test passed, no regressions (764/765 passed) |
| REFACTOR | COMPLETED | Lint passed, precommit passed |

## Details

### RED Phase

**Test Command:** `pytest tests/test_when_index_parser.py::test_parse_when_entry_basic -v`

**Expected Failure:** `ModuleNotFoundError: No module named 'claudeutils.when.index_parser'`

**Actual Result:** FAIL ✓
```
ModuleNotFoundError: No module named 'claudeutils.when.index_parser'
```

RED phase verified: Test fails before implementation.

### GREEN Phase

**Implementation:**
- Created `src/claudeutils/when/index_parser.py` with:
  - `WhenEntry(BaseModel)` — Pydantic model with fields: operator, trigger, extra_triggers, line_number, section
  - `parse_index(index_path)` — Parses index file line-by-line, tracks H2 section context, identifies `/when` and `/how` lines, splits on `|` for trigger and extras

**Test Result:** PASS ✓
```
tests/test_when_index_parser.py::test_parse_when_entry_basic PASSED
```

**Regression Check:** All tests pass (764/765 with 1 expected xfail)
```
Summary: 764/765 passed, 1 xfail
```

### REFACTOR Phase

**Linting Issues Fixed:**
- Added module docstring: `"""Parse /when and /how format entries from index files."""`
- Added module docstring to test file: `"""Tests for index_parser module."""`
- Added type annotation: `tmp_path: Path` in test function signature
- Added import: `from pathlib import Path`

**Quality Check:**
```
just precommit: PASS ✓
just lint: PASS ✓
```

## Files Modified

- `src/claudeutils/when/index_parser.py` — Created
- `tests/test_when_index_parser.py` — Created

## Architecture Decisions

**None** — Implementation follows design specification exactly. Pydantic BaseModel pattern matches project conventions (per implementation-notes.md). Line-by-line parsing with H2 section tracking aligns with design requirements.

## Stop Conditions

**None** — Cycle completed successfully. No UNFIXABLE issues, no architectural blockers.

## Commit

```
3b94345 WIP: Cycle 1.1 Parse `/when trigger | extras` format
```

Tree is clean. Commit contains both source changes (index_parser.py, test_when_index_parser.py) and this execution report.
