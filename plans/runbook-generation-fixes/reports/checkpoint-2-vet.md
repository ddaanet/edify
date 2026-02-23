# Vet Review: Phase 2 Checkpoint — Model Propagation

**Scope**: Phase 2 implementation — `extract_phase_models()`, model threading in `validate_and_create()`, agent frontmatter model, missing-model error
**Date**: 2026-02-22T03:12:38
**Mode**: review + fix

## Summary

Phase 2 correctly implements the D-1 model priority chain (step body > phase model > frontmatter > error). `extract_phase_models()` parses phase headers accurately, threading through `validate_and_create()` is correct, and the missing-model validation is sound. Two issues require fixes: stale `default_model="haiku"` defaults in generator functions create a maintenance hazard, and the agent frontmatter writes `model: None` when models are only declared at the phase level with no frontmatter model.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Agent frontmatter writes `model: None` when no frontmatter model set**
   - Location: `agent-core/bin/prepare-runbook.py:617-626`, `validate_and_create()` lines 984-985
   - Problem: When a runbook has phase-level models but no frontmatter `model:` key, `metadata.get("model")` returns `None`. `generate_agent_frontmatter(runbook_name, None)` produces `model: None` in the agent YAML. The validation at lines 939-962 correctly passes (phase models satisfy each step), but the agent file is malformed. Most relevant for single-file runbooks where the author specifies models per phase rather than globally.
   - Fix: In `validate_and_create()`, derive the agent model from the first phase model when frontmatter model is absent. Use `phase_models[min(phase_models)]` as fallback before writing agent frontmatter.
   - **Status**: FIXED

### Minor Issues

1. **Stale `default_model="haiku"` in `generate_step_file` and `generate_cycle_file`**
   - Location: `agent-core/bin/prepare-runbook.py:745`, `agent-core/bin/prepare-runbook.py:775`
   - Note: These defaults are never activated — `validate_and_create()` always passes an explicit resolved model. But the defaults contradict the "no haiku fallback" guarantee introduced in Cycle 2.5. A future caller using these functions directly could silently produce haiku-defaulted artifacts.
   - **Status**: FIXED

2. **Helper function duplication between test files**
   - Location: `tests/test_prepare_runbook_mixed.py:106-126`, `tests/test_prepare_runbook_inline.py:288-309`
   - Note: `_setup_git_repo` and `_setup_baseline_agents` are identical in both files. The existing inline test file is pre-existing (not Phase 2 scope). Extracting to a conftest.py would resolve this.
   - **Status**: FIXED

3. **`MIXED_RUNBOOK_5PHASE` Phase 3 model resolution path undocumented**
   - Location: `tests/test_prepare_runbook_mixed.py:59-63`
   - Note: Phase 3 (`### Phase 3: Cleanup (type: general)`) has no model annotation and Step 3.1 has no step-level model. Resolution falls to `frontmatter_model = "sonnet"`. No comment documents this dependency on frontmatter fallback. Tests using this fixture that invoke `validate_and_create` would silently cover the frontmatter-fallback path, not the phase-model path. However, the only test using this fixture (`test_mixed_runbook_phase_metadata_and_orchestrator_correct`) doesn't call `validate_and_create`, so this is a documentation gap rather than a test correctness issue.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/prepare-runbook.py:984-987` — In `validate_and_create()`, compute `agent_model` as frontmatter model with fallback to first phase model (`phase_models[min(phase_models)]`), preventing `model: None` in agent YAML when models are only at phase level.
- `agent-core/bin/prepare-runbook.py:745` — Changed `generate_step_file` default from `default_model="haiku"` to `default_model=None`.
- `agent-core/bin/prepare-runbook.py:775` — Changed `generate_cycle_file` default from `default_model="haiku"` to `default_model=None`.
- `tests/pytest_helpers.py` — Added `setup_git_repo()` and `setup_baseline_agents()` shared helpers, with `import subprocess`.
- `tests/test_prepare_runbook_mixed.py` — Removed duplicate `_setup_git_repo`/`_setup_baseline_agents`; import from `tests.pytest_helpers`; renamed call sites; added fixture comment.
- `tests/test_prepare_runbook_inline.py` — Removed duplicate `_setup_git_repo`/`_setup_baseline_agents`; import from `tests.pytest_helpers`; renamed call sites.

## Requirements Validation

No explicit requirements context provided in task prompt. Design decisions validated against `plans/runbook-generation-fixes/outline.md`:

| Design Decision | Status | Evidence |
|----------------|--------|----------|
| D-1: Model priority chain (step > phase > frontmatter > error) | Satisfied | `extract_step_metadata()` priority: body regex → default_model param. `validate_and_create()`: `step_model or phase_models.get(phase) or frontmatter_model` |
| D-1: No haiku default (Cycle 2.5) | Satisfied | `extract_step_metadata(default_model=None)`, missing model → error in `validate_and_create()` |
| D-2: Phase context extraction | OUT-OF-SCOPE | Phase 3 (not yet implemented) |
| D-3: Phase numbering from file boundaries | Satisfied (Phase 1) | Pre-existing, verified passing |
| D-4: Single agent | Satisfied | One agent file generated per runbook |
| D-5: Orchestrator plan phase file references | OUT-OF-SCOPE | Phase 4 |

**Gaps:** Agent frontmatter model with phase-only models (major issue above, fixed).

---

## Positive Observations

- `extract_phase_models()` regex uses `re.IGNORECASE | re.MULTILINE` — handles case variations in phase header annotations cleanly.
- Model normalization to lowercase in `extract_phase_models()` prevents case-sensitivity bugs downstream.
- `validate_and_create()` validation loop checks all cycles and all steps before failing, collecting all unresolved items — error message is complete rather than stopping at first failure.
- `assemble_phase_files()` correctly sets frontmatter model from first phase (`phase_models[min(phase_models)]`) rather than any arbitrary phase.
- `_run_validate` test helper correctly threads `extract_phase_models()` through the pipeline, mirroring `main()` logic.
- Test assertions include diagnostic messages (f-strings with partial content on failure) — makes test failures self-explanatory.
