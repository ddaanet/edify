### Phase 3: Cross-Tree Aggregation (type: tdd)

**Purpose:** Implement cross-tree status collection via git worktree discovery and per-tree data gathering.

**Scope:**
- `src/claudeutils/planstate/aggregation.py` - Cross-tree data collection
- `tests/test_planstate_aggregation.py` - Real git repo tests

**Dependencies:** Phases 1 + 2 (aggregates planstate + vet status)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** High (git interaction correctness requires real-repo tests)

---

## Cycle 3.1: Parse `git worktree list --porcelain` output

**Prerequisite:** Read explore-worktree-cli.md to understand worktree discovery patterns and porcelain format.

**RED Phase:**

**Test:** `test_parse_worktree_list_porcelain`
**Assertions:**
- Parses `worktree /path/to/main` + `branch refs/heads/main` → TreeInfo(path="/path/to/main", branch="main")
- Parses `worktree /path/to/wt/slug` + `branch refs/heads/slug` → TreeInfo(path="/path/to/wt/slug", branch="slug")
- Handles multiple worktrees in single output
- Returns list of TreeInfo objects (internal model for parsing)

**Expected failure:** ImportError (aggregation module doesn't exist)

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

## Cycle 3.2: Detect main tree (is_main=True, slug=None)

**RED Phase:**

**Test:** `test_main_tree_detection`
**Assertions:**
- First worktree in `git worktree list` output is marked is_main=True
- First worktree has slug=None
- Other worktrees have is_main=False and slug extracted from path
- Slug extraction uses path basename (e.g., /path/wt/my-task → "my-task")

**Expected failure:** is_main is always False or slug is None for main tree (detection wrong)

**Why it fails:** Main tree detection logic not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_main_tree_detection -v`

**GREEN Phase:**

**Implementation:** Mark first worktree as main, extract slug from path for others

**Behavior:**
- First TreeInfo in list → is_main=True, slug=None
- Other TreeInfo → is_main=False, slug=path.name (basename)
- Use Path(tree_path).name to extract slug

**Approach:** Enumerate over parsed worktrees, check index == 0 for main

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Add is_main and slug fields to TreeInfo, compute based on position
  Location hint: In _parse_worktree_list() or separate post-processing

- File: `src/claudeutils/planstate/models.py`
  Action: Add is_main and slug fields to TreeStatus dataclass
  Location hint: TreeStatus definition

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with porcelain output containing main + 2 worktrees
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_main_tree_detection -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Cycle 3.3: Commits since handoff (git log anchor on agents/session.md)

**RED Phase:**

**Test:** `test_commits_since_handoff_counting`
**Assertions:**
- With session.md in git history: counts commits from last session.md change to HEAD
- Without session.md commits: returns 0 (no anchor = no session commits)
- Uses `git log -1 --format=%H -- agents/session.md` for anchor
- Uses `git rev-list <anchor>..HEAD --count` for counting

**Expected failure:** Always returns 0 or raises exception (git command not implemented)

**Why it fails:** No git integration for commit counting

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_commits_since_handoff_counting -v`

**GREEN Phase:**

**Implementation:** Use git log to find session.md anchor, git rev-list to count commits

**Behavior:**
- Run: `git -C <tree> log -1 --format=%H -- agents/session.md`
- If empty output: return 0 (no session.md commits)
- Otherwise: run `git -C <tree> rev-list <anchor>..HEAD --count`
- Parse count as integer

**Approach:** subprocess.run with capture_output, check stderr for errors

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _commits_since_handoff(tree_path: Path) -> int using subprocess
  Location hint: New helper function

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo via tmp_path, create commits and session.md changes
  Location hint: New test function, use subprocess to init repo and make commits

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_commits_since_handoff_counting -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Cycle 3.4: Latest commit subject + timestamp

**RED Phase:**

**Test:** `test_latest_commit_extraction`
**Assertions:**
- `git log -1 --format=%s%n%ct` returns subject on first line, unix timestamp on second
- Correctly parses both fields
- latest_commit_subject contains commit message text
- latest_commit_timestamp is integer (Unix epoch)

**Expected failure:** Fields not extracted or wrong format

**Why it fails:** Latest commit extraction not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_latest_commit_extraction -v`

**GREEN Phase:**

**Implementation:** Run git log with format %s (subject) and %ct (committer timestamp)

**Behavior:**
- Run: `git -C <tree> log -1 --format=%s%n%ct`
- Split output by newline
- First line = subject string
- Second line = timestamp integer (parse with int())

**Approach:** Two-line output, split and parse separately

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _latest_commit(tree_path: Path) -> tuple[str, int]
  Location hint: New helper function

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo, make commit with known message
  Location hint: New test function, verify exact subject and timestamp type

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_latest_commit_extraction -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Cycle 3.5: Dirty state detection (git status --porcelain)

**RED Phase:**

**Test:** `test_dirty_state_detection`
**Assertions:**
- `git status --porcelain --untracked-files=no` with empty output → is_dirty=False
- `git status --porcelain --untracked-files=no` with non-empty output → is_dirty=True
- Only tracked file changes count (untracked files ignored)

**Expected failure:** is_dirty always False or always True (detection wrong)

**Why it fails:** Dirty state detection not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_dirty_state_detection -v`

**GREEN Phase:**

**Implementation:** Run git status --porcelain, check if output is empty

**Behavior:**
- Run: `git -C <tree> status --porcelain --untracked-files=no`
- If output.strip() is empty → is_dirty=False
- Otherwise → is_dirty=True

**Approach:** String emptiness check after strip()

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _is_dirty(tree_path: Path) -> bool
  Location hint: New helper function

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo, modify tracked file without staging
  Location hint: New test function, create dirty tree and verify detection

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_dirty_state_detection -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Cycle 3.6: Task summary from session.md (first pending task)

**RED Phase:**

**Test:** `test_task_summary_extraction`
**Assertions:**
- Reads <tree>/agents/session.md
- Extracts first pending task name via extract_task_blocks()
- task_summary contains task name string
- Returns None if no pending tasks exist
- Returns None if session.md doesn't exist

**Expected failure:** task_summary always None or exception when session.md missing

**Why it fails:** Session.md reading and task extraction not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_task_summary_extraction -v`

**GREEN Phase:**

**Implementation:** Read session.md, call extract_task_blocks(), return first task name

**Behavior:**
- Check if <tree>/agents/session.md exists
- If not exists: return None
- Read file content
- Call extract_task_blocks(content, section="Pending Tasks")
- If blocks empty: return None
- Otherwise: return blocks[0].name

**Approach:** Import extract_task_blocks from worktree.session module

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Implement _task_summary(tree_path: Path) -> str | None
  Location hint: New helper function, imports extract_task_blocks

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with real git repo, write session.md with pending task
  Location hint: New test function, verify correct task name extracted

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_task_summary_extraction -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Cycle 3.7: Per-tree plan discovery (list_plans per tree)

**RED Phase:**

**Test:** `test_per_tree_plan_discovery`
**Assertions:**
- For each tree, runs list_plans(tree_path / "plans")
- Aggregates all plans across all trees
- Plans from main tree and worktree trees both included
- Plans deduplicated by name if same plan exists in multiple trees (main wins)

**Expected failure:** Plans from worktrees not discovered or duplicates exist

**Why it fails:** Per-tree plan scanning not implemented

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_per_tree_plan_discovery -v`

**GREEN Phase:**

**Implementation:** Run list_plans() for each tree's plans/ directory, aggregate results

**Behavior:**
- For each tree_path in worktrees:
  - Run list_plans(tree_path / "plans")
  - Collect PlanState objects
- Deduplicate by plan name (main tree plans override worktree plans)
- Store all plans in AggregatedStatus.plans list

**Approach:** Dict keyed by plan name to deduplicate, convert to list at end

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Add plan discovery loop in aggregate_trees()
  Location hint: After tree iteration, before return

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with main + worktree, both having plans/ directories
  Location hint: New test function, verify both trees' plans found

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_per_tree_plan_discovery -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Cycle 3.8: Sort trees by latest_commit_timestamp descending

**RED Phase:**

**Test:** `test_tree_sorting_by_timestamp`
**Assertions:**
- Trees sorted with most recent commit first
- latest_commit_timestamp used as sort key
- Descending order (highest timestamp = index 0)
- TreeStatus list in AggregatedStatus.trees is sorted

**Expected failure:** Trees in arbitrary order or sorted incorrectly

**Why it fails:** No sorting applied to trees list

**Verify RED:** `pytest tests/test_planstate_aggregation.py::test_tree_sorting_by_timestamp -v`

**GREEN Phase:**

**Implementation:** Sort trees by latest_commit_timestamp in descending order

**Behavior:**
- After collecting all TreeStatus objects, sort by latest_commit_timestamp
- Use sorted(trees, key=lambda t: t.latest_commit_timestamp, reverse=True)
- Store sorted list in AggregatedStatus.trees

**Approach:** Python sorted() with lambda key and reverse=True

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Add sorting step in aggregate_trees() before return
  Location hint: After tree collection loop, before creating AggregatedStatus

- File: `tests/test_planstate_aggregation.py`
  Action: Create test with main + 2 worktrees, make commits at different times
  Location hint: New test function, verify order matches commit timestamps

**Verify GREEN:** `pytest tests/test_planstate_aggregation.py::test_tree_sorting_by_timestamp -v`
**Verify no regression:** `pytest tests/test_planstate_aggregation.py -v`

---

## Phase 3 Checkpoint

**After all cycles complete:**

1. Run `just dev` to verify code quality
2. Functional review: Check that aggregate_trees() correctly discovers worktrees and collects per-tree data
3. Integration check: Verify all git operations work with real repos (no mocked subprocess)
4. Commit: All Phase 3 implementations and tests

**Expected state:**
- aggregation.py module exists with aggregate_trees() function
- All 8 tests pass in test_planstate_aggregation.py
- Real git repos used in all tests (tmp_path fixtures)
- Cross-tree plan discovery works correctly
- Trees sorted by recency (most recent first)
