# Cycle 2.1

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Orchestrator plan format changes and integration through `validate_and_create()`.

---

## Cycle 2.1: Orchestrator plan format — Agent field and Phase-Agent Mapping table

Depends on: 1.4 (phase type info for table rows)

**RED Phase:**

**Test:** `test_orchestrator_agent_field_per_step` and `test_orchestrator_phase_agent_mapping_table`

**Sub-case (a) — Agent field per step:**
- `generate_default_orchestrator("testjob", cycles=[...], phase_agents={1: "crew-testjob-p1", 2: "crew-testjob-p2"})` output includes:
  - `Agent: crew-testjob-p1` after phase 1 step headers
  - `Agent: crew-testjob-p2` after phase 2 step headers
  - Header text does NOT contain "using testjob-task agent"

**Sub-case (b) — Phase-Agent Mapping table:**
- `generate_default_orchestrator("testjob", ..., phase_agents={1: "crew-testjob-p1", 2: "(orchestrator-direct)", 3: "crew-testjob-p3"}, phase_types={1: "tdd", 2: "inline", 3: "general"})` output includes:
  - `## Phase-Agent Mapping` section
  - Table row containing `1`, `crew-testjob-p1`, `tdd`
  - Table row containing `2`, `(orchestrator-direct)`, `inline`
  - Table row containing `3`, `crew-testjob-p3`, `general`

**Expected failure:** TypeError — `generate_default_orchestrator()` doesn't accept `phase_agents` or `phase_types` params.

**Why it fails:** Current signature has no `phase_agents` or `phase_types` parameters.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "orchestrator"`

**GREEN Phase:**

**Implementation:** Extend `generate_default_orchestrator()` with `phase_agents` and `phase_types` params.

**Behavior:**
- New params: `phase_agents` (dict of phase→agent_name), `phase_types` (dict of phase→type_str)
- Header text: "Execute steps using per-phase agents." (replaces old `{name}-task` reference)
- After step `##` header line, emit `Agent: {phase_agents[phase]}` line
- Before step list, generate `## Phase-Agent Mapping` table with columns: Phase, Agent, Model, Type
- Inline phases show "(orchestrator-direct)" in Agent column

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `generate_default_orchestrator()` (line 987) — add params, emit Agent: lines, generate mapping table
  Location hint: Function signature and the step iteration loop

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "orchestrator"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---
