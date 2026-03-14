# Cycle 3.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

Pure data transformation: session.md + filesystem state → STATUS output. No mutations, no stdin.

---

---

## Cycle 3.3: Parallel group detection

**Note: Design revision pending.** ST-1 "largest independent group" selection replaced with "first eligible consecutive group" (document order, cap 5). The "top priority unblocked items" change primarily affects the cap and consecutive constraint retention — both are implemented here. Outline update required before orchestration to align wording.

**RED Phase:**

**Test:** `test_detect_parallel_group`, `test_detect_parallel_no_group`, `test_detect_parallel_shared_plan`
**File:** `tests/test_session_status.py`

**Assertions:**
- `detect_parallel(tasks, blockers)` with 3 consecutive tasks having different `plan_dir` values and no blockers returns group of all 3 task names
- `detect_parallel(tasks, blockers)` with single task returns `None` (no group)
- `detect_parallel(tasks, blockers)` with 2 tasks sharing `plan_dir="parser"` returns `None` (shared plan = dependent)
- `detect_parallel(tasks, blockers)` with tasks where a dependency breaks consecutive run → returns first eligible consecutive group (before the break)
- `detect_parallel(tasks, blockers)` with 7 consecutive independent tasks → returns first 5 (cap at 5 concurrent sessions)
- Blocker text mentioning task name creates dependency (breaks consecutive run)

**Expected failure:** `ImportError` — `detect_parallel` doesn't exist

**Why it fails:** No parallel detection function

**Verify RED:** `pytest tests/test_session_status.py::test_detect_parallel_group -v`

---
