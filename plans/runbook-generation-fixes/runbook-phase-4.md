### Phase 4: Orchestrator plan improvements (type: tdd, model: sonnet)

D-5: Phase file references in PHASE_BOUNDARY markers. Phase-agent model mapping.

**Post-Phase-2 state:** `extract_phase_models()` exists and `validate_and_create()` threads per-phase models to step/cycle generation. Phase models dict is available for orchestrator plan generation.

**Cumulative signature note (if Phases 3 and 4 run sequentially):** When implementing Phase 4, `validate_and_create()` already has `phase_models` (Phase 2) and `phase_preambles` (Phase 3) parameters. Add `phase_dir` as an additional parameter — do not replace the prior additions.

**Prerequisites:**
- Phase 2 complete (model propagation working)
- `agent-core/bin/prepare-runbook.py` — target file
- `tests/test_prepare_runbook_mixed.py` — test module (with Phases 1-3 tests)

**Completion validation:**
- All 2 cycles pass (RED fails then GREEN passes)
- `just test tests/test_prepare_runbook_mixed.py` — all tests pass (Phases 1-4)
- No regressions: `just test tests/test_prepare_runbook_inline.py`
- Orchestrator plan includes phase file paths and phase-model mapping table

---

## Cycle 4.1: PHASE_BOUNDARY entries include phase file path

**Prerequisite:** Read `generate_default_orchestrator()` (line ~743-805) — understand PHASE_BOUNDARY generation at line ~798-800 and how `is_phase_boundary` is computed.

**RED Phase:**

**Test:** `test_orchestrator_plan_includes_phase_file_paths`
**Setup:** Create phase files in `tmp_path` directory:
- `plans/test-job/runbook-phase-1.md`: Phase 1 with general steps (model: sonnet)
- `plans/test-job/runbook-phase-2.md`: Phase 2 with TDD cycles (model: sonnet)

Assemble via `assemble_phase_files()`, run full pipeline through `validate_and_create()`.

**Assertions:**
- Orchestrator plan contains `Phase file: plans/test-job/runbook-phase-1.md` in Phase 1 PHASE_BOUNDARY entry
- Orchestrator plan contains `Phase file: plans/test-job/runbook-phase-2.md` in Phase 2 PHASE_BOUNDARY entry
- Phase file paths reference the actual source phase files (not assembled content)

**Expected failure:** AssertionError — current `generate_default_orchestrator()` does not include phase file paths in PHASE_BOUNDARY entries

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestOrchestratorPlan::test_orchestrator_plan_includes_phase_file_paths -v`

---

**GREEN Phase:**

**Implementation:** Add phase file references to PHASE_BOUNDARY entries.

**Behavior:**
- When runbook is assembled from phase files (directory input), PHASE_BOUNDARY entries include the source phase file path
- When runbook is a single file (no phase files), phase file paths are omitted
- Format: `Phase file: {phase_dir}/runbook-phase-{phase_num}.md` on a separate line within the PHASE_BOUNDARY block

**Approach:**
1. Add `phase_dir` parameter to `generate_default_orchestrator()` (default: `None`)
2. In PHASE_BOUNDARY block (line ~798-800): when `phase_dir` is not None, append `Phase file: {phase_dir}/runbook-phase-{phase}.md\n` after the checkpoint instruction line
3. In `validate_and_create()`: pass the source directory path (when assembled from phase files) to `generate_default_orchestrator()`. Add `phase_dir` parameter to `validate_and_create()` signature, populated from `main()` when input is a directory.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_dir` parameter to `generate_default_orchestrator()`, include phase file path in PHASE_BOUNDARY
  Location hint: Function signature (line ~743), PHASE_BOUNDARY block (line ~798-800)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_dir` parameter to `validate_and_create()`, pass to orchestrator generation
  Location hint: Function signature (line ~808), orchestrator call (line ~904-908)
- File: `agent-core/bin/prepare-runbook.py`
  Action: In `main()`, pass source directory to `validate_and_create()` when input is directory
  Location hint: Directory handling branch (line ~955-967)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestOrchestratorPlan -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`

---

## Cycle 4.2: Phase-agent mapping table with correct models

**Prerequisite:** Understand Phase 2 state — `phase_models` dict is computed in `main()` and threaded to `validate_and_create()`.

**RED Phase:**

**Test:** `test_orchestrator_plan_includes_phase_model_table`
**Setup:** Create mixed runbook with phases having different models:
- Frontmatter: `model: haiku` (explicit — required; Cycle 2.5 removed the haiku fallback default)
- Phase 1 header: `### Phase 1: ... (type: tdd, model: sonnet)` — explicit model in header
- Phase 2 header: `### Phase 2: ... (type: tdd, model: opus)` — explicit model in header
- Phase 3 header: `### Phase 3: ... (type: general)` — no model in header (inherits frontmatter `model: haiku`)

Run full pipeline.

**Assertions:**
- Orchestrator plan contains a `## Phase Models` section
- Section contains `- Phase 1: sonnet`, `- Phase 2: opus`, `- Phase 3: haiku` (one per line)
- All phases present (not just those with explicit models)

**Expected failure:** AssertionError — current orchestrator plan has no `## Phase Models` section

**Verify RED:** `pytest tests/test_prepare_runbook_mixed.py::TestOrchestratorPlan::test_orchestrator_plan_includes_phase_model_table -v`

---

**GREEN Phase:**

**Implementation:** Generate phase-model mapping table in orchestrator plan.

**Behavior:**
- After the step execution order section, add a `## Phase Models` section
- List each phase with its resolved model (phase-level if declared, frontmatter default if not)
- Format: `- Phase N: model_name` per line

**Approach:**
1. Add `phase_models` and `default_model` parameters to `generate_default_orchestrator()` (default: `None`)
2. After step execution order section: if `phase_models` is provided, generate `## Phase Models` section
3. Collect all phase numbers from items list, resolve each to its model: `phase_models.get(phase_num, default_model)`
4. In `validate_and_create()`: pass `phase_models` dict and frontmatter `model` to `generate_default_orchestrator()` call

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `phase_models` and `default_model` parameters to `generate_default_orchestrator()`, generate Phase Models section
  Location hint: Function signature (line ~743), after step execution order section (line ~805)
- File: `agent-core/bin/prepare-runbook.py`
  Action: In `validate_and_create()`, pass `phase_models` and `model` to orchestrator generation call
  Location hint: Orchestrator call (line ~904-908)

**Verify GREEN:** `pytest tests/test_prepare_runbook_mixed.py::TestOrchestratorPlan -v`
**Verify no regression:** `pytest tests/test_prepare_runbook_mixed.py tests/test_prepare_runbook_inline.py -v`
