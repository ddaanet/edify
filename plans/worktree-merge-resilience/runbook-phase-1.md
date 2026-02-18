## Phase 1: State detection + idempotent resume (type: tdd)

**Goal:** Add `_detect_merge_state(slug)` to `merge.py` and rewrite `merge()` entry to route based on detected state. Enables Phases 2–4 to be exercised independently (resume from mid-merge state).

**Files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_merge_head.py`

**Common context for all cycles:**
- `_detect_merge_state(slug)` returns a string: `"merged"`, `"parent_resolved"`, `"parent_conflicts"`, `"submodule_conflicts"`, or `"clean"`
- Detection order matters (D-5): check in order merged → submodule_conflicts → parent_resolved → parent_conflicts → clean
- All test repos: real git, no mocks. Use `tmp_path`, set git user.name/email. Use `mock_precommit` fixture for all cycles.
- `merged` detection: `_is_branch_merged(slug)` (already in utils.py)
- `parent_resolved`/`parent_conflicts` detection: `git rev-parse --verify MERGE_HEAD` (0 = MERGE_HEAD exists)
- Conflict presence: `git diff --name-only --diff-filter=U` (non-empty = unresolved conflicts)
- `submodule_conflicts` detection: `git -C agent-core rev-parse --verify MERGE_HEAD`

---

## Cycle 1.1: `_detect_merge_state` identifies `merged` state

**RED Phase:**

**Test:** `test_detect_state_merged`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- `_detect_merge_state("branch")` returns `"merged"` when branch is already an ancestor of HEAD
- Returns `"clean"` for same repo before branch is merged (control assertion)

**Expected failure:** `ImportError` — `_detect_merge_state` does not yet exist in `merge.py`

**Why it fails:** Function not implemented.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_detect_state_merged -v`

**Test setup:** Create repo, add a commit on a branch, merge it into main with `git merge --no-edit branch`. Monkeypatch chdir. Call `_detect_merge_state("branch")` directly (import from `claudeutils.worktree.merge`).

**GREEN Phase:**

**Implementation:** Add `_detect_merge_state(slug: str) -> str` to `merge.py` with only the `merged` and `clean` states. Submodule and parent MERGE_HEAD checks are added in later cycles.

**Behavior:**
- Check `_is_branch_merged(slug)` (already in utils.py) — return `"merged"` if True
- Otherwise return `"clean"`

Note: Detection of `submodule_conflicts`, `parent_resolved`, and `parent_conflicts` states is added in Cycles 1.2 and 1.4. This minimal implementation is sufficient to pass Cycle 1.1's test.

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add `_detect_merge_state(slug: str) -> str` function near top of file (after existing helpers, before `_phase1_validate_clean_trees`)
  Location hint: After `_format_git_error`, before `_check_clean_for_merge`

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_detect_state_merged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_merge_head.py -v`

---

## Cycle 1.2: `merge()` routes `parent_resolved` state to Phase 4

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:67-90` — understand `_check_clean_for_merge` which currently prevents resume from mid-merge state.

**RED Phase:**

**Test:** `test_merge_resumes_from_parent_resolved`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- Exit code is 0 when `merge(slug)` called on repo with MERGE_HEAD + no unresolved conflicts
- A merge commit is created (HEAD has 2+ parents after call)
- No `CalledProcessError` from clean-tree check

**Expected failure:** `SystemExit(1)` — current `_phase1_validate_clean_trees` calls `_check_clean_for_merge` which detects staged changes (from the manually resolved merge) and exits 1 with "Clean tree required"

**Why it fails:** Phase 1 validation rejects staged files even though they belong to an in-progress merge.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_resumes_from_parent_resolved -v`

**Test setup:**
1. Create repo with branch that has a unique file (`branch-file.txt`) and main that has a conflicting change in another file
2. Start merge manually: `subprocess.run(["git", "merge", "--no-commit", "--no-ff", slug], ...)`
3. All auto-resolved — `git diff --name-only --diff-filter=U` returns empty (no conflicts)
4. Use `mock_precommit` fixture. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit 0 and merge commit created.

**GREEN Phase:**

**Implementation:** Extend `_detect_merge_state(slug)` to detect parent MERGE_HEAD states, then rewrite `merge()` entry point to route based on detected state.

**Behavior for `_detect_merge_state` extension:**
- After `merged` check: check parent MERGE_HEAD via `git rev-parse --verify MERGE_HEAD` (exit 0 = present)
- If MERGE_HEAD present: check `git diff --name-only --diff-filter=U` — return `"parent_resolved"` if empty, `"parent_conflicts"` if non-empty
- Otherwise return `"clean"` (submodule detection added in Cycle 1.4)

**Behavior for `merge()` routing:**
- If `"merged"`: call `_phase4_merge_commit_and_precommit(slug)` only
- If `"parent_resolved"`: call `_phase4_merge_commit_and_precommit(slug)` only
- If `"parent_conflicts"`: report unresolved conflicts and `raise SystemExit(3)` (stub — Phase 3 adds full behavior, Phase 4 adds formatted report)
- If `"submodule_conflicts"`: call `_phase3_merge_parent(slug)` then `_phase4_merge_commit_and_precommit(slug)` (D-5)
- If `"clean"`: run full pipeline `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit`

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Extend `_detect_merge_state` body to check parent MERGE_HEAD (after the `_is_branch_merged` check); add `parent_resolved` and `parent_conflicts` return paths
  Location hint: `_detect_merge_state` function added in Cycle 1.1
- File: `src/claudeutils/worktree/merge.py`
  Action: Replace `merge()` body with state detection + routing dispatch
  Location hint: `merge()` function at end of file, lines 257–262

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_resumes_from_parent_resolved -v`
**Verify no regression:** `pytest tests/ -k "merge" --ignore=tests/test_worktree_merge_conflicts.py -v`

---

## Cycle 1.3: `merge()` routes `parent_conflicts` state to exit 3

**RED Phase:**

**Test:** `test_merge_reports_and_exits_3_when_parent_conflicts`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- Exit code is 3 when `merge(slug)` called with MERGE_HEAD present and unresolved conflicts
- MERGE_HEAD still exists after the call (no `--abort` was run)
- Output contains name of conflicted file
- No traceback in output

**Expected failure:** `SystemExit(1)` — current Phase 1 clean-tree check rejects the dirty tree before reaching any conflict detection

**Why it fails:** Current code validates clean tree before checking merge state; staged conflict-marker files fail the clean check.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_reports_and_exits_3_when_parent_conflicts -v`

**Test setup:**
1. Create repo, branch with different content in `src/feature.py`, main with different content in same file
2. Start merge: `subprocess.run(["git", "merge", "--no-commit", "--no-ff", slug], ...)`
3. Verify MERGE_HEAD exists and `git diff --name-only --diff-filter=U` is non-empty
4. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit_code == 3, MERGE_HEAD still present (subprocess check), conflicted filename in output.

**GREEN Phase:**

**Implementation:** The routing from Cycle 1.2 already dispatches `parent_conflicts` to stub. Implement stub to list conflicts from `git diff --name-only --diff-filter=U` and exit 3.

**Behavior:**
- For `parent_conflicts` route: get conflict list via `git diff --name-only --diff-filter=U`
- Print each conflicted file
- `raise SystemExit(3)` — no `--abort`, no `clean -fd` (D-3, D-7)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Replace stub in `parent_conflicts` branch of `merge()` with conflict listing + exit 3
  Location hint: `parent_conflicts` case in `merge()` dispatch

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_reports_and_exits_3_when_parent_conflicts -v`
**Verify MERGE_HEAD preserved:** subprocess check in test; verify MERGE_HEAD still valid after CliRunner call.
**Verify no regression:** `pytest tests/ -k "merge" -x -v`

**CHECKPOINT after Cycle 1.3:** Verify all in-progress states route correctly:
- `merged` + `parent_resolved` → Phase 4
- `parent_conflicts` → exit 3, MERGE_HEAD preserved
- Run: `pytest tests/test_worktree_merge_merge_head.py -v`

---

## Cycle 1.4: `merge()` routes `submodule_conflicts` state to Phase 3

**RED Phase:**

**Test:** `test_merge_continues_to_phase3_when_submodule_conflicts`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- When agent-core has MERGE_HEAD (submodule mid-merge), calling `merge(slug)` does not exit with "Clean tree required"
- Agent-core MERGE_HEAD is present (test verifies the starting condition)
- `_detect_merge_state` returns `"submodule_conflicts"` when called directly with agent-core in mid-merge state (test this explicitly before the CliRunner call)
- After CliRunner call: exit code is 0 or 3 (not 1), confirming state routing bypassed the clean-tree check

**Expected failure:** `SystemExit(1)` with "Clean tree required" — current Phase 1 detects agent-core is dirty (staged files from mid-merge); additionally `_detect_merge_state` does not yet return `"submodule_conflicts"` (not implemented until this cycle's GREEN)

**Why it fails:** `_detect_merge_state` (as of Cycle 1.2) does not check agent-core MERGE_HEAD, so state is misclassified as `"clean"` and the full pipeline runs, hitting the clean-tree check.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_continues_to_phase3_when_submodule_conflicts -v`

**Test setup:**
1. Use `repo_with_submodule` fixture (chdir already handled by fixture)
2. Create branch on parent repo (no changes — just branch pointer)
3. Manually put agent-core in mid-merge state: create a conflicting commit on agent-core, then `git -C agent-core merge --no-commit --no-ff <commit>` leaving it mid-merge with no conflicts (so parent Phase 3 can proceed)
4. Invoke `worktree merge slug` via CliRunner.
5. Assert exit code is NOT 1 from clean-tree check (accept 0 or 3 as valid outcomes)

**GREEN Phase:**

**Implementation:** Add submodule MERGE_HEAD check to `_detect_merge_state`, inserting it between the `merged` check and the parent MERGE_HEAD check (per D-5 detection order).

**Behavior:**
- After `_is_branch_merged` check (returns `"merged"` if True):
- Add: run `git -C agent-core rev-parse --verify MERGE_HEAD` (exit 0 = agent-core mid-merge) — return `"submodule_conflicts"` if found, before checking parent MERGE_HEAD
- Rest of function unchanged (parent MERGE_HEAD → `parent_resolved`/`parent_conflicts`, else `"clean"`)

This makes the full detection order match D-5: merged → submodule_conflicts → parent_resolved/parent_conflicts → clean.

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Insert `git -C agent-core rev-parse --verify MERGE_HEAD` check into `_detect_merge_state`, after `_is_branch_merged` and before the parent MERGE_HEAD check
  Location hint: `_detect_merge_state` body, between `merged` return and parent MERGE_HEAD check

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_continues_to_phase3_when_submodule_conflicts -v`
**Verify no regression:** `pytest tests/ -k "merge" -x -v`

---

## Cycle 1.5: `merge()` routes `clean` state through full pipeline

**RED Phase:**

**Test:** `test_merge_clean_state_runs_full_pipeline`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- `merge(slug)` on a clean repo with a diverged branch produces a merge commit: `HEAD` has exactly 2 parents after the call
- Exit code is 0
- Merge commit message matches `f"🔀 Merge {slug}"`
- `_is_branch_merged(slug)` returns True after call

**Expected failure:** `AssertionError` — as of Cycle 1.4, `_detect_merge_state` is implemented but `merge()` still calls `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit` directly (the old linear chain), without routing through `_detect_merge_state`. Write this test after Cycle 1.4 GREEN but before wiring `clean` routing into `merge()`. The test verifies the `clean` path specifically: if `merge()` is not yet calling `_detect_merge_state` for routing, break the test by temporarily having `_detect_merge_state` return `"merged"` for any input — a 1-line change confirmed to fail this test — then revert after writing.

**Why it fails:** The `clean` routing path must be confirmed to exercise all 4 phases in order. Before Cycle 1.5 GREEN, this is enforced by verifying the test fails when `_detect_merge_state` short-circuits to `"merged"` (which would skip Phase 3, producing no merge commit or a fast-forward, failing the 2-parent check).

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_clean_state_runs_full_pipeline -v` (after applying the 1-line `_detect_merge_state` sabotage)

**STOP condition for RED:** If the test passes without sabotage AND Cycle 1.2 routing was correctly wired, the `clean` assertion is too weak. Verify HEAD has exactly 2 parents, not just that exit code is 0.

**Test setup:**
1. Use `repo_with_submodule` and `mock_precommit` fixtures
2. Create branch with one unique file commit
3. Add a different commit on main (diverge) so merge produces a real merge commit
4. Invoke `worktree merge slug` via CliRunner (repo_with_submodule fixture already handles chdir).
5. Assert exit 0, `len(parents_of_HEAD) == 2`, commit message starts with `"🔀 Merge"`, `_is_branch_merged(slug)` returns True.

**GREEN Phase:**

**Implementation:** Confirm that the `clean` routing path in `merge()` from Cycle 1.2 calls all 4 phases in sequence. Revert the RED-phase sabotage if applied.

**Behavior:**
- `clean` route: `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit`
- No new changes needed if Cycle 1.2 routing was correctly wired; revert sabotage if used for RED verification

**Changes:** Revert the 1-line sabotage in `_detect_merge_state` (if applied for RED phase). No other changes required.
**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py -v`
**Verify no regression:** `pytest tests/ -k "merge" -v`

---

**Phase 1 STOP conditions:**
- RED fails to fail (test passes before GREEN) → STOP, assert is too weak or test setup is incorrect
- `_detect_merge_state` returns wrong state for any git scenario → STOP, debug detection logic
- Regression in existing merge tests → STOP, state machine routing broke existing path
