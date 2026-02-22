# Cycle 4.2

**Plan**: `plans/runbook-generation-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

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
