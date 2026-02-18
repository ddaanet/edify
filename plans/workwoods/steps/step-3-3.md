# Cycle 3.3

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.3: Git metadata helpers (commits since handoff + latest commit)

**RED Phase:**

**Test:** `test_git_metadata_helpers`
**Assertions:**
- _commits_since_handoff:
  - Setup: Create git repo, commit session.md, make 3 additional commits (total 4 commits)
  - `_commits_since_handoff(repo_path)` returns integer 3 (commits after session.md)
  - No session.md in history → returns integer 0 (not None or exception)
  - session.md modified in HEAD → returns integer 0 (anchor is HEAD itself)
- _latest_commit:
  - Setup: Create git repo, commit with subject "Test commit message"
  - `_latest_commit(repo_path)` returns tuple (str, int)
  - First element equals "Test commit message" exactly
  - Second element is integer type, Unix epoch (10-digit)
- Both use real subprocess calls to git (no mocking)

**Expected failure:** NameError: name '_commits_since_handoff' is not defined

**Why it fails:** No git integration for commit counting or latest commit extraction

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_git_metadata_helpers -v`

**GREEN Phase:**

**Implementation:** Use git log to find session.md anchor, git rev-list to count commits; extract latest commit subject and timestamp

**Behavior:**
- _commits_since_handoff: Run `git -C <tree> log -1 --format=%H -- agents/session.md`, then `git -C <tree> rev-list <anchor>..HEAD --count`
- _latest_commit: Run `git -C <tree> log -1 --format=%s%n%ct`, split output, parse timestamp as int
- Both return default values for edge cases (0 for no anchor, etc.)

**Approach:** subprocess.run with capture_output, check stderr for errors

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _commits_since_handoff(tree_path: Path) -> int and _latest_commit(tree_path: Path) -> tuple[str, int]
  Location hint: New helper functions

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo via tmp_path, covering both helpers
  Location hint: New test function, use subprocess to init repo and make commits

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_git_metadata_helpers -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
