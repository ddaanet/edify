### Phase 4: Upgraded wt-ls CLI (type: tdd)

**Purpose:** Upgrade existing ls command with rich output mode and backward-compatible porcelain flag.

**Scope:**
- `src/claudeutils/worktree/cli.py` - ls command modification
- `tests/test_worktree_ls_upgrade.py` - CLI output tests

**Dependencies:** Phase 3 (CLI consumes aggregation)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** Low-Medium (CLI output formatting with backward compatibility)

**Weak Orchestrator Metadata:**
- Total Cycles: 4
- Restart required: No

---

## Cycle 4.1: Add --porcelain flag to ls command

**Prerequisite:** Read current cli.py ls implementation (lines 145-151) to understand existing structure.

**RED Phase:**

**Test:** `test_porcelain_flag_exists`
**Assertions:**
- `claudeutils _worktree ls --porcelain` runs without error
- `claudeutils _worktree ls --help` shows --porcelain flag in help text
- Flag is boolean (no argument required)

**Expected failure:** Unrecognized option --porcelain (flag not added)

**Why it fails:** ls command doesn't accept --porcelain flag yet

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_flag_exists -v`

**GREEN Phase:**

**Implementation:** Add @click.option for --porcelain flag to ls command

**Behavior:**
- Add `@click.option("--porcelain", is_flag=True, help="Machine-readable output")`
- Accept porcelain parameter in ls function signature
- When porcelain=True: use existing logic
- When porcelain=False: use new rich output (stub for now)

**Approach:** Click boolean flag, default False (rich output is new default)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add @click.option("--porcelain") decorator above ls command
  Location hint: Above @worktree.command() decorator for ls (around line 145)

- File: `src/claudeutils/worktree/cli.py`
  Action: Update ls() function signature to accept porcelain: bool parameter
  Location hint: ls function definition (line 146)

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test invoking CLI with --porcelain flag via CliRunner
  Location hint: New file, use click.testing.CliRunner

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_flag_exists -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.2: Porcelain mode preserves existing behavior

**RED Phase:**

**Test:** `test_porcelain_mode_backward_compatible`
**Assertions:**
- Output format matches existing ls output: `<slug>\t<branch>\t<path>`
- Tab-separated fields preserved
- Main tree excluded (existing behavior)
- Uses existing _parse_worktree_list() logic

**Expected failure:** Output format changed or incompatible with existing consumers

**Why it fails:** Porcelain mode not wired to existing logic

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_mode_backward_compatible -v`

**GREEN Phase:**

**Implementation:** When porcelain=True, execute existing ls logic unchanged

**Behavior:**
- if porcelain: run existing code path (_parse_worktree_list + tab output)
- else: run new rich output path (to be implemented)
- Preserve exact output format for porcelain mode

**Approach:** Conditional branch on porcelain flag

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add if/else branch in ls() based on porcelain parameter
  Location hint: Inside ls function body

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with real worktree, verify tab-separated output matches expected format
  Location hint: New test function, use tmp_path with git worktree

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_mode_backward_compatible -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.3: Rich mode header + task formatting

**Prerequisite:** Verify `src/claudeutils/planstate/aggregation.py` exists with `aggregate_trees()` function (Phase 1-3 dependency). If missing, STOP — Phase 4 requires completed planstate module.

**RED Phase:**

**Test:** `test_rich_mode_header_and_task`
**Assertions:**
- Header format:
  - For worktree with slug="test-wt", branch="feature", is_dirty=True, commits_since_handoff=3:
    Output contains: `test-wt (feature)  ●  3 commits since handoff`
  - For main tree with is_dirty=False, commits_since_handoff=0:
    Output contains: `main (main)  ○  clean`
  - Dirty indicator: `●` when is_dirty=True, `○` when is_dirty=False
- Task line:
  - For tree with task_summary="Implement foo feature":
    Output contains exactly: `  Task: Implement foo feature` (2-space indent)
  - For tree with task_summary=None:
    Output does NOT contain any line starting with "  Task:"
  - Task line appears directly after header line for same tree

**Expected failure:** Rich output not formatted (AttributeError accessing TreeStatus fields)

**Why it fails:** Rich output formatting not implemented

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_and_task -v`

**GREEN Phase:**

**Implementation:** Format header line and conditional task line from TreeStatus fields

**Behavior:**
- Call aggregate_trees() from planstate.aggregation
- For each tree: format header line with slug/branch, dirty indicator, commit status
- Slug display: tree.slug, or "main" when tree.is_main=True
- Dirty indicator: "●" when is_dirty=True, "○" when False
- Commit status: "N commits since handoff" when >0, "clean" when 0
- After header, if task_summary is not None: output `  Task: <summary>` (2-space indent)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Import aggregate_trees from planstate.aggregation
  Location hint: Top of file, with other imports

- File: `src/claudeutils/worktree/cli.py`
  Action: Implement rich output with header + conditional task line in else branch
  Location hint: Inside ls function, else clause

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with real git repo + session.md, verify header format and task line
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_and_task -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.4: Rich mode plan + gate formatting

**RED Phase:**

**Test:** `test_rich_mode_plan_and_gate`
**Assertions:**
- Plan line:
  - For tree containing plan "foo" with status="designed", next_action="/runbook plans/foo/design.md":
    Output contains exactly: `  Plan: foo [designed] → /runbook plans/foo/design.md` (2-space indent)
  - Multiple plans: both plan lines shown in same tree section
  - No plans: no "  Plan:" line for that tree
- Gate line:
  - For plan with gate="vet stale — re-vet first":
    Output contains exactly: `  Gate: vet stale — re-vet first` (2-space indent)
    Gate line appears after plan line for same plan
  - For plan with gate=None: no "  Gate:" line for that plan
- Plans filtered by tree (only plans under current tree's plans/ directory shown)

**Expected failure:** Plan line not displayed (AttributeError or plan filtering not implemented)

**Why it fails:** Plan and gate line formatting not implemented

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_and_gate -v`

**GREEN Phase:**

**Implementation:** Display plan lines with conditional gate lines for plans in current tree

**Behavior:**
- After task line, iterate through aggregated_status.plans
- Filter to plans belonging to current tree (plan directory under tree path)
- For each plan: output plan line `  Plan: <name> [<status>] → <next_action>`
- If plan.gate is not None: output gate line `  Gate: <gate message>`

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py` (Phase 1-3 artifact)
  Action: Verify PlanState includes tree association for filtering
  Location hint: Check AggregatedStatus.plans structure

- File: `src/claudeutils/worktree/cli.py`
  Action: Add plan + gate line output after task line in rich formatting loop
  Location hint: After task line in tree iteration

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with plans/ directory + stale design.md, verify Plan and Gate lines
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_and_gate -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Phase 4 Checkpoint

**After all cycles complete:**

1. Run `just dev` to verify code quality
2. Functional review: Check that rich output displays correctly with real worktrees
3. Backward compatibility check: Verify porcelain mode exactly matches old output
4. File growth check: If cli.py exceeds 400 lines, extract rich formatting to format.py or display.py module
5. Commit: All Phase 4 implementations and tests

**Expected state:**
- ls command accepts --porcelain flag
- Porcelain mode preserves exact backward compatibility
- Rich mode displays header, task, plan, and gate lines correctly
- All 4 tests pass in test_worktree_ls_upgrade.py
- Integration test with real worktrees verifies correct plan status display
