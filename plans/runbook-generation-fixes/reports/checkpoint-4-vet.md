# Vet Review: Phase 4 — Orchestrator Plan Improvements

**Scope**: `agent-core/bin/prepare-runbook.py`, `tests/test_prepare_runbook_orchestrator.py` (Cycles 4.1–4.2)
**Date**: 2026-02-22
**Mode**: review + fix

## Summary

Phase 4 adds `phase_models` and `default_model` parameters to `generate_default_orchestrator()`, generates a `## Phase Models` section in the orchestrator plan, and includes phase file paths in PHASE_BOUNDARY entries. `validate_and_create()` correctly threads these parameters through. The implementation is clean, consistent with Phases 1–3 patterns, and satisfies D-5.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_run_validate` helper redundantly sets `metadata["type"] = "tdd"`**
   - Location: `tests/test_prepare_runbook_orchestrator.py:29`
   - Note: The runbook content passed to `_run_validate` already contains `type: tdd` in frontmatter. `parse_frontmatter` extracts it correctly. The override is harmless but misleading — suggests the frontmatter type is unreliable, which is false.
   - **Status**: FIXED

2. **No test for Phase Models section absent when both `phase_models` and `default_model` are None**
   - Location: `tests/test_prepare_runbook_orchestrator.py`
   - Note: `generate_default_orchestrator(name, cycles=[...], phase_models=None, default_model=None)` should NOT generate a `## Phase Models` section. The condition at line 946 (`if phase_models is not None or default_model is not None`) covers this, but it is untested. In practice, `validate_and_create` always passes `phase_models={}` (not None), so the section is always generated via the main pipeline. The edge case is reachable only by calling `generate_default_orchestrator` directly.
   - **Status**: FIXED

## Fixes Applied

- `tests/test_prepare_runbook_orchestrator.py:29` — Removed redundant `metadata["type"] = "tdd"` override. `parse_frontmatter` extracts `type` from frontmatter; forcing it here implies the extraction is wrong.
- `tests/test_prepare_runbook_orchestrator.py` — Added `test_orchestrator_plan_omits_phase_models_when_no_model_info` to verify `## Phase Models` is absent when both params are None.

## Design Anchoring

| Decision | Status | Evidence |
|----------|--------|----------|
| D-5: PHASE_BOUNDARY entries reference source phase file | Satisfied | `prepare-runbook.py:939-940` — `Phase file: {phase_dir}/runbook-phase-{phase}.md` added to PHASE_BOUNDARY entries |
| Phase Models table (Cycle 4.2) | Satisfied | `prepare-runbook.py:946-952` — `## Phase Models` section with phase-level resolution |
| D-1 model priority chain | Satisfied | `prepare-runbook.py:951` — `resolved.get(p, default_model)` respects phase override then frontmatter fallback |

## Lifecycle Audit

Traced `validate_and_create()` → `generate_default_orchestrator()` → file writes:

- Directory creation (`mkdir`, line 1039-1040): idempotent, no stateful objects
- Steps directory cleanup (line 1042-1045): iterates and unlinks; no handle left open
- File writes (`write_text`, lines 1072, 1089, 1111, 1129): atomic — open/write/close in one call, no handles left open
- `subprocess.run` (line 1142): subprocess terminates before `run()` returns; no leak

No stateful objects persist on success paths.

## Positive Observations

- `generate_default_orchestrator` correctly conditions the Phase Models section on `phase_models is not None or default_model is not None`, not on truthiness of `phase_models`. This correctly handles the case where `phase_models={}` (empty) with `default_model` set — all phases fall back to `default_model`.
- `validate_and_create` at line 1015 normalizes `phase_models = phase_models or {}` before use, eliminating None checks downstream.
- First test exercises realistic mixed runbook (steps + cycles, two phases) with `phase_dir` to verify file path injection. Assertions check content with readable error messages.
- Second test covers phase model resolution: phase-level override (sonnet, opus) and frontmatter fallback (haiku) in a single runbook. Assertions are behavioral, not structural.
- Sorting of `all_phases` (line 947) is correct and handles non-contiguous phase numbers.
