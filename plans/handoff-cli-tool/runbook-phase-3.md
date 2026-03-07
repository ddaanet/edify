### Phase 3: Status subcommand (type: tdd, model: sonnet)

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

## Cycle 3.1: Render Next task

**RED Phase:**

**Test:** `test_render_next_task`, `test_render_next_skips_worktree_markers`, `test_render_next_no_pending`
**File:** `tests/test_session_status.py`

**Assertions:**
- `render_next(tasks)` where first task is pending (checkbox `" "`) with no `→` marker returns:
  ```
  Next: Build parser
    `/runbook plans/parser/design.md`
    Model: sonnet | Restart: no
  ```
- `render_next(tasks)` where first task has `worktree_marker="my-slug"` and second has `worktree_marker="wt"` and third is plain pending → returns third task's info
- `render_next([])` returns `""` (empty string, no Next section)
- Tasks with checkbox `"x"`, `"!"`, `"†"`, `"-"` are all skipped (only `" "` without marker is eligible)

**Expected failure:** `ImportError` — `render_next` doesn't exist

**Why it fails:** No `session/status/render.py` module

**Verify RED:** `pytest tests/test_session_status.py::test_render_next_task -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status/render.py` with `render_next()`

**Behavior:**
- Iterate tasks, find first with `checkbox == " "` and `worktree_marker is None`
- Format as `Next:` block with command, model, restart
- Model defaults to "sonnet" if None. Restart shows "yes" if True, "no" if False

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Create with `render_next(tasks: list[ParsedTask]) -> str`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.2: Render list sections with parametrized tests

**RED Phase:**

**Test:** `test_render_section[pending]`, `test_render_section[worktree]`, `test_render_section[unscheduled]`, `test_render_empty_section[pending]`, `test_render_empty_section[worktree]`, `test_render_empty_section[unscheduled]`
**File:** `tests/test_session_status.py`

**Assertions — Pending section:**
- `render_pending(tasks, plan_states)` with two tasks returns:
  ```
  Pending:
  - Build parser (sonnet)
    - Plan: parser | Status: outlined
  - Fix bug (haiku)
  ```
- Task with non-default model shows `(model)`. Default (sonnet) omitted
- Task with associated plan directory shows nested plan/status line
- Completed tasks (`checkbox == "x"`) excluded

**Assertions — Worktree section:**
- `render_worktree(tasks)` with branched task returns:
  ```
  Worktree:
  - Parallel work → my-slug
  - Future work → wt
  ```
- `→ slug` for branched tasks, `→ wt` for destined-but-not-yet-branched

**Assertions — Unscheduled Plans section:**
- `render_unscheduled(all_plans, task_plan_dirs)` with plans not associated to any task returns:
  ```
  Unscheduled Plans:
  - orphan-plan — designed
  ```
- Plans with status `delivered` excluded
- Sorted alphabetically
- Plans associated to any pending task excluded

**Empty section assertions (all three):**
- Each render function returns `""` when input list is empty

**Expected failure:** `ImportError` — render functions don't exist

**Why it fails:** No rendering functions for these sections

**Verify RED:** `pytest tests/test_session_status.py -k "render_section or render_empty" -v`

---

**GREEN Phase:**

**Implementation:** Add `render_pending()`, `render_worktree()`, `render_unscheduled()` to `session/status/render.py`

**Behavior:**
- `render_pending(tasks, plan_states)`: Filter to pending tasks (checkbox `" "`), format with optional plan status. Non-default model shown in parens. Plan status from `plan_states` dict mapping plan name → status string
- `render_worktree(tasks)`: Format worktree tasks with `→` markers
- `render_unscheduled(all_plans, task_plan_dirs)`: Filter plans not in `task_plan_dirs` set, exclude `delivered`, sort alphabetically, format with `—` separator

**Approach:** Each function produces a section string or empty string. Caller concatenates non-empty sections.

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add three rendering functions

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.3: Parallel group detection

**RED Phase:**

**Test:** `test_detect_parallel_group`, `test_detect_parallel_no_group`, `test_detect_parallel_shared_plan`
**File:** `tests/test_session_status.py`

**Assertions:**
- `detect_parallel(tasks, blockers)` with 3 tasks having different `plan_dir` values and no blockers returns group of all 3 task names
- `detect_parallel(tasks, blockers)` with single task returns `None` (no group)
- `detect_parallel(tasks, blockers)` with 2 tasks sharing `plan_dir="parser"` returns `None` (shared plan = dependent)
- `detect_parallel(tasks, blockers)` with 4 tasks where 2 share a plan returns group of 2 independent tasks (largest independent subset)
- Blocker text mentioning task name creates dependency (excluded from group)

**Expected failure:** `ImportError` — `detect_parallel` doesn't exist

**Why it fails:** No parallel detection function

**Verify RED:** `pytest tests/test_session_status.py::test_detect_parallel_group -v`

---

**GREEN Phase:**

**Implementation:** Add `detect_parallel()` to `session/status/render.py`

**Behavior:**
- `detect_parallel(tasks: list[ParsedTask], blockers: list[list[str]]) -> list[str] | None`
- Build dependency graph: tasks with shared `plan_dir` are dependent. Tasks mentioned in blocker text are dependent on the blocker
- Find largest independent set (no shared plan_dir, no blocker references between them)
- Return task names if group has 2+ members, else None

**Approach:** Simple graph algorithm — build dependency edges (shared plan_dir, blocker reference), then find the largest independent set (no edges between members). For small task lists (<20), brute-force over subsets is fine: enumerate all subsets of pending tasks in descending size order, return first subset with no dependency edges between any pair.

**Changes:**
- File: `src/claudeutils/session/status/render.py`
  Action: Add `detect_parallel()` function

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 3.4: CLI wiring — `claudeutils _session status`

**RED Phase:**

**Test:** `test_session_status_cli`, `test_session_status_missing_session`
**File:** `tests/test_session_status.py`

**Assertions:**
- CliRunner invoking `_session status` with a real session.md file in cwd produces output containing:
  - `Next:` section with first pending task
  - `Pending:` section
  - Output exits with code 0
- CliRunner invoking `_session status` without session.md file → exit code 2, output contains `**Error:**`

**Expected failure:** Command `_session status` not registered — Click returns non-zero with "No such command"

**Why it fails:** No status subcommand registered in session CLI group

**Verify RED:** `pytest tests/test_session_status.py::test_session_status_cli -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/status/cli.py` with Click command, register in session group

**Behavior:**
- `@click.command(name="status")` function
- Read `agents/session.md` (cwd-relative) → `parse_session()`
- Call `claudeutils _worktree ls` via subprocess for plan states
- Parse `_worktree ls` output for plan status: lines matching `  Plan: {name} [{status}] → ...` — extract name and status into a dict `{name: status}` passed to `render_pending()`
- Call render functions (Next, Pending, Worktree, Unscheduled, Parallel)
- Concatenate non-empty sections with blank line separators
- Output to stdout, exit 0
- Missing session.md → `_fail("**Error:** Session file not found: agents/session.md", code=2)`

**Changes:**
- File: `src/claudeutils/session/status/cli.py`
  Action: Create with `status` Click command
- File: `src/claudeutils/session/cli.py`
  Action: Import and register: `from claudeutils.session.status.cli import status; session_group.add_command(status)`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---

**Phase 3 Checkpoint:** `just precommit` — status subcommand fully functional.
