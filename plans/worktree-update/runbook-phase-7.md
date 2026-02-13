# Phase 7: Add `merge` Command (4-Phase Ceremony)

**Complexity:** High (13 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Implement 4-phase merge ceremony — clean tree gate, submodule resolution, parent merge with auto-resolution, precommit validation.

**Dependencies:** Phase 1 (needs `wt_path()` for directory resolution)

---

## Cycle 7.1: Phase 1 pre-checks — OURS clean tree (session exempt)

**Objective:** Verify main repo and submodule are clean before merge, with session file exemption.

**Prerequisite:** Read justfile `wt-merge` recipe lines 200-250 — understand 4-phase ceremony structure and clean tree enforcement.

**RED Phase:**

**Test:** `test_merge_ours_clean_tree`
**Assertions:**
- Command: `claudeutils _worktree merge <slug>` (new command, doesn't exist yet)
- When main repo has uncommitted changes in source files: exit 1 with message "Clean tree required for merge (main)"
- When main repo has uncommitted changes in `agents/session.md`: merge proceeds (session exempt)
- When main repo has uncommitted changes in `agents/learnings.md`: merge proceeds (learnings exempt)
- When agent-core submodule has uncommitted changes: exit 1 with message "Clean tree required for merge (main submodule)"
- Both parent and submodule checked (not just parent)

**Expected failure:** NameError: command `merge` not defined, or no clean tree enforcement

**Why it fails:** Command doesn't exist yet

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_ours_clean_tree -v`

---

**GREEN Phase:**

**Implementation:** Create `merge` command with OURS clean tree validation

**Behavior:**
- New Click command: `@click.command()` with slug argument
- Check main repo: run `git status --porcelain --untracked-files=no`
- Filter output: exclude lines matching `agents/session.md` and `agents/learnings.md`
- If filtered output non-empty: exit 1 with "Clean tree required for merge (main)"
- Check submodule: run `git -C agent-core status --porcelain --untracked-files=no`
- If output non-empty: exit 1 with "Clean tree required for merge (main submodule)"

**Approach:** New command function, subprocess status checks, filtered validation, early exit on dirty

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add new `merge` command function with Click decorators
  Location hint: After `rm` command definition
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement OURS clean tree check with session exemption
  Location hint: Early in function, use subprocess and filtering
- File: `src/claudeutils/worktree/cli.py`
  Action: Implement submodule clean tree check (strict, no exemptions)
  Location hint: After main repo check

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_ours_clean_tree -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_rm.py -v`
- All Phase 6 tests still pass

---

## Cycle 7.2: Phase 1 pre-checks — THEIRS clean tree (strict, no session exemption)

**Objective:** Verify worktree and its submodule are clean (strict check prevents uncommitted state loss).

**RED Phase:**

**Test:** `test_merge_theirs_clean_tree`
**Assertions:**
- When worktree has ANY uncommitted changes (including session.md): exit 1 with message "Clean tree required for merge (worktree: uncommitted changes would be lost)"
- No exemption for session files in worktree (strict enforcement)
- When worktree submodule has uncommitted changes: exit 1 with message "Clean tree required for merge (worktree submodule)"
- Both worktree parent and submodule checked
- Error message mentions potential data loss

**Expected failure:** AssertionError: no worktree clean check, or session exemption applied to worktree

**Why it fails:** THEIRS check not implemented, or uses same exemption logic as OURS

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_theirs_clean_tree -v`

---

**GREEN Phase:**

**Implementation:** Add THEIRS clean tree check (strict, no exemptions)

**Behavior:**
- Get worktree path using `wt_path(slug)`
- Check worktree: run `git -C <wt-path> status --porcelain --untracked-files=no`
- If output non-empty: exit 1 with "Clean tree required for merge (worktree: uncommitted changes would be lost)"
- Check worktree submodule: run `git -C <wt-path>/agent-core status --porcelain --untracked-files=no`
- If output non-empty: exit 1 with "Clean tree required for merge (worktree submodule)"
- NO filtering (strict check on all files)

**Approach:** Same subprocess pattern as OURS, but without session file filtering

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add worktree path resolution in `merge` command
  Location hint: After OURS checks, use `wt_path(slug)`
- File: `src/claudeutils/worktree/cli.py`
  Action: Add THEIRS clean tree check (strict, no filter)
  Location hint: After OURS checks, use `cwd=<wt-path>` for git status
- File: `src/claudeutils/worktree/cli.py`
  Action: Add THEIRS submodule check
  Location hint: After THEIRS parent check

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_theirs_clean_tree -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_merge_ours_clean_tree -v`
- Cycle 7.1 test still passes

---

## Cycle 7.3: Phase 1 pre-checks — branch existence and worktree directory check

**Objective:** Verify branch exists and optionally warn about missing worktree directory.

**RED Phase:**

**Test:** `test_merge_branch_existence`
**Assertions:**
- When branch doesn't exist: exit 2 with message "Branch <slug> not found"
- When branch exists but worktree directory doesn't: warning printed, merge continues (branch-only merge valid)
- When both exist: no warning, merge proceeds
- Exit code 2 for fatal errors (branch missing), exit 1 for conflicts/precommit, exit 0 for success

**Expected failure:** AssertionError: no branch check, or error on missing worktree directory

**Why it fails:** Branch existence validation not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_branch_existence -v`

---

**GREEN Phase:**

**Implementation:** Add branch existence check and directory warning

**Behavior:**
- Run `git rev-parse --verify <slug>` with `check=False`
- If exit code ≠ 0: exit 2 with "Branch <slug> not found"
- Check if `<wt-path>` exists on filesystem
- If not exists: print warning "Worktree directory not found, merging branch only"
- Continue merge (branch-only merge is valid)

**Approach:** Subprocess with exit code check, filesystem check with conditional warning

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add branch existence check in `merge` command
  Location hint: After clean tree checks
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `git rev-parse --verify <slug>`, exit 2 on failure
  Location hint: Use subprocess with check=False
- File: `src/claudeutils/worktree/cli.py`
  Action: Add worktree directory check with warning
  Location hint: After branch check, use `Path(<wt-path>).exists()`

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_branch_existence -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 pre-check tests still pass

---

## Cycle 7.4: Phase 2 submodule resolution — ancestry check

**Objective:** Determine if worktree's submodule commit needs merging (or is already ancestor).

**RED Phase:**

**Test:** `test_merge_submodule_ancestry`
**Assertions:**
- Extract worktree's submodule commit: `git ls-tree <slug> -- agent-core` returns commit SHA
- Compare to local: `git -C agent-core rev-parse HEAD` returns local commit SHA
- When commits identical: skip submodule merge (no-op)
- When worktree commit is ancestor of local: skip merge (already merged)
- When worktree commit is NOT ancestor: proceed to merge (Cycle 7.5-7.6)
- Ancestry check uses `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>`

**Expected failure:** AssertionError: no ancestry check, or wrong merge decision

**Why it fails:** Submodule ancestry logic not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_submodule_ancestry -v`

---

**GREEN Phase:**

**Implementation:** Add submodule ancestry check logic

**Behavior:**
- Extract worktree's submodule commit: `git ls-tree <slug> -- agent-core | awk '{print $3}'`
- Get local submodule commit: `git -C agent-core rev-parse HEAD`
- If commits identical: skip submodule merge
- Check ancestry: `git -C agent-core merge-base --is-ancestor <wt-commit> <local-commit>` with `check=False`
- If exit code 0 (is ancestor): skip submodule merge
- If exit code ≠ 0 (not ancestor): proceed to merge (flag for 7.5-7.6)

**Approach:** Subprocess calls to extract commits and check ancestry, conditional branching

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule commit extraction in `merge` command
  Location hint: After Phase 1 checks (Phase 2 start)
- File: `src/claudeutils/worktree/cli.py`
  Action: Extract worktree submodule commit from ls-tree
  Location hint: Parse `git ls-tree <slug> -- agent-core` output
- File: `src/claudeutils/worktree/cli.py`
  Action: Get local submodule commit
  Location hint: `git -C agent-core rev-parse HEAD`
- File: `src/claudeutils/worktree/cli.py`
  Action: Compare commits and check ancestry
  Location hint: Use merge-base --is-ancestor, capture exit code

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_submodule_ancestry -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 and 7.4 tests still pass

---

## Cycle 7.5: Phase 2 submodule resolution — fetch if needed (with object check)

**Objective:** Fetch worktree's submodule commit if unreachable in local repo.

**RED Phase:**

**Test:** `test_merge_submodule_fetch`
**Assertions:**
- Before fetching: check object reachability with `git -C agent-core cat-file -e <wt-commit>`
- If object exists locally (exit 0): skip fetch (optimization)
- If object doesn't exist locally (exit ≠ 0): fetch from worktree
- Fetch command: `git -C agent-core fetch <wt-path>/agent-core HEAD`
- After fetch: object becomes reachable (can proceed to merge)
- Only fetch when needed (not unconditional)

**Expected failure:** AssertionError: unconditional fetch, or no object reachability check

**Why it fails:** Fetch logic not implemented, or always runs regardless of object existence

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_submodule_fetch -v`

---

**GREEN Phase:**

**Implementation:** Add conditional fetch based on object reachability

**Behavior:**
- From 7.4: have `wt_commit` and `needs_merge` flag
- If `needs_merge == False`: skip entirely (already ancestor)
- Check object reachability: `git -C agent-core cat-file -e <wt-commit>` with `check=False`
- If exit code 0: object exists, skip fetch
- If exit code ≠ 0: object missing, run `git -C agent-core fetch <wt-path>/agent-core HEAD`
- Fetch makes object available for merge in 7.6

**Approach:** Conditional fetch based on cat-file check, optimization for local objects

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add object reachability check in `merge` command
  Location hint: After ancestry check from 7.4
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `cat-file -e` to check if object exists
  Location hint: Use subprocess with check=False
- File: `src/claudeutils/worktree/cli.py`
  Action: Conditional fetch if object missing
  Location hint: Only run fetch when cat-file exit code ≠ 0

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_submodule_fetch -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_merge_submodule_ancestry -v`
- Cycle 7.4 test still passes

---

## Cycle 7.6: Phase 2 submodule resolution — merge and commit

**Objective:** Merge worktree's submodule commit into local submodule and commit.

**RED Phase:**

**Test:** `test_merge_submodule_merge_commit`
**Assertions:**
- When merge needed (from 7.4): run `git -C agent-core merge --no-edit <wt-commit>`
- After merge: stage submodule with `git add agent-core`
- Commit with message: `🔀 Merge agent-core from <slug>`
- Only commit if staged changes exist (check `git diff --cached --quiet`)
- When no merge needed: skip merge and commit (no-op)

**Expected failure:** AssertionError: no merge performed, or wrong commit message, or commit when no changes

**Why it fails:** Submodule merge logic not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_submodule_merge_commit -v`

---

**GREEN Phase:**

**Implementation:** Add submodule merge and commit logic

**Behavior:**
- From 7.4-7.5: have `needs_merge` flag and `wt_commit` (fetched if needed)
- If `needs_merge == False`: skip entirely
- Run `git -C agent-core merge --no-edit <wt-commit>`
- Stage: `git add agent-core`
- Check if staged: `git diff --cached --quiet agent-core` (exit ≠ 0 means changes)
- If staged changes: `git commit -m "🔀 Merge agent-core from <slug>"`
- If no staged changes: skip commit

**Approach:** Conditional merge based on flag, staging check before commit

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add submodule merge in `merge` command
  Location hint: After fetch logic from 7.5
- File: `src/claudeutils/worktree/cli.py`
  Action: Run merge, stage, check for staged changes, commit
  Location hint: Sequential subprocess calls conditional on `needs_merge` flag

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_submodule_merge_commit -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 2 tests still pass

---

## Cycle 7.7: Phase 3 parent merge — initiate merge

**Objective:** Initiate parent merge and detect conflicts.

**RED Phase:**

**Test:** `test_merge_parent_initiate`
**Assertions:**
- Run `git merge --no-commit --no-ff <slug>` (capture stdout and stderr)
- When merge succeeds (no conflicts): exit code 0, proceed to commit
- When conflicts occur: exit code ≠ 0, get conflict list from `git diff --name-only --diff-filter=U`
- No automatic commit (--no-commit flag ensures manual conflict handling possible)
- Non-fast-forward merge enforced (--no-ff preserves merge structure)

**Expected failure:** AssertionError: wrong git command, or auto-commit on success, or no conflict detection

**Why it fails:** Parent merge initiation not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_parent_initiate -v`

---

**GREEN Phase:**

**Implementation:** Add parent merge initiation with conflict detection

**Behavior:**
- Run `git merge --no-commit --no-ff <slug>` with `check=False` (capture exit code and output)
- If exit code 0: merge clean, proceed to commit (skip conflict handling)
- If exit code ≠ 0: conflicts occurred, get conflict list
- Conflict list: `git diff --name-only --diff-filter=U`
- Store conflict list for 7.8-7.11 auto-resolution logic

**Approach:** Subprocess with error handling, conflict detection via diff filter

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add parent merge initiation in `merge` command (Phase 3 start)
  Location hint: After Phase 2 submodule resolution
- File: `src/claudeutils/worktree/cli.py`
  Action: Run merge with --no-commit --no-ff flags
  Location hint: Use subprocess with check=False, capture exit code
- File: `src/claudeutils/worktree/cli.py`
  Action: Get conflict list if exit code ≠ 0
  Location hint: Run `git diff --name-only --diff-filter=U`

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_parent_initiate -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 1 and Phase 2 tests still pass

---

## Cycle 7.8: Phase 3 conflict handling — agent-core auto-resolve

**Objective:** Auto-resolve agent-core submodule conflicts (already merged in Phase 2).

**RED Phase:**

**Test:** `test_merge_conflict_agent_core`
**Assertions:**
- When `agent-core` in conflict list: run `git checkout --ours agent-core && git add agent-core`
- After resolution: `agent-core` removed from conflict list
- Rationale: submodule already merged in Phase 2, Phase 3 conflict is stale
- No manual intervention required (automatic resolution)

**Expected failure:** AssertionError: agent-core conflict not resolved, or wrong resolution strategy

**Why it fails:** agent-core auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_agent_core -v`

---

**GREEN Phase:**

**Implementation:** Add agent-core conflict auto-resolution

**Behavior:**
- From 7.7: have conflict list
- Check if `"agent-core"` in conflict list
- If present: run `git checkout --ours agent-core` then `git add agent-core`
- Use `--ours` because Phase 2 already resolved submodule (local state is correct)
- Remove from conflict list after resolution

**Approach:** Conditional resolution based on conflict list membership, subprocess commands

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add agent-core conflict check in `merge` command
  Location hint: After merge initiation from 7.7, in conflict handling section
- File: `src/claudeutils/worktree/cli.py`
  Action: Run checkout --ours and git add for agent-core
  Location hint: Conditional on conflict list membership

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_agent_core -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py::test_merge_parent_initiate -v`
- Cycle 7.7 test still passes

---

## Cycle 7.9: Phase 3 conflict handling — session.md auto-resolve (task extraction)

**Objective:** Auto-resolve session.md conflicts by keeping ours and printing new worktree tasks for manual extraction.

**Prerequisite:** Read design lines 150-154 — understand session.md conflict handling (keep ours, extract new tasks from theirs).

**RED Phase:**

**Test:** `test_merge_conflict_session_md`
**Assertions:**
- When `agents/session.md` in conflict list: extract new tasks from `:3:agents/session.md` (theirs)
- New tasks: lines matching `- [ ] **<name>**` pattern that don't exist in `:2:agents/session.md` (ours)
- Resolution: run `git checkout --ours agents/session.md && git add agents/session.md`
- Warning printed with list of new tasks for manual extraction
- Warning message actionable (helps user transfer tasks manually)

**Expected failure:** AssertionError: session.md conflict not resolved, or no task extraction warning

**Why it fails:** session.md auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_session_md -v`

---

**GREEN Phase:**

**Implementation:** Add session.md conflict auto-resolution with task extraction

**Behavior:**
- From 7.7: have conflict list
- Check if `"agents/session.md"` in conflict list
- If present:
  - Extract ours tasks: `git show :2:agents/session.md | grep "- [ ] \*\*.*\*\*"`
  - Extract theirs tasks: `git show :3:agents/session.md | grep "- [ ] \*\*.*\*\*"`
  - Find new tasks (in theirs, not in ours)
  - Run `git checkout --ours agents/session.md && git add agents/session.md`
  - Print warning with new task list
- Remove from conflict list after resolution

**Approach:** git show for stage extraction, grep/parsing for task detection, warning output

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add session.md conflict check in `merge` command
  Location hint: After agent-core resolution from 7.8
- File: `src/claudeutils/worktree/cli.py`
  Action: Extract tasks from both sides using git show
  Location hint: Use subprocess to get `:2:` and `:3:` content
- File: `src/claudeutils/worktree/cli.py`
  Action: Find new tasks (set difference)
  Location hint: Compare task lists
- File: `src/claudeutils/worktree/cli.py`
  Action: Resolve with --ours and print warning
  Location hint: Checkout ours, add, print new tasks

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_session_md -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 tests still pass

---

## Cycle 7.10: Phase 3 conflict handling — learnings.md auto-resolve (append theirs-only)

**Objective:** Auto-resolve learnings.md conflicts by keeping both (append theirs-only content to ours).

**RED Phase:**

**Test:** `test_merge_conflict_learnings_md`
**Assertions:**
- When `agents/learnings.md` in conflict list: append theirs-only content to ours
- Extract ours: `git show :2:agents/learnings.md`
- Extract theirs: `git show :3:agents/learnings.md`
- Find theirs-only lines (in theirs, not in ours)
- Result: ours content + separator + theirs-only content
- Write merged result and stage: `git add agents/learnings.md`

**Expected failure:** AssertionError: learnings.md conflict not resolved, or wrong merge strategy (not both-sides)

**Why it fails:** learnings.md auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_learnings_md -v`

---

**GREEN Phase:**

**Implementation:** Add learnings.md conflict auto-resolution (append theirs-only)

**Behavior:**
- From 7.7: have conflict list
- Check if `"agents/learnings.md"` in conflict list
- If present:
  - Extract ours: `git show :2:agents/learnings.md`
  - Extract theirs: `git show :3:agents/learnings.md`
  - Find theirs-only lines (line-by-line comparison)
  - Compose result: ours + theirs-only lines
  - Write to `agents/learnings.md`
  - Run `git add agents/learnings.md`
- Remove from conflict list after resolution

**Approach:** git show for stage extraction, line-by-line diff, file write and stage

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add learnings.md conflict check in `merge` command
  Location hint: After session.md resolution from 7.9
- File: `src/claudeutils/worktree/cli.py`
  Action: Extract both sides using git show
  Location hint: Use subprocess to get `:2:` and `:3:` content
- File: `src/claudeutils/worktree/cli.py`
  Action: Find theirs-only lines (set difference on lines)
  Location hint: Split into lines, compare
- File: `src/claudeutils/worktree/cli.py`
  Action: Write merged result and stage
  Location hint: Write to file, git add

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_learnings_md -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 tests still pass

---

## Cycle 7.11: Phase 3 conflict handling — jobs.md auto-resolve

**Objective:** Auto-resolve jobs.md conflicts by keeping ours with warning (plan status is local state).

**RED Phase:**

**Test:** `test_merge_conflict_jobs_md`
**Assertions:**
- When `agents/jobs.md` in conflict list: run `git checkout --ours agents/jobs.md && git add agents/jobs.md`
- After resolution: `agents/jobs.md` removed from conflict list
- Warning printed: "jobs.md conflict: kept ours (local plan status)"
- No manual intervention required

**Expected failure:** AssertionError: jobs.md conflict not resolved, or no warning

**Why it fails:** jobs.md auto-resolution not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_jobs_md -v`

---

**GREEN Phase:**

**Implementation:** Add jobs.md conflict auto-resolution

**Behavior:**
- From 7.7: have conflict list
- Check if `"agents/jobs.md"` in conflict list
- If present: run `git checkout --ours agents/jobs.md` then `git add agents/jobs.md`
- Print warning: "jobs.md conflict: kept ours (local plan status)"
- Remove from conflict list after resolution

**Approach:** Same pattern as agent-core resolution (7.8) — known-file auto-resolve with warning

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add jobs.md conflict check in `merge` command
  Location hint: After learnings.md resolution from 7.10, before source file abort
- File: `src/claudeutils/worktree/cli.py`
  Action: Run checkout --ours and git add for jobs.md
  Location hint: Conditional on conflict list membership

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_jobs_md -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 conflict handling tests still pass

---

## Cycle 7.12: Phase 3 conflict handling — source file abort

**Objective:** Abort merge and clean debris when source file conflicts remain (manual resolution required).

**RED Phase:**

**Test:** `test_merge_conflict_source_files`
**Assertions:**
- When conflicts remain after auto-resolution (not agent-core, session.md, learnings.md, jobs.md): abort merge
- Run `git merge --abort` to cancel merge
- Clean debris: `git clean -fd` to remove materialized files from merge attempt
- Exit 1 with conflict list: "Merge aborted: conflicts in <file1>, <file2>"
- Exit code 1 (conflicts require manual resolution, not fatal error)

**Expected failure:** AssertionError: merge proceeds with unresolved conflicts, or no abort/cleanup

**Why it fails:** Source file conflict handling not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_conflict_source_files -v`

---

**GREEN Phase:**

**Implementation:** Add source file conflict abort logic

**Behavior:**
- After 7.8-7.11 auto-resolutions: check if conflict list still non-empty
- Run `git diff --name-only --diff-filter=U` again to get remaining conflicts
- If conflicts remain:
  - Run `git merge --abort`
  - Run `git clean -fd` to remove debris
  - Exit 1 with message listing conflicted files
- If no conflicts remain (all auto-resolved): proceed to commit

**Approach:** Final conflict check, abort and cleanup if any remain, exit with message

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add final conflict check in `merge` command
  Location hint: After all auto-resolutions (7.8-7.11)
- File: `src/claudeutils/worktree/cli.py`
  Action: Recheck conflict list with git diff
  Location hint: Run same command as 7.7
- File: `src/claudeutils/worktree/cli.py`
  Action: If conflicts remain: abort merge and clean
  Location hint: `git merge --abort && git clean -fd`
- File: `src/claudeutils/worktree/cli.py`
  Action: Exit 1 with conflict list
  Location hint: Print message and sys.exit(1)

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_conflict_source_files -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 3 conflict handling tests still pass

---

## Cycle 7.13: Phase 4 precommit validation — run and check exit code

**Objective:** Run precommit validation after successful merge, exit 1 on failure.

**RED Phase:**

**Test:** `test_merge_precommit_validation`
**Assertions:**
- After successful merge (no conflicts): commit with message `🔀 Merge <slug>`
- Only commit if staged changes exist (check `git diff --cached --quiet`)
- Then run `just precommit` (capture exit code and stderr)
- If precommit passes (exit 0): exit 0 with success message
- If precommit fails (exit ≠ 0): exit 1 with message "Precommit failed after merge" + stderr
- Exit codes: 0 (success), 1 (conflicts or precommit failure), 2 (fatal error)

**Expected failure:** AssertionError: no precommit run, or wrong exit code, or no commit before precommit

**Why it fails:** Phase 4 precommit validation not implemented

**Verify RED:** `pytest tests/test_worktree_cli.py::test_merge_precommit_validation -v`

---

**GREEN Phase:**

**Implementation:** Add merge commit and precommit validation

**Behavior:**
- After conflict resolution (or clean merge from 7.7): check for staged changes
- Run `git diff --cached --quiet` (exit ≠ 0 means changes staged)
- If staged changes: `git commit -m "🔀 Merge <slug>"`
- If no staged changes: skip commit (no-op merge)
- Then run `just precommit` with `check=False` (capture exit code and stderr)
- If exit code 0: print success, exit 0
- If exit code ≠ 0: print failure message with stderr, exit 1

**Approach:** Staged changes check, commit, precommit run, exit code handling

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add merge commit in `merge` command (Phase 4 start)
  Location hint: After Phase 3 conflict handling
- File: `src/claudeutils/worktree/cli.py`
  Action: Check for staged changes before commit
  Location hint: `git diff --cached --quiet`, commit if exit ≠ 0
- File: `src/claudeutils/worktree/cli.py`
  Action: Run `just precommit` and capture result
  Location hint: subprocess with check=False
- File: `src/claudeutils/worktree/cli.py`
  Action: Handle precommit result (success message or failure exit)
  Location hint: Conditional on exit code

**Verify GREEN:** `pytest tests/test_worktree_cli.py::test_merge_precommit_validation -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_cli.py -v`
- All Phase 7 tests still pass

---

**Checkpoint: Post-Phase 7**

**Type:** Full checkpoint (Fix + Vet + Functional)

**Process:**
1. **Fix:** Run `just dev`. If failures, sonnet quiet-task diagnoses and fixes. Commit when passing.
2. **Vet:** Review all Phase 1-7 changes for quality, clarity, design alignment. Apply all fixes. Commit.
3. **Functional:** Review all implementations against design.
   - Check: Is 4-phase ceremony implemented completely? Do auto-resolutions actually work?
   - Check: Are exit codes correct (0=success, 1=conflicts/precommit, 2=fatal)?
   - Check: Is session.md task extraction correct (regex matching, theirs-only detection)?
   - If stubs found: STOP, report which implementations need real behavior
   - If all functional: TDD implementation complete, proceed to Phase 8 (non-code artifacts)

**Rationale:** Phase 7 completes TDD implementation. Final full checkpoint validates all 37 TDD cycles before non-code artifacts.
