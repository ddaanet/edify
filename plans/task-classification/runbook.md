# Task Classification Runbook (Tier 2)

**Design:** `plans/task-classification/outline.md`
**Tier:** 2 — Lightweight Delegation
**Model:** sonnet (TDD), opus (prose artifacts)

---

## Recall Context

Key decisions resolved:
- **Worktree tasks:** Static classification, no move semantics. `→ slug` marker inline, filesystem query for status display.
- **D+B compliance:** Skill steps must open with concrete tool call (Read/Bash/Glob).
- **E2E testing:** Real git repos in tmp_path, mock only for error injection.
- **CLI testing:** Click CliRunner in-process.
- **Context preloading:** Explicit `/prime` skill invocation, not @ref injection.

---

## TDD Cycles

### Cycle 1: `add_slug_marker()` — add marker inline

**RED:** Test in `tests/test_worktree_session.py`:
- `add_slug_marker(session_path, "Task A", "task-a")` on session.md with "## Worktree Tasks" containing `- [ ] **Task A** — desc`
- Assert: task line becomes `- [ ] **Task A** → \`task-a\` — desc`
- Assert: task stays in "Worktree Tasks" section (no section move)
- Assert: other tasks unchanged
- Edge: task not found → ValueError

**GREEN:** Implement `add_slug_marker(session_path, task_name, slug)` in `session.py`:
- Read content, find task by name in "Worktree Tasks" section
- Regex-insert `→ \`slug\`` after `**name**` on first line
- Write back. No section creation, no moves.

### Cycle 2: `remove_slug_marker()` — remove marker inline

**RED:** Test in `tests/test_worktree_session.py`:
- `remove_slug_marker(session_path, "task-a")` on session.md with `→ \`task-a\`` in Worktree Tasks
- Assert: `→ \`task-a\`` removed from task line
- Assert: task remains in Worktree Tasks (no removal, no section move)
- Assert: no-op if slug not found (no error)
- Multi-line task: continuation lines preserved

**GREEN:** Implement `remove_slug_marker(session_path, slug)` in `session.py`:
- Read content, find task with `→ \`slug\`` in "Worktree Tasks"
- Regex-remove `→ \`slug\` ` from first line
- Write back. No git operations, no completion check.

### Cycle 3: `focus_session()` — read from Worktree Tasks, output In-tree Tasks

**RED:** Test in `tests/test_worktree_session.py`:
- Session.md has "## In-tree Tasks" and "## Worktree Tasks" sections
- Task is in "Worktree Tasks"
- `focus_session("Task A", session_path)` finds it
- Output contains `## In-tree Tasks` header (not "Pending Tasks")
- Output strips `→ \`slug\`` from task if present

**GREEN:** Update `focus_session()`:
- Change `section="Pending Tasks"` → `section="Worktree Tasks"` (line 328)
- Change output header `## Pending Tasks` → `## In-tree Tasks` (line 340)
- Strip slug marker from task lines in output

### Cycle 4: Delete old functions, update session.py exports

**RED:** Verify existing tests for `move_task_to_worktree` and `remove_worktree_task` are removed/updated.
- Tests that call old functions should be rewritten for new functions (cycles 1-2 tests replace these)

**GREEN:**
- Delete `move_task_to_worktree()`, `remove_worktree_task()`, `_task_is_in_pending_section()`, `_find_git_root()`
- Update all test files: remove/replace old test functions
- Remove tests in `test_worktree_session_remove.py` (entire file tests old `remove_worktree_task`)

### Cycle 5: resolve.py — "In-tree Tasks" merge strategy

**RED:** Test in `tests/test_worktree_merge_session_resolution.py`:
- `_merge_session_contents()` with "## In-tree Tasks" sections → additive merge works
- Worktree Tasks also additive (new tasks from branch merged)
- Existing tests updated from "Pending Tasks" to "In-tree Tasks"

**GREEN:** Update `_merge_session_contents()`:
- Change `"Pending Tasks"` → `"In-tree Tasks"` in section name references
- Remove `if b.section != "Worktree Tasks"` filter — both sections participate in additive merge
- Update `find_section_bounds()` call from `"Pending Tasks"` → `"In-tree Tasks"`

### Cycle 6: session_structure.py — "In-tree Tasks" validation

**RED:** Test in `tests/test_validation_session_structure.py`:
- `validate()` with "## In-tree Tasks" + "## Worktree Tasks" → cross-section check works
- "Pending Tasks" section still recognized (backward compat in validation)
- Existing tests updated for new section names

**GREEN:** Update `validate()`:
- Change `sections.get("Pending Tasks", [])` → `sections.get("In-tree Tasks", [])`
- Update `check_cross_section_uniqueness()` parameter names/docs
- Update error messages: "both Pending" → "both In-tree"

### Cycle 7: aggregation.py + cli.py caller updates

**RED:** Test:
- `_task_summary()` reads from "## In-tree Tasks" section
- CLI `new()` command uses `add_slug_marker()` behavior
- CLI `rm()` command uses `remove_slug_marker()` behavior (no amend)

**GREEN:**
- `aggregation.py`: change `section="Pending Tasks"` → `section="In-tree Tasks"` in `_task_summary()`
- `cli.py`: import `add_slug_marker`, `remove_slug_marker` instead of old functions
- `cli.py new()`: call `add_slug_marker()` instead of `move_task_to_worktree()`
- `cli.py _update_session_and_amend()`: simplify to just `remove_slug_marker()`, drop amend ceremony
- Update `test_worktree_session_automation.py` and `test_planstate_aggregation_integration.py`

---

## General Steps

### Step 8: `/prime` skill (opus)

**New file:** `agent-core/skills/prime/SKILL.md`

Skill behavior:
1. Accept arg: `plans/<name>/` (plan directory path)
2. Read all existing plan artifacts: requirements.md, outline.md, design.md, runbook-outline.md
3. Chain-call `/recall` (no explicit topic — plan content in conversation provides signal)

D+B compliant: Step 1 opens with Glob/Read calls (concrete tool anchors). Step 2 is skill invocation.

### Step 9: Handoff skill updates (opus)

Update `agent-core/skills/handoff/SKILL.md`:
- Section template: replace "## Pending Tasks" with "## In-tree Tasks"
- Add classification heuristic (D-9) for new task creation:
  - In-tree: no plan directory, mechanical edits, no restart
  - Worktree: plan directory + behavioral changes, opus model tier, restart flag, or explicitly parallel scope
- Carry-forward rule: covers both "In-tree Tasks" and "Worktree Tasks" sections

### Step 10: execute-rule.md updates (opus)

Update `agent-core/fragments/execute-rule.md`:
- `#status` display: show "In-tree Tasks" first, then "Worktree Tasks" (D-7)
- `#execute` pickup: `x` starts first in-tree task (D-8). Worktree tasks require `wt` setup.
- Section names throughout: "Pending Tasks" → "In-tree Tasks"
- Task metadata format example: update section references

### Step 11: operational-tooling.md decision update (opus)

Update `agents/decisions/operational-tooling.md`:
- "When Tracking Worktree Tasks In Session.md" entry:
  - Old pattern (inline marker in single Pending section) → superseded
  - New pattern: two-section model (In-tree Tasks + Worktree Tasks), static classification, no move semantics
  - Reference outline D-4 rationale

---

## Execution Order

1. TDD cycles 1-3 (session.py core): sequential, one agent, piecemeal
2. TDD cycle 4 (cleanup): depends on 1-3
3. TDD cycles 5-7 (callers): depends on 4, can be parallelized
4. General steps 8-11 (prose): independent of TDD, opus model
5. Checkpoint: `just precommit`, corrector review

---

## Test Files Affected

- `tests/test_worktree_session.py` — update/add tests for new functions
- `tests/test_worktree_session_remove.py` — replace with remove_slug_marker tests or delete
- `tests/test_worktree_session_automation.py` — update for add_slug_marker CLI flow
- `tests/test_worktree_merge_session_resolution.py` — update section names
- `tests/test_validation_session_structure.py` — update section names
- `tests/test_planstate_aggregation_integration.py` — update section name
