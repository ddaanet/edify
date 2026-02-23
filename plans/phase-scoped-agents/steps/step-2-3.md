# Cycle 2.3

**Plan**: `plans/phase-scoped-agents/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Orchestrator plan format changes and integration through `validate_and_create()`.

---

## Cycle 2.3: Existing test regression updates

Depends on: 2.2 (API change: `agent_path` → `agents_dir`)

[REGRESSION] — RED is implicit: existing tests fail after 2.2 changes the `validate_and_create` signature.

**GREEN Phase:**

**Implementation:** Update all existing test files to use new `agents_dir` signature.

**Behavior:**
- `_run_validate()` helpers (2 files) change from passing `tmp_path / ".claude" / "agents" / f"{name}-task.md"` to `tmp_path / ".claude" / "agents"`
- Direct `validate_and_create()` calls (2 files) same change
- Assertions checking `agent_path.exists()` or agent content now check `agents_dir / f"crew-{name}[-p{N}].md"`
- For tests using single-phase runbooks: agent is `crew-{name}.md` (no -pN)
- For tests using multi-phase runbooks: agents are `crew-{name}-p{N}.md`

**Changes:**
- File: `tests/test_prepare_runbook_mixed.py`
  Action: Update `_run_validate()` helper and assertions
  Location hint: Lines 86-95 (helper), agent path assertions throughout
- File: `tests/test_prepare_runbook_orchestrator.py`
  Action: Update `_run_validate()` helper and assertions
  Location hint: Lines 26-44 (helper), assertions throughout
- File: `tests/test_prepare_runbook_inline.py`
  Action: Update direct `validate_and_create()` calls and assertions
  Location hint: Lines 168-182, 214-225, 258-267, 297-306, 340-348
- File: `tests/test_prepare_runbook_phase_context.py`
  Action: Update direct `validate_and_create()` calls and assertions
  Location hint: Lines 95, 193

**Verify GREEN:** `pytest tests/test_prepare_runbook_*.py -v`
**Verify no regression:** Full test suite passes

---

### Phase 3: Orchestrate skill update (type: inline)

- Update `agent-core/skills/orchestrate/SKILL.md`:
  - Section 3.1, line 97: Change `subagent_type: "<runbook-name>-task"` to `subagent_type: [from orchestrator plan "Agent:" field for this step]`
  - Section 2, line 39: Update `.claude/agents/<runbook-name>-task.md` to `.claude/agents/crew-<runbook-name>[-p<N>].md`
  - Section 2, line 47: Update `Plan-specific agent: .claude/agents/<runbook-name>-task.md` to describe per-phase agents
