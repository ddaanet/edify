### Cycle 2.5: Missing model produces error (no haiku default) 2026-02-22
- Status: GREEN_VERIFIED
- Test command: `pytest tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_missing_model_produces_error -v`
- RED result: FAIL as expected — `validate_and_create()` returned True, silently using haiku
- GREEN result: PASS
- Regression check: 15/15 passed (test_prepare_runbook_mixed.py + test_prepare_runbook_inline.py)
- Refactoring: Extracted `_run_validate()` helper (3 callers) to reduce test boilerplate; removed what-comments; compressed position check in test_assembly_injects; removed unused `got` variable
- Files modified: `tests/test_prepare_runbook_mixed.py`, `agent-core/bin/prepare-runbook.py`
- Stop condition: none
- Decision made: none
