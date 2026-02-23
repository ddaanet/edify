# Cycle 2.2

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Orchestrator plan format changes and integration through `validate_and_create()`.

---

## Cycle 2.2: validate_and_create creates per-phase agents (with inline-skip)

Depends on: 1.3, 1.4, 2.1

**RED Phase:**

**Test:** `test_validate_creates_per_phase_agents` and `test_validate_inline_phase_no_agent`

**Sub-case (a) — 2-phase mixed runbook (TDD phase 1, general phase 2):**
- Call `validate_and_create()` with `agents_dir` param (new signature)
- Assert: `crew-<name>-p1.md` file exists in agents_dir
- Assert: `crew-<name>-p2.md` file exists in agents_dir
- Assert: `<name>-task.md` does NOT exist (old naming gone)
- Assert: Phase 1 agent file contains "Test Driver" (test-driver baseline)
- Assert: Phase 2 agent file contains "Artisan" (artisan baseline)
- Assert: Both agents contain plan context ("Shared info" from Common Context)
- Assert: Phase 1 agent contains Phase 1 preamble; Phase 2 agent contains Phase 2 preamble

**Sub-case (b) — 3-phase runbook (TDD, inline, general):**
- Assert: `crew-<name>-p1.md` exists (TDD phase)
- Assert: `crew-<name>-p3.md` exists (general phase)
- Assert: `crew-<name>-p2.md` does NOT exist (inline phase — no agent)
- Assert: Orchestrator plan contains "(orchestrator-direct)" for phase 2

**Expected failure:** TypeError — `validate_and_create()` doesn't accept `agents_dir` param.

**Why it fails:** Current signature has `agent_path` (single file), not `agents_dir` (directory).

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "validate_creates"`

**GREEN Phase:**

**Implementation:** Modify `validate_and_create()` to create per-phase agents.

**Behavior:**
- Replace `agent_path` param with `agents_dir` (Path to agents directory)
- Use `detect_phase_types()` to classify all phases from assembled content
- For each non-inline phase: call `generate_phase_agent()`, write to `agents_dir / f"crew-{name}-p{N}.md"`
- For single non-inline phase: use `crew-{name}.md` (no -pN)
- Build `phase_agents` dict, pass to `generate_default_orchestrator()`
- Stage all created agent files with `git add`
- Remove old single-agent creation code

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `validate_and_create()` (line 1090) — new param, per-phase loop
  Location hint: Lines 1187-1205 (current agent creation block)
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `derive_paths()` (line 751) — return `agents_dir` instead of single `agent_path`
  Location hint: Lines 762-764
- File: `agent-core/bin/prepare-runbook.py`
  Action: Update `main()` — pass `agents_dir` to `validate_and_create()`
  Location hint: Lines 1420-1432

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "validate_creates"`
**Verify no regression:** Existing tests will FAIL (expected — Cycle 2.3 handles regression)

---
