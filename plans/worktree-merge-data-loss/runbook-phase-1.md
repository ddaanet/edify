# Phase 1: Core Implementation (TDD)

**Type:** tdd
**Model:** haiku
**Scope:** Track 1 (removal guard), Track 2 (merge correctness), shared helpers

---

## Cycle 1.1: Shared helper — `_is_branch_merged(slug)` in utils.py

**Type:** Creation

**Prerequisite:** Read `src/claudeutils/worktree/utils.py` (lines 1-38) — understand existing helpers (`_git`, `wt_path`) and module structure.

**RED Phase:**

**Test:** `test_is_branch_merged` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- For merged branch: `_is_branch_merged("merged-branch")` returns `True`
- For unmerged branch: `_is_branch_merged("unmerged-branch")` returns `False`
- Set up: Create branch, commit to main (branch becomes ancestor), verify True
- Set up: Create branch, commit to branch (not merged), verify False

**Expected failure:** `ImportError` or `AttributeError` — function doesn't exist

**Why it fails:** `_is_branch_merged` not implemented in utils.py

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_is_branch_merged -v`

**GREEN Phase:**

**Implementation:** Add `_is_branch_merged(slug: str) -> bool` to utils.py

**Behavior:**
- Execute `git merge-base --is-ancestor <slug> HEAD`
- Return True if exit code 0 (branch is ancestor of HEAD)
- Return False if exit code 1 (branch not ancestor)
- Use `subprocess.run` directly (not `_git()`) — `_git()` returns `stdout.strip()`, not returncode. Codebase pattern for exit code checks uses `subprocess.run` directly (see merge.py line 269, cli.py line 370).

**Approach:** Single subprocess call with exit code check. Design specifies this exact command (design.md line 41).

**Changes:**
- File: `src/claudeutils/worktree/utils.py`
  Action: Add function after `wt_path()`, before EOF
  Location hint: After line 38

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_is_branch_merged -v`
**Verify no regression:** `pytest tests/test_worktree_utils.py -v`

---

## Cycle 1.2: Branch classification — `_classify_branch(slug)` returns count and focused flag

**Type:** Creation

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` (lines 154-178) — understand marker text format `"Focused session for {slug}"` from `_create_session_commit`.

**RED Phase:**

**Test:** `test_classify_branch` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Focused-session-only branch (1 commit with marker): returns `(1, True)`
- Real-history branch (1 user commit): returns `(1, False)`
- Multi-commit branch (3 commits): returns `(3, False)`
- Set up: Create branch, make N commits, verify count
- Set up: Create branch with exact marker text `"Focused session for test-branch"`, verify focused=True
- Set up: Create branch with similar but different message `"Focused session test-branch"` (no "for"), verify focused=False

**Expected failure:** `AttributeError` — function doesn't exist

**Why it fails:** `_classify_branch` not implemented in cli.py

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`

**GREEN Phase:**

**Implementation:** Add `_classify_branch(slug: str) -> tuple[int, bool]` to cli.py

**Behavior:**
- Get merge-base between HEAD and slug: `git merge-base HEAD <slug>`
- Count commits: `git rev-list --count <merge_base>..<slug>`
- If count == 1: get commit message: `git log -1 --format=%s <slug>`
- Check if message matches exactly: `f"Focused session for {slug}"`
- Return (count, is_focused)

**Approach:** Three git commands in sequence. Design specifies exact logic (design.md lines 46-53).

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add helper function near other rm-related code
  Location hint: Before `rm()` function (before line 347)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`
**Verify no regression:** `pytest tests/test_worktree_rm.py -v`

---

## Cycle 1.3: Classification edge case — orphan branch (merge-base failure)

**Type:** Transformation

**RED Phase:**

**Test:** `test_classify_orphan_branch` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create orphan branch (no common ancestor with HEAD): `git checkout --orphan orphan-test`
- Commit on orphan branch (unrelated history)
- Call `_classify_branch("orphan-test")`: returns `(0, False)`
- Rationale: Design specifies orphan returns `(0, False)` to be treated as real history (design.md line 55)

**Expected failure:** `subprocess.CalledProcessError` or incorrect return value (undefined behavior)

**Why it fails:** `merge-base` fails when no common ancestor exists, code doesn't handle this

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_classify_orphan_branch -v`

**GREEN Phase:**

**Implementation:** Add error handling to `_classify_branch`

**Behavior:**
- Wrap `merge-base` call in try-except
- If `merge-base` raises `subprocess.CalledProcessError` (no common ancestor)
- Return `(0, False)` — treat as real history

**Approach:** Catch subprocess exception from `_git()` when merge-base fails

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Modify `_classify_branch` to handle merge-base failure
  Location hint: Around merge-base call in function body

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_classify_orphan_branch -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py::test_classify_branch -v`

---

## Cycle 1.4: Guard refuses unmerged real history (exit 1, stderr message with count)

**Type:** Creation

**Prerequisite:** Read `src/claudeutils/worktree/cli.py` (lines 347-382) — understand current `rm()` flow and structure.

**RED Phase:**

**Test:** `test_rm_refuses_unmerged_real_history` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Scenario A (real history): Create branch with 2 unmerged commits (not focused-session marker)
  - Call `worktree rm <slug>` via CliRunner
  - Exit code is 1 (refused)
  - Stderr contains: `"Branch {slug} has 2 unmerged commit(s). Merge first."`
  - Worktree directory still exists (not removed)
  - Branch still exists: `git rev-parse --verify <slug>` succeeds
- Scenario B (orphan): Create orphan branch (`git checkout --orphan`), commit on it
  - Call `worktree rm <slug>` via CliRunner
  - Exit code is 1 (refused)
  - Stderr contains: `"Branch {slug} is orphaned (no common ancestor). Merge first."`
  - Branch still exists

**Expected failure:** Exit code 0 (current behavior proceeds with removal) for both scenarios

**Why it fails:** Guard logic not implemented — rm proceeds unconditionally

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_refuses_unmerged_real_history -v`

**GREEN Phase:**

**Implementation:** Add guard logic to `rm()` in cli.py

**Behavior:**
- Before ANY destructive operations (before `_probe_registrations`)
- Check if branch exists: `git rev-parse --verify <slug>`
- If branch exists:
  - Check if merged: `_is_branch_merged(slug)` (from Cycle 1.1)
  - If not merged:
    - Get classification: `_classify_branch(slug)` (from Cycle 1.2)
    - If not focused-session-only (count != 1 or not focused):
      - If count == 0 (orphan): stderr `"Branch {slug} is orphaned (no common ancestor). Merge first."`
      - Else: stderr `"Branch {slug} has {count} unmerged commit(s). Merge first."`
      - Exit 1
- Proceed with removal (existing flow)

**Approach:** Insert guard block at function start. Design specifies exact flow (design.md lines 60-74).

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Insert guard logic at start of `rm()` function
  Location hint: After function docstring, before line 351

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_refuses_unmerged_real_history -v`
**Verify no regression:** `pytest tests/test_worktree_rm.py -v`

---

## Cycle 1.5: Guard allows merged branch removal (exit 0, `git branch -d` safe delete, "Removed {slug}")

**Type:** Transformation

**RED Phase:**

**Test:** `test_rm_allows_merged_branch` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create branch, commit changes, merge to main (branch becomes merged)
- Call `worktree rm <slug>` via CliRunner
- Exit code is 0 (success)
- Branch deleted: `git rev-parse --verify <slug>` fails
- Stdout contains: `"Removed {slug}"` (no qualifier like "focused session only")
- Branch was merged before deletion (safe delete with `-d` succeeds for merged branches; no force required)

**Expected failure:** Output contains `"Removed worktree {slug}"` instead of expected `"Removed {slug}"` (current code at line 382 includes "worktree" in message)

**Why it fails:** Current rm outputs `"Removed worktree {slug}"` (line 382) — test asserts `"Removed {slug}"` without "worktree" qualifier. Also, current code has no per-branch-type message differentiation.

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_merged_branch -v`

**GREEN Phase:**

**Implementation:** Update rm() to use `-d` for merged branches and appropriate message

**Behavior:**
- After guard passes (branch is merged or focused-session-only)
- For merged branches: use `git branch -d <slug>` (safe delete)
- Success message: `"Removed {slug}"` (design.md line 81)

**Approach:** Modify existing branch deletion code (lines 369-373) to track merge status and use appropriate flags/messages

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Update branch deletion to use `-d` for merged, differentiate messages
  Location hint: Lines 369-373 (current branch delete) and line 382 (current success message)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_merged_branch -v`
**Verify no regression:** `pytest tests/test_worktree_rm.py -v`

---

## Cycle 1.6: Guard allows focused-session-only removal (exit 0, `git branch -D` force delete, "Removed {slug} (focused session only)")

**Type:** Transformation

**RED Phase:**

**Test:** `test_rm_allows_focused_session_only` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create branch with exactly 1 commit having marker text: `"Focused session for test-branch"`
- Branch is NOT merged (unmerged but allowed due to focused-session marker)
- Call `worktree rm <slug>` via CliRunner
- Exit code is 0 (success)
- Branch deleted: `git rev-parse --verify <slug>` fails
- Stdout contains: `"Removed {slug} (focused session only)"` (design.md line 82)
- Branch deleted despite being unmerged (force delete required — `-d` alone would fail for unmerged branch)

**Expected failure:** Exit code 1 (guard refuses) or wrong message/deletion method

**Why it fails:** Guard from Cycle 1.4 blocks all unmerged branches; need exception for focused-session-only

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_focused_session_only -v`

**GREEN Phase:**

**Implementation:** Update guard to allow focused-session-only branches

**Behavior:**
- In guard logic (from Cycle 1.4):
  - If branch not merged AND focused-session-only (count == 1 and focused == True):
    - Allow removal to proceed
  - Track removal type: set local variable `removal_type` (`"merged"` or `"focused"`) before proceeding — used by branch deletion code (Cycles 1.5-1.6) to choose `-d` vs `-D` flag and success message
- For focused-session-only: use `git branch -D <slug>` (force delete)
- Success message: `"Removed {slug} (focused session only)"`

**Approach:** Modify guard conditional from Cycle 1.4 to pass through focused branches; update branch deletion to use `-D` flag when appropriate

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Update guard conditional (from 1.4) to allow focused branches; modify branch deletion to use `-D` for focused-only
  Location hint: Guard block + branch deletion (lines ~351-373)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_allows_focused_session_only -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py::test_rm_refuses_unmerged_real_history -v`

---

## Cycle 1.7: Guard integration — cli.py rm() calls guard before all destructive operations

**Type:** Transformation

**Dependencies:** Requires Cycles 1.1-1.6 complete

**RED Phase:**

**Test:** `test_rm_guard_prevents_destruction` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Create branch with unmerged real history (2 commits, not focused)
- Create worktree directory on disk
- Add worktree task to session.md
- Call `worktree rm <slug>`
- Exit code is 1 (guard refused)
- **Negative assertions (regression test for incident):**
  - Worktree directory still exists on disk
  - Branch still exists
  - Session.md task NOT removed
  - `_probe_registrations` NOT called (verify via side effect absence: no worktree prune or removal occurred)

**Expected failure:** Side effects occur despite guard refusal — session.md task removed, worktree directory deleted, or `_probe_registrations` called. This tests the integration ordering, not the guard logic itself (which was added in Cycles 1.4-1.6).

**Why it fails:** Even with guard logic from Cycles 1.4-1.6, the rm() function structure may allow downstream operations to execute before the guard's early return. This cycle verifies the complete ordering: guard refusal prevents ALL downstream side effects (the original incident's root cause).

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_guard_prevents_destruction -v`

**GREEN Phase:**

**Implementation:** Reorder rm() to execute guard FIRST

**Behavior:**
- New rm() flow: `check_exists → guard → probe → warn → remove_session_task → remove_worktrees → branch -d/-D → rmtree → clean`
- Guard block from Cycles 1.4-1.6 executes before line 351 (`worktree_path = wt_path(slug)`)
- When guard exits 1, NONE of the following execute:
  - `_probe_registrations`
  - `remove_worktree_task`
  - `_remove_worktrees`
  - `shutil.rmtree`
  - `git branch -d/-D`

**Approach:** Restructure rm() function — guard at top, existing operations below

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Move guard logic (from 1.4-1.6) to function start; ensure early exit prevents all downstream operations
  Location hint: Entire rm() function (lines 347-382)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_guard_prevents_destruction -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py -v` (all Track 1 tests)

---

## Cycle 1.8: No `git branch -D` in output — verify no destructive suggestions in stderr/stdout

**Type:** Transformation (Regression guard)

**Note:** This is a regression guard for FR-5 (design.md line 24). Current code emits `"use: git branch -D {slug}"` in the branch delete fallback. After Cycles 1.4-1.7 restructure rm(), this old fallback code is obsolete — the guard handles all branch deletion paths with appropriate flags. This cycle removes the obsolete code and tests that no destructive suggestions remain.

**RED Phase:**

**Test:** `test_rm_no_destructive_suggestions` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Test three scenarios: merged branch removal, focused-session removal, guard refusal
- For each scenario: capture stdout and stderr
- Assert `"git branch -D"` NOT in stdout
- Assert `"git branch -D"` NOT in stderr
- Run against CURRENT code to verify RED failure

**Expected failure:** Output contains `"git branch -D"` string from old branch delete fallback code (cli.py:373). The focused-session scenario is most likely to trigger it: the branch is unmerged, so the old `git branch -d` at line 369 fails, and line 373 emits the destructive suggestion. If Cycles 1.5-1.6 already replaced this code path, RED may pass for all scenarios — in that case, the GREEN phase is a no-op cleanup verification and the test remains as a regression guard.

**Why it fails:** Old branch delete fallback code still present — emits destructive suggestion when `-d` fails for unmerged branches

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_no_destructive_suggestions -v`

**GREEN Phase:**

**Implementation:** Remove destructive suggestion from rm() output

**Behavior:**
- Remove the old branch delete fallback block (`subprocess.run(["git", "branch", "-d", slug])` + error message suggesting `-D`)
- Guard (Cycles 1.4-1.6) now handles all branch deletion scenarios with appropriate flags (`-d` for merged, `-D` for focused-session-only)
- No CLI output should suggest manual git commands

**Approach:** Delete obsolete branch deletion code — guard replacement makes it redundant

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Remove old branch delete fallback block (the `subprocess.run` with `-d` and its error message)
  Location hint: Branch deletion section (may have shifted from original line 369 due to Cycles 1.4-1.7 edits)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_no_destructive_suggestions -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py -v` (full Track 1 suite)

---

## Cycle 1.9: MERGE_HEAD checkpoint — Phase 4 refuses single-parent commit when branch unmerged (exit 2, "merge state lost" message)

**Type:** Transformation

**Dependencies:** Requires Cycle 1.1 (`_is_branch_merged` in utils.py)

**Prerequisite:** Read `src/claudeutils/worktree/merge.py` (lines 261-299) — understand current Phase 4 logic (two-branch: MERGE_HEAD present vs staged changes present).

**RED Phase:**

**Test:** `test_phase4_refuses_single_parent_when_unmerged` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Set up: Create branch, make changes, initiate merge (Phases 1-3)
- Simulate MERGE_HEAD loss: remove `.git/MERGE_HEAD` after Phase 3
- Staged changes still present (merge did stage files)
- Branch is NOT merged (verified via `_is_branch_merged`)
- Call `_phase4_merge_commit_and_precommit(slug)`
- Exit code is 2 (error)
- Stderr contains: `"Error: merge state lost — MERGE_HEAD absent, branch not merged"`
- NO commit created: `git log -1 --format=%s` shows commit BEFORE Phase 4 call

**Expected failure:** Exit code 0 with single-parent commit (current behavior: `elif` at line 284 creates commit)

**Why it fails:** Current code creates commit when staged changes present, regardless of merge status

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_refuses_single_parent_when_unmerged -v`

**GREEN Phase:**

**Implementation:** Add checkpoint to Phase 4 `elif` branch

**Behavior:**
- Current flow: `if merge_in_progress → commit; elif staged → commit`
- New flow: `if merge_in_progress → commit; elif staged → check branch merged → if merged: commit, else: exit 2`
- Import `_is_branch_merged` from utils.py
- In `elif staged_check.returncode != 0:` block (line 284):
  - Before creating commit, check: `if not _is_branch_merged(slug): stderr + exit 2`
  - If merged: proceed with commit (idempotent case)

**Approach:** Insert merge check before commit in `elif` branch. Design specifies exact logic (design.md lines 105-109).

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add import for `_is_branch_merged`; insert checkpoint in `elif` block
  Location hint: Line 284 (inside `elif staged_check.returncode != 0:`)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_refuses_single_parent_when_unmerged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_merge_head.py -v`

---

## Cycle 1.10: [REGRESSION] Already-merged idempotency — Phase 4 allows commit when branch already merged (exit 0)

**Type:** Transformation (regression guard for Cycle 1.9)

**Note:** Cycle 1.9's implementation (`if not _is_branch_merged(slug): exit 2`) already handles the already-merged case correctly — merged branches pass the check and proceed to commit. This cycle verifies that behavior explicitly as a regression guard. The RED phase test should PASS against Cycle 1.9's implementation.

**RED Phase:**

**Test:** `test_phase4_allows_already_merged` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Set up: Create branch, merge to main (branch becomes merged)
- Stage changes (simulate re-merge with staged content)
- No MERGE_HEAD (already merged)
- Call `_phase4_merge_commit_and_precommit(slug)`
- Exit code is 0 (success)
- Commit created with staged changes

**Expected result:** Test PASSES against Cycle 1.9 implementation (regression guard — verifies `_is_branch_merged` correctly allows merged branches through the `elif` path)

**Why this test exists:** Documents and locks the idempotent behavior. If a future change to the `elif` branch breaks the merge check, this test catches it.

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_allows_already_merged -v` (expected: PASS)

**GREEN Phase:**

**Implementation:** No additional code needed — Cycle 1.9's `if not _is_branch_merged(slug)` handles this

**Behavior:**
- `elif staged_check.returncode != 0:` → checks `_is_branch_merged(slug)`
- If merged: creates commit (idempotent — re-merging already-merged branch)
- If not merged: exits 2 (Cycle 1.9 behavior)

**Changes:**
- File: `tests/test_worktree_merge_correctness.py`
  Action: Regression test verifies Cycle 1.9 implementation allows merged branches
  Location hint: N/A (test-only cycle)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_allows_already_merged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_refuses_single_parent_when_unmerged -v`

---

## Cycle 1.11: No MERGE_HEAD + no staged changes — exit 2 if branch unmerged, skip if merged

**Type:** Transformation

**RED Phase:**

**Test:** `test_phase4_handles_no_merge_head_no_staged` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Scenario A (unmerged): Branch exists, no MERGE_HEAD, no staged changes, branch NOT merged
  - Call `_phase4_merge_commit_and_precommit(slug)`
  - Exit code is 2
  - Stderr contains: `"Error: nothing to commit and branch not merged"`
  - No commit created
- Scenario B (merged): Branch exists, no MERGE_HEAD, no staged changes, branch IS merged
  - Call `_phase4_merge_commit_and_precommit(slug)`
  - Exit code is 0 (success)
  - No commit created (skip — already merged, nothing to do)
  - Stdout contains: (no error message)

**Expected failure:** Both scenarios fall through with no action (current code: no `else` branch after line 285)

**Why it fails:** Current code has no `else` branch to handle no-MERGE_HEAD + no-staged case

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_handles_no_merge_head_no_staged -v`

**GREEN Phase:**

**Implementation:** Add `else` branch to Phase 4 commit logic

**Behavior:**
- After `if merge_in_progress:` and `elif staged_check.returncode != 0:`
- Add `else:` (no MERGE_HEAD, no staged changes)
  - Check if branch merged: `_is_branch_merged(slug)`
  - If merged: skip commit (nothing to commit — already merged). Function continues to validation/precommit.
  - If not merged: stderr `"Error: nothing to commit and branch not merged"` + exit 2

**Approach:** Add third branch to handle edge case. Design specifies exact logic (design.md lines 111-115).

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add `else:` block after `elif` (line 285)
  Location hint: After the `elif staged_check.returncode != 0:` block

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_phase4_handles_no_merge_head_no_staged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_correctness.py -v` (all Phase 4 logic tests)

---

## Cycle 1.12: Post-merge ancestry validation — `_validate_merge_result(slug)` called after commit, verifies slug is ancestor of HEAD

**Type:** Creation

**RED Phase:**

**Test:** `test_validate_merge_result` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Scenario A (valid merge): Create branch, merge properly, slug IS ancestor of HEAD
  - Call `_validate_merge_result(slug)`
  - Exit code is 0 (success — validation passes)
  - No stderr output
- Scenario B (invalid merge): Simulate incomplete merge (slug NOT ancestor of HEAD)
  - Call `_validate_merge_result(slug)`
  - Exit code is 2 (error)
  - Stderr contains: `"Error: branch {slug} not fully merged"`
- Scenario C (diagnostic): After single-parent commit, call `_validate_merge_result(slug)` where ancestry passes
  - Stderr contains: `"Warning: merge commit has 1 parent(s)"` (parent count < 2 diagnostic)

**Expected failure:** `AttributeError` or `ImportError` — function doesn't exist

**Why it fails:** `_validate_merge_result` not implemented in merge.py

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_validate_merge_result -v`

**GREEN Phase:**

**Implementation:** Add `_validate_merge_result(slug: str) -> None` to merge.py AND wire it into `_phase4_merge_commit_and_precommit`

**Behavior:**
- Execute `git merge-base --is-ancestor <slug> HEAD` (same check as `_is_branch_merged`)
- If exit code 0: validation passes, return
- If exit code != 0: stderr `"Error: branch {slug} not fully merged"` + exit 2
- Also emit diagnostic logging for parent count when < 2:
  - `git cat-file -p HEAD` → count lines starting with "parent "
  - If parent_count < 2: stderr `"Warning: merge commit has {parent_count} parent(s)"`

**Integration wiring:** Call `_validate_merge_result(slug)` in `_phase4_merge_commit_and_precommit` after the commit block (after `if merge_in_progress` / `elif staged` / `else`) but before `just precommit`. Design specifies this placement (design.md line 155: "validate ancestry after any successful commit or skip, then precommit").

**Approach:** Defensive check using merge-base. Design specifies exact command (design.md lines 125-132, 137-143).

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add function after existing helper functions, before `_phase4_merge_commit_and_precommit`; add call to `_validate_merge_result(slug)` in `_phase4_merge_commit_and_precommit` after commit block, before precommit
  Location hint: Function near other Phase 4 helpers; call site between commit block and `just precommit` (line 287)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_validate_merge_result -v`
**Verify no regression:** `pytest tests/test_worktree_merge_*.py -v`
**Verify existing tests:** `pytest tests/test_worktree_merge_merge_head.py -v` (existing Phase 4 tests must still pass after wiring)

---

## Cycle 1.13: Parent repo file preservation — end-to-end test: branch with parent + submodule changes → merge → verify all files present in HEAD

**Type:** Integration (regression test for original incident)

**Dependencies:** Requires Cycles 1.9-1.12 complete (full Phase 4 modifications)

**Note:** This test may pass even without fixes if the original bug was environment-specific (design.md line 204). The test has value as a regression guard.

**RED Phase:**

**Test:** `test_merge_preserves_parent_repo_files` in `tests/test_worktree_merge_correctness.py`

**Assertions:**
- Set up: Create worktree branch
- In worktree: Add parent repo file (`parent-change.txt` in repo root, NOT in submodule)
- In worktree: Add submodule change (`agent-core/submodule-change.txt`)
- Commit both changes in worktree
- Switch to main, run full merge (Phases 1-4)
- Verify parent repo file exists in main after merge: `Path("parent-change.txt").exists()`
- Verify submodule file exists: `Path("agent-core/submodule-change.txt").exists()`
- Verify merge commit has 2 parents: `git log -1 --format=%p HEAD` → two parent hashes
- Verify branch is ancestor of HEAD: `git merge-base --is-ancestor <slug> HEAD` succeeds

**Expected failure:** Parent repo file missing (reproduces original incident) OR test passes (incident was environment-specific)

**Why it fails (if it fails):** Original bug: Phase 4 created single-parent commit, dropping parent changes

**Verify RED:** `pytest tests/test_worktree_merge_correctness.py::test_merge_preserves_parent_repo_files -v`

**GREEN Phase:**

**Implementation:** Phase 4 modifications from Cycles 1.9-1.12 prevent single-parent commits

**Behavior:**
- MERGE_HEAD checkpoint (Cycle 1.9): refuses commit if MERGE_HEAD absent and branch unmerged
- Ancestry validation (Cycle 1.12): verifies branch is ancestor after commit
- Defense-in-depth: both checks catch the single-parent bug from different angles

**Approach:** No additional code — test verifies Cycles 1.9-1.12 collectively prevent data loss

**Changes:**
- File: `tests/test_worktree_merge_correctness.py`
  Action: Integration test exercises full merge flow
  Location hint: N/A (test-only cycle)

**Verify GREEN:** `pytest tests/test_worktree_merge_correctness.py::test_merge_preserves_parent_repo_files -v`
**Verify no regression:** `pytest tests/test_worktree_merge_*.py -v` (all merge tests including existing)

---

## Checkpoint: Light Checkpoint (Fix + Functional)

**Placement:** After Cycle 1.13 (end of Phase 1)

**Process:**

1. **Fix:** Run `just dev`
   - If failures: sonnet quiet-task diagnoses and fixes
   - Commit when passing

2. **Functional:** Sonnet reviews implementations against design
   - Check: Real implementations or stubs?
   - For each function (`_is_branch_merged`, `_classify_branch`, `_validate_merge_result`, guard logic):
     - Does it compute real results or return constants?
     - Does it execute actual git operations?
   - If stubs found: STOP, report which need real behavior
   - If all functional: proceed

**Rationale:** Light checkpoint (not full) because Phase 1 is all implementation, no architectural changes.

