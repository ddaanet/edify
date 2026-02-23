# Cycle 1.1

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Phase Context

Core functions for naming, composition, and per-phase baseline selection.

---

## Cycle 1.1: Agent naming convention

**RED Phase:**

**Test:** `test_agent_frontmatter_crew_naming_multi_phase` and `test_agent_frontmatter_crew_naming_single_phase`
**Assertions:**
- `generate_agent_frontmatter("testplan", model="sonnet", phase_num=2, total_phases=3)` produces frontmatter containing `name: crew-testplan-p2`
- Description contains `Execute phase 2 of testplan`
- `generate_agent_frontmatter("testplan", model="sonnet", phase_num=1, total_phases=1)` produces frontmatter containing `name: crew-testplan` (no `-pN` suffix)
- Description contains `Execute testplan` (no phase number for single-phase)

**Expected failure:** AttributeError or TypeError — `generate_agent_frontmatter()` doesn't accept `phase_num`/`total_phases` params yet.

**Why it fails:** Current signature is `generate_agent_frontmatter(runbook_name, model=None)` — no phase params.

**Verify RED:** `pytest tests/test_prepare_runbook_agents.py -v -k "naming"`

**GREEN Phase:**

**Implementation:** Extend `generate_agent_frontmatter()` with `phase_num` and `total_phases` params.

**Behavior:**
- When `total_phases > 1`: name is `crew-{name}-p{phase_num}`, description is `Execute phase {phase_num} of {name}`
- When `total_phases == 1` (or defaults): name is `crew-{name}`, description is `Execute {name}`
- Both params default to allow backward-compatible calling (but old `<name>-task` naming is replaced)

**Approach:** Add keyword params with defaults. Conditional formatting in f-string.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify `generate_agent_frontmatter()` (line 794) — add `phase_num=1, total_phases=1` params, update name/description format strings
  Location hint: Function signature and return format string

**Verify GREEN:** `pytest tests/test_prepare_runbook_agents.py -v -k "naming"`
**Verify no regression:** `pytest tests/test_prepare_runbook_*.py -v`

---
