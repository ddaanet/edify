### Cycle 1.2: Assembly preserves existing phase headers 2026-02-22

- Status: GREEN_VERIFIED
- Test command: `just test tests/test_prepare_runbook_mixed.py::TestPhaseNumbering::test_assembly_preserves_existing_phase_headers -v`
- RED result: FAIL as expected — `assert 2 == 1` (duplicate `### Phase 1:` lines)
- GREEN result: PASS — guard regex `^###? Phase\s+N:` skips injection when header already present
- Regression check: 9/9 passed (TestPhaseNumbering 2/2, test_prepare_runbook_inline.py 7/7), 1144/1145 full suite (1 xfail pre-existing)
- Refactoring: docstring rewritten to avoid D400 lint issue (formatter split inline `### Phase N:` across lines)
- Files modified:
  - `tests/test_prepare_runbook_mixed.py` (added test_assembly_preserves_existing_phase_headers)
  - `agent-core/bin/prepare-runbook.py` (guard condition on header injection)
- Stop condition: none
- Decision made: none
