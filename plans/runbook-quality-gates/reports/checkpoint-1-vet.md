# Vet Review: Phase 1 Checkpoint — model-tags subcommand

**Scope**: `agent-core/bin/validate-runbook.py`, `tests/test_validate_runbook.py`, `plans/runbook-quality-gates/reports/execution-report.md`
**Date**: 2026-02-17
**Mode**: review + fix

## Summary

Phase 1 implements the `validate-runbook.py` script scaffold and the `model-tags` subcommand via 3 TDD cycles. All 3 tests pass. The implementation is clean and correctly uses `importlib` to pull functions from `prepare-runbook.py` per D-7. Two minor issues found: a narration comment and a test isolation gap with direct `sys.argv` mutation.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Narration comment in `_is_artifact_path`**
   - Location: `agent-core/bin/validate-runbook.py:31`
   - Note: `# agents/decisions/workflow-*.md` restates what the regex immediately below it already expresses. The regex is self-explanatory.
   - **Status**: FIXED

2. **`sys.argv` mutated directly in tests**
   - Location: `tests/test_validate_runbook.py:109,133`
   - Note: Tests assign `sys.argv = [...]` directly rather than via `monkeypatch.setattr(sys, "argv", [...])`. If test isolation fails (e.g., a future test runner uses threads), mutation is not cleaned up. `monkeypatch` restores state automatically.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/validate-runbook.py:31` — Removed `# agents/decisions/workflow-*.md` narration comment
- `tests/test_validate_runbook.py:109` — Replaced `sys.argv = [...]` with `monkeypatch.setattr(sys, "argv", [...])`
- `tests/test_validate_runbook.py:133` — Replaced `sys.argv = [...]` with `monkeypatch.setattr(sys, "argv", [...])`

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-2 (mechanical): artifact files must use opus | Satisfied | `check_model_tags` + `_is_artifact_path` correctly identify artifact paths and flag non-opus model |
| D-7: subcommand architecture, importlib imports | Satisfied | 4 subcommands registered; 6 functions imported via `importlib.util` at module top |
| Exit 0 = pass, 1 = violations | Satisfied | `cmd_model_tags` exits 1 on violations, 0 otherwise |

---

## Positive Observations

- `_is_artifact_path` cleanly separates path classification from violation logic — makes it testable and extensible
- `write_report` correctly uses `p.stem` for files and `p.parent.name` for directories — the path-to-job derivation is correct for both invocation modes
- Stub handlers use correct `argparse.Namespace` signature — ready for future phases without refactoring
- `monkeypatch.chdir(tmp_path)` correctly isolates report path generation from the real project tree
- Violation message format (`**Expected:** opus, got: haiku`) matches test assertion precisely — RED→GREEN flow was disciplined
