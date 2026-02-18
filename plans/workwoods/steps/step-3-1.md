# Cycle 3.1

**Plan**: `plans/workwoods/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.1: Parse `git worktree list --porcelain` output

**Prerequisite:** Read explore-worktree-cli.md to understand worktree discovery patterns and porcelain format.

**RED Phase:**

**Test:** `test_parse_worktree_list_porcelain`
**Assertions:**
- Input: porcelain format with blocks separated by blank lines
- Each block contains "worktree <path>" on first line, "branch <ref>" on second line
- Output: list of TreeInfo objects with path and branch fields
- Specific case: "worktree /path/to/main\nbranch refs/heads/main\n\n" → TreeInfo(path="/path/to/main", branch="main")
- Specific case: "worktree /path/to/wt/slug\nbranch refs/heads/slug\n\n" → TreeInfo(path="/path/to/wt/slug", branch="slug")
- Multi-worktree: two blocks → two TreeInfo objects in list
- Branch format: "refs/heads/" prefix stripped from output (branch="main", not "refs/heads/main")

**Expected failure:** ImportError: cannot import name '_parse_worktree_list' from 'claudeutils.planstate.aggregation'

**Why it fails:** No aggregation.py module yet

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_parse_worktree_list_porcelain -v`

**GREEN Phase:**

**Implementation:** Parse git worktree list --porcelain output format

**Behavior:**
- Split output by blank lines (each block is one worktree)
- Extract path from "worktree <path>" line
- Extract branch from "branch <ref>" line, strip "refs/heads/" prefix
- Create TreeInfo namedtuple or dataclass for each worktree

**Approach:** Line-by-line parsing, collect fields per block, yield TreeInfo when blank line

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Create module with _parse_worktree_list(output: str) -> list[TreeInfo]
  Location hint: New file, internal helper function

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with sample porcelain output (no real git commands yet)
  Location hint: New file, test parser with string input

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_parse_worktree_list_porcelain -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---
