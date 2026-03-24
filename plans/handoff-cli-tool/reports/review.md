# Review: handoff-cli-tool RC7 fixes

**Scope**: RC7 minor finding fixes across 6 test files (m-1..m-6)
**Date**: 2026-03-24
**Mode**: review + fix

## Summary

All 6 RC7 minor findings have been correctly applied. The fixes cover: vacuous assertion replacement, parametrized test collapse, import alignment, new combination test, and two assertion string pins. Each fix matches its requirement exactly. No issues found.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

All 6 fixes were pre-applied before this review. No edits required.

- `tests/test_session_commit_format.py:21` — m-1: vacuous `assert A or B` replaced with `output.split("\n")[0].startswith("[")` (VERIFIED)
- `tests/test_session_commit.py:50-67` — m-2: 4 single-field parametrized cases collapsed to one test asserting all fields from shared fixture (VERIFIED)
- `tests/test_status_rework.py:11` — m-3: `from claudeutils.session.parse import ParsedTask` aligns import to S-4 public interface (VERIFIED)
- `tests/test_session_commit_validation.py:259-291` — m-4: `test_commit_just_lint_no_vet` added; asserts precommit not called, lint called once, vet not called (VERIFIED)
- `tests/test_git_cli.py:83` — m-5: `"Tree is clean." in result.output` pins to actual emitted string (VERIFIED)
- `tests/test_session_handoff_cli.py:90` — m-6: `"**Git status:**" in result.output` pins to markdown-formatted string (VERIFIED)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| m-1: Vacuous disjunction removed | Satisfied | test_session_commit_format.py:21 |
| m-2: Parametrize collapsed to single combined assertion test | Satisfied | test_session_commit.py:50-67 |
| m-3: Import aligned to claudeutils.session.parse | Satisfied | test_status_rework.py:11 |
| m-4: test_commit_just_lint_no_vet added | Satisfied | test_session_commit_validation.py:259-291 |
| m-5: Assertion pinned to "Tree is clean." | Satisfied | test_git_cli.py:83 |
| m-6: Assertion pinned to "**Git status:**" | Satisfied | test_session_handoff_cli.py:90 |

---

## Positive Observations

- m-2 collapsed test is stronger than the original: asserts all fields (files, options, submodule dict key and message body, parent message and body) in one parse from the shared fixture, vs. one field per case in the parametrized form
- m-4 test structure mirrors `test_commit_just_lint` exactly, making the combination-option coverage immediately legible by comparison
- All docstring summaries comply with the ≤70-char content constraint (m-2: 64 chars, m-4: 43 chars)
- m-1 replacement is more specific than a substring check: verifies the first-line prefix character (`[`), making the "no label prefix" intent explicit in the assertion itself
- m-5 and m-6 pins surface the actual emitted strings in the assertion, removing the case-folding and substring indirection that masked the exact contract
