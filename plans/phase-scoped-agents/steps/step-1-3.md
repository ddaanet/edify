# Cycle 1.3

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Core functions for naming, composition, and per-phase baseline selection.

---

## Cycle 1.3: Phase agent body composition

Depends on: 1.1, 1.2

**RED Phase:**

**Test:** `test_generate_phase_agent_layers`
**Assertions:**
- `generate_phase_agent("myplan", phase_num=1, phase_type="tdd", plan_context="## Common Context\nShared info", phase_context="Phase 1 preamble text", model="sonnet", total_phases=2)` returns markdown containing:
  - (1) Frontmatter block with `name: crew-myplan-p1` (from `generate_agent_frontmatter`)
  - (2) Test-driver baseline body (contains "Test Driver" from baseline template)
  - (3) Plan context section: `# Runbook-Specific Context` followed by common context
  - (4) Phase context section: `# Phase Context` followed by phase preamble
  - (5) Clean-tree footer: "Clean tree requirement"
- Layer ordering: frontmatter index < baseline index < plan context index < phase context index < footer index

**Expected failure:** ImportError or NameError — `generate_phase_agent` doesn't exist yet.

**Why it fails:** Function not yet defined.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "phase_agent_layers"`

**GREEN Phase:**

**Implementation:** New function `generate_phase_agent()`.

**Behavior:**
- Composes 5 layers in order:
  1. `generate_agent_frontmatter(name, model, phase_num, total_phases)` → frontmatter
  2. `read_baseline_agent(phase_type)` → baseline body
  3. Plan context: `"\n---\n# Runbook-Specific Context\n\n" + plan_context` (if non-empty)
  4. Phase context: `"\n---\n# Phase Context\n\n" + phase_context` (if non-empty)
  5. Footer: `"\n\n---\n\n**Clean tree requirement:** Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions.\n"`

**Approach:** String concatenation of layers, using existing functions for 1 and 2.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add new function `generate_phase_agent()` after `generate_agent_frontmatter()`
  Location hint: After the updated `generate_agent_frontmatter()` function

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "phase_agent_layers"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---
