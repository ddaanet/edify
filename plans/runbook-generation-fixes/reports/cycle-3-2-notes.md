# Cycle 3.2 Notes

### Cycle 3.2: step-and-cycle-files-include-phase-context [2026-02-22]
- Status: STOP_CONDITION
- Test command: `pytest tests/test_prepare_runbook_mixed.py::TestPhaseContext::test_step_and_cycle_files_include_phase_context -v`
- RED result: FAIL as expected — AssertionError: Expected '## Phase Context' in cycle file
- GREEN result: PASS (16/16 tests pass including regressions)
- Regression check: 16/16 passed
- Refactoring: none — precommit quality check found warning
- Files modified: `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_mixed.py`
- Stop condition: `tests/test_prepare_runbook_mixed.py` is 478 lines (exceeds 400 line limit)
- Decision made: none

## Quality Warning

`just precommit` reports:
```
❌ tests/test_prepare_runbook_mixed.py:      478 lines (exceeds 400 line limit)
```

The test file grew from 381 lines to 478 lines after adding the `TestPhaseContext` class (97 lines).

## Implementation Summary

GREEN phase changes:
- `generate_step_file()`: added `phase_context=""` param; injects `## Phase Context\n\n{text}\n\n---` between metadata header and body when non-empty
- `generate_cycle_file()`: same pattern with `phase_context=""` param
- `validate_and_create()`: added `phase_preambles=None` param; resolves to `{}` when None; passes `preambles.get(phase, "")` to each generation call
- `main()`: calls `extract_phase_preambles(body)` and passes result to `validate_and_create()`
- `tests/test_prepare_runbook_mixed.py`: added `extract_phase_preambles` import; added `TestPhaseContext` class with test

## Escalation for Line Limit

Test file at 478 lines exceeds 400-line limit. Options for splitting:
- Extract `TestPhaseContext` (97 lines) to `tests/test_prepare_runbook_phase_context.py`
- Or split existing file more coarsely (TestPhaseNumbering + TestModelPropagation into separate files)
