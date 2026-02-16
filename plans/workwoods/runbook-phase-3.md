### Phase 3: Cross-Tree Aggregation (type: tdd)

**Purpose:** Implement cross-tree status collection via git worktree discovery and per-tree data gathering.

**Scope:**
- `src/claudeutils/planstate/aggregation.py` - Cross-tree data collection
- `tests/test_planstate_aggregation.py` - Real git repo tests

**Dependencies:** Phases 1 + 2 (aggregates planstate + vet status)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** High (git interaction correctness requires real-repo tests)

**Weak Orchestrator Metadata:**
- Total Cycles: 7
- Restart required: No

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

## Cycle 3.2: Detect main tree (is_main=True, slug=None)

**RED Phase:**

**Test:** `test_main_tree_detection`
**Assertions:**
- Input: list with 3 TreeInfo objects representing main + 2 worktrees
- First TreeInfo: is_main field equals True (boolean True, not truthy value)
- First TreeInfo: slug field equals None (not empty string)
- Second TreeInfo: is_main equals False, slug equals "worktree-1" (extracted from path "/path/wt/worktree-1")
- Third TreeInfo: is_main equals False, slug equals "worktree-2" (extracted from path "/path/wt/worktree-2")
- Slug extraction verifies basename only (path.name, not parent directories)

**Expected failure:** AssertionError: TreeInfo object missing is_main or slug attributes, or is_main=False for first tree

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

## Cycle 3.4: Dirty state detection (git status --porcelain)

**RED Phase:**

**Test:** `test_dirty_state_detection`
**Assertions:**
- Setup: Create git repo, commit tracked file, create clean state
- Clean state: Call _is_dirty(repo_path) → returns False (boolean False, not falsy value)
- Dirty state: Modify tracked file without staging, call _is_dirty(repo_path) → returns True
- Untracked ignored: Create new untracked file, call _is_dirty(repo_path) → returns False (untracked files don't trigger dirty)
- Verification: Uses git status --porcelain --untracked-files=no (exact command, not --short or other variants)

**Expected failure:** NameError: name '_is_dirty' is not defined, or always returns False even when tracked file modified

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

## Cycle 3.5: Task summary from session.md (first pending task)

**RED Phase:**

**Test:** `test_task_summary_extraction`
**Assertions:**
- Setup: Create git repo with agents/session.md containing "## Pending Tasks\n- [ ] **Fix bug** — description"
- Call _task_summary(repo_path) → returns string "Fix bug" (task name only, not markdown formatting)
- Edge case: session.md exists but no Pending Tasks section → returns None (not exception)
- Edge case: Pending Tasks section empty (no task lines) → returns None
- Edge case: session.md file doesn't exist → returns None (not FileNotFoundError)
- Verification: Uses extract_task_blocks(content, section="Pending Tasks") and returns blocks[0].name

**Expected failure:** NameError: name '_task_summary' is not defined, or returns None when pending task exists

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

## Cycle 3.6: Per-tree plan discovery (list_plans per tree)

**RED Phase:**

**Test:** `test_per_tree_plan_discovery`
**Assertions:**
- Setup: Create main repo with plans/plan-a/, create worktree with plans/plan-b/
- Call aggregate_trees() → AggregatedStatus.plans contains 2 PlanState objects
- Plan names: "plan-a" from main and "plan-b" from worktree both present
- Deduplication: Create same plan (plans/plan-c/) in both trees → only 1 PlanState in result
- Deduplication precedence: main tree plan overrides worktree plan (main wins on conflict)
- Verification: Uses actual list_plans() function (from Phase 1), not mocked

**Expected failure:** AggregatedStatus.plans contains only main tree plans, or contains duplicate plan-c entries

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

## Cycle 3.7: Sort trees by latest_commit_timestamp descending

**RED Phase:**

**Test:** `test_tree_sorting_by_timestamp`
**Assertions:**
- Setup: Create main + 2 worktrees, commit to main at T1, worktree1 at T2, worktree2 at T3 (T3 > T2 > T1)
- Call aggregate_trees() → AggregatedStatus.trees[0] is worktree2 (most recent)
- Order verification: trees[0].latest_commit_timestamp > trees[1].latest_commit_timestamp > trees[2].latest_commit_timestamp
- Specific index check: trees[0].slug == "worktree-2", trees[1].slug == "worktree-1", trees[2].is_main == True
- Type check: All latest_commit_timestamp values are integers

**Expected failure:** Trees in wrong order (main first, or worktree1 before worktree2), or timestamps not descending

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
- All 7 tests pass in test_planstate_aggregation.py
- Real git repos used in all tests (tmp_path fixtures)
- Cross-tree plan discovery works correctly
- Trees sorted by recency (most recent first)
