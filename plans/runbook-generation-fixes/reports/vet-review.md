# Vet Review: Runbook Generation Fixes — Final Quality Review

**Scope**: Phases 1-5 implementation — prepare-runbook.py (D-1/D-2/D-3/D-5 fixes), 3 new test modules, pytest_helpers, SKILL.md prose, implementation-notes.md
**Date**: 2026-02-22T00:00:00Z
**Mode**: review + fix

## Summary

Four root causes (RC-1 model propagation, RC-2 phase context, RC-3 phase numbering, RC-4 orchestrator) have been addressed with clean implementations. The core logic in `prepare-runbook.py` is correct: `extract_phase_models`, `extract_phase_preambles`, and the model resolution chain in `validate_and_create` all work as designed. Tests are behavior-focused with meaningful assertions and cover all design-specified cases. Two minor code quality issues identified and fixed.

**Overall Assessment**: Ready (post-fix)

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Section banner comment in test_prepare_runbook_inline.py**
   - Location: `tests/test_prepare_runbook_inline.py:23`
   - Note: `# --- Fixtures ---` is a section banner — deslop violation. Code grouping is communicated by proximity and naming.
   - **Status**: FIXED

2. **`generate_agent_frontmatter` emits `model: None` when model is absent**
   - Location: `agent-core/bin/prepare-runbook.py:660`
   - Note: The function writes `model: {model}` literally. When `agent_model` is `None` (pure inline runbook with no frontmatter model), the agent YAML has `model: None` — syntactically valid YAML but semantically wrong (Claude Code expects a string model name). The unresolved-model check only runs over steps/cycles, so inline-only runbooks skip that guard. In practice, inline runbooks in the test suite always have `model: haiku` in frontmatter, but the edge case exists.
   - **Status**: FIXED

---

## Fixes Applied

- `tests/test_prepare_runbook_inline.py:23` — removed `# --- Fixtures ---` section banner; fixtures are visually grouped by blank line and module-constant naming
- `agent-core/bin/prepare-runbook.py:655-658` — `generate_agent_frontmatter`: added None guard via `model_line = f"model: {model}\n" if model is not None else ""`; omits `model:` line entirely when model is absent instead of writing `model: None`

---

## Requirements Validation

Design reference: `plans/runbook-generation-fixes/outline.md`

| Requirement | Status | Evidence |
|-------------|--------|----------|
| RC-1 D-1: phase model extracted from header | Satisfied | `extract_phase_models()` regex at line 469-473 |
| RC-1 D-1: phase model overrides frontmatter | Satisfied | `cycle_model = phase_models.get(cycle['major'], model)` at line 1082; step path at line 1102 |
| RC-1 D-1: step-level model overrides phase model | Satisfied | `extract_step_metadata()` reads `**Execution Model**` from content; takes priority in `generate_cycle_file` |
| RC-1 D-1: no-model error | Satisfied | `validate_and_create` unresolved check at lines 1016-1036 |
| RC-1: fix hardcoded haiku in assemble_phase_files | Satisfied | `phase_models[min(phase_models)]` at line 595-596 replaces hardcoded haiku |
| RC-2 D-2: phase preamble extracted | Satisfied | `extract_phase_preambles()` at lines 476-511 |
| RC-2 D-2: preamble injected as `## Phase Context` in step files | Satisfied | `generate_step_file` at lines 812-815; `generate_cycle_file` at lines 848-851 |
| RC-2 D-2: empty preamble omits section | Satisfied | `if phase_context and phase_context.strip():` at lines 812 and 848 |
| RC-3 D-3: phase headers injected at assembly | Satisfied | `assemble_phase_files` lines 581-585 injects `### Phase N:` when absent |
| RC-3 D-3: existing headers not duplicated | Satisfied | `if re.search(rf"^###? Phase\s+{phase_num}:", ...)` check at line 582 |
| D-5: PHASE_BOUNDARY entries include phase file path | Satisfied | `generate_default_orchestrator` phase_dir injection at lines 939-940 |
| D-5: phase model table in orchestrator | Satisfied | `## Phase Models` section at lines 946-953 |
| Phase 5 SKILL.md: phase header format directive | Satisfied | "Every phase file MUST start with `### Phase N: title (type: TYPE, model: MODEL)` header" at SKILL.md:439 |
| Phase 5 SKILL.md: fallback header injection note | Satisfied | "Fallback header injection" paragraph at SKILL.md:622 |
| Phase 5 SKILL.md: missing headers pitfall | Satisfied | "Missing phase headers in phase files (causes model defaults and context loss)" at SKILL.md:893 |
| Phase 5 implementation-notes: When Editing Runbook Step Or Agent Files | Satisfied | New entry at implementation-notes.md:344-352 |

---

## Positive Observations

- `extract_phase_preambles` correctly handles all edge cases: phase with preamble, phase without preamble (empty string), last phase with trailing content, phase immediately followed by another phase header
- The model resolution chain (`step body > phase header > frontmatter > None`) is cleanly implemented with no inversion points
- `_run_validate` helpers in the new test modules are private (underscore prefix) and have minimal surface — they don't overengineer the test setup
- `TestPhaseContext.test_step_and_cycle_files_include_phase_context` validates ordering (metadata header → Phase Context → body) with `find`/`rfind` — tests the structural contract, not just content presence
- `TestPhaseNumbering.test_mixed_runbook_phase_metadata_and_orchestrator_correct` validates both PHASE_BOUNDARY assignment AND no-interleaving in a single test with clear assertion messages
- The `DEFAULT_TDD_COMMON_CONTEXT` sentinel approach avoids per-cycle stop condition duplication cleanly
- Phase file injection in `assemble_phase_files` uses `re.search` with `rf"^###? Phase\s+{phase_num}:"` to accept both H2 and H3 existing headers — correct for both formats
- `pytest_helpers.py` shared helpers are genuinely reusable: `setup_git_repo` and `setup_baseline_agents` used across all 3 new test modules without duplication

## Recommendations

None — the implementation is complete and correct for the stated requirements.
