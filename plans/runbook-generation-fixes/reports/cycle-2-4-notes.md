### Cycle 2.4: Agent frontmatter uses detected model 2026-02-22
- Status: GREEN_VERIFIED
- Test command: `just test tests/test_prepare_runbook_mixed.py::TestModelPropagation::test_assembly_frontmatter_uses_detected_model -v`
- RED result: FAIL as expected — `assert 'haiku' == 'sonnet'` (hardcoded haiku in frontmatter)
- GREEN result: PASS
- Regression check: 14/14 passed (test_prepare_runbook_mixed.py + test_prepare_runbook_inline.py)
- Refactoring: none (precommit passed with no warnings)
- Files modified: `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_mixed.py`
- Stop condition: none
- Decision made: After `assembled_body` construction, call `extract_phase_models()` and use first phase's model (lowest phase number). Falls back to `haiku` only if no phases declare a model (will be caught by 2.5 validation).
