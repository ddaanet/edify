# Cycle 3.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

**GREEN Phase:**

**Implementation:** Add `detect_parallel()` to `session/status.py`

**Behavior:**
- `detect_parallel(tasks: list[ParsedTask], blockers: list[list[str]]) -> list[str] | None`
- Only consecutive independent tasks form a group (not arbitrary subsets)
- Walk tasks in document order, building a consecutive run of independent tasks. A task is dependent if it shares `plan_dir` with any task in the current run, or is mentioned in blocker text
- A dependency breaks the consecutive run — start a new run
- First eligible group in document order (2+ consecutive independent tasks)
- Cap at 5 concurrent sessions
- Return task names if group has 2+ members, else None

**Approach:** Linear scan — iterate tasks, extend current consecutive group while independent. On dependency, check if current group qualifies (2+), return it. If not, reset and continue. Cap group size at 5.

**Changes:**
- File: `src/claudeutils/session/status.py`
  Action: Add `detect_parallel()` function

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_status.py -v`
**Verify no regression:** `just precommit`

---
