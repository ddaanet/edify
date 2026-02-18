# Cycle 1.2

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 1

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
