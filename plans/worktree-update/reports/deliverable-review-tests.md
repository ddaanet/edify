# Deliverable Review: Test Coverage for worktree-update

**Reviewer:** Opus 4.6
**Date:** 2026-02-13
**Methodology:** ISO 25010 / IEEE 1012 review axes for test artifacts
**Scope:** 12 test files (2854 lines), 1 fixture file, 1 design spec

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 6 |
| Minor | 5 |
| Total | 13 |

| Axis | Count |
|------|-------|
| Functional completeness (gap) | 5 |
| Vacuity | 2 |
| Independence | 2 |
| Excess (duplication) | 2 |
| Specificity | 1 |
| Conformance | 1 |

---

## Findings

### F-01: No precommit failure test (exit code 1)

- **File:** `tests/test_worktree_merge_parent.py` (entire file)
- **Axis:** Functional completeness (gap)
- **Severity:** Critical

Design spec Phase 4 requires: "If precommit fails (exit != 0): exit 1 with message 'Precommit failed after merge' + stderr." The `test_merge_precommit_validation` test (line 89) documents this behavior in its docstring (lines 101-103) but only tests the success path. The `mock_precommit` fixture always returns `returncode=0`. No test mocks a failing precommit to verify exit code 1 and the error message. This is a specified critical scenario with zero test coverage.

### F-02: No merge idempotency test (re-run after fix)

- **File:** `tests/test_worktree_merge_*.py` (all merge test files)
- **Axis:** Functional completeness (gap)
- **Severity:** Critical

Design spec requires: "Idempotency: re-running after manual fix resumes correctly." No test creates a merge that fails (e.g., source conflict or precommit failure), fixes the issue, then re-runs merge to verify it completes successfully. This is the recovery workflow and the only way to verify the merge command is safe to retry.

### F-03: No exit code 2 for submodule failure

- **File:** `tests/test_worktree_merge_validation.py`
- **Axis:** Functional completeness (gap)
- **Severity:** Major

Design spec exit codes: "2: Fatal error (branch not found, submodule failure)." The test at line 27 covers exit code 2 for branch-not-found, but no test covers exit code 2 for a submodule failure scenario (e.g., submodule merge conflict, fetch failure that cannot be recovered).

### F-04: test_merge_submodule_ancestry mocks away the behavior it claims to test

- **File:** `tests/test_worktree_merge_submodule.py:15-96`
- **Axis:** Vacuity
- **Severity:** Major

The test sets up diverged submodule state (lines 30-86) with real git operations, then patches `claudeutils.worktree.merge._git` with a `MagicMock` that returns empty string for all calls (lines 88-91). The actual merge behavior is completely replaced by the mock. The assertions check that `ls-tree` appeared in mock call args (line 94-95), which verifies the function was *called* but not that ancestry checking *works correctly*. The real git operations in setup are wasted. This is structural validation (was the function called?) not behavioral validation (does ancestry checking produce correct outcomes?).

### F-05: test_merge_submodule_fetch uses implementation-coupled mocking

- **File:** `tests/test_worktree_merge_submodule.py:163-232`
- **Axis:** Independence
- **Severity:** Major

The test monkey-patches `subprocess.run` globally and tracks specific command patterns (`cat-file`, `fetch`, `merge-base`). This couples the test to the exact subprocess commands and argument ordering used in the implementation. If the implementation changes to use `git -C agent-core log --ancestry-path` instead of `merge-base`, the test breaks despite behavior being equivalent. The test validates implementation details (specific git commands issued), not behavioral outcomes (submodule commit is reachable after merge).

### F-06: commit_file helper duplicated across 3 test files

- **File:** `tests/test_worktree_merge_parent.py:162`, `tests/test_worktree_merge_conflicts.py:394`, `tests/test_worktree_merge_jobs_conflict.py:141`
- **Axis:** Excess (duplication)
- **Severity:** Major

Identical `commit_file()` function defined as a module-level function in three test files. The `fixtures_worktree.py` already provides `commit_file` as a pytest fixture. The three module-level duplicates shadow the fixture version. This creates maintenance risk: if the fixture signature changes, the module-level copies continue working with divergent behavior.

### F-07: _setup_repo_with_submodule duplicated across test files

- **File:** `tests/test_worktree_new_creation.py:13-97`, `tests/test_worktree_submodule.py:13-96`
- **Axis:** Excess (duplication)
- **Severity:** Minor

Nearly identical `_setup_repo_with_submodule` helper (~85 lines) duplicated between two files. The `repo_with_submodule` fixture in `fixtures_worktree.py` serves a similar purpose but uses `git submodule add` instead of manual `update-index --cacheinfo`. The duplication exists because the approach differs, but this means three different submodule setup strategies exist in the test suite.

### F-08: No test for source file conflict cleanup (git clean -fd)

- **File:** `tests/test_worktree_merge_validation.py:46-117`
- **Axis:** Functional completeness (gap)
- **Severity:** Major

Design spec Phase 3 requires: "Abort: `git merge --abort`, clean debris: `git clean -fd`." The `test_merge_conflict_source_files` test verifies `MERGE_HEAD` does not exist after abort (line 117), but does not verify that `git clean -fd` was run and that any debris files from the merge branch were removed. The test creates a conflict and checks abort happened, but the "clean debris" behavior is untested.

### F-09: test_merge_theirs_clean_tree has conditional submodule test

- **File:** `tests/test_worktree_clean_tree.py:242-264`
- **Axis:** Specificity
- **Severity:** Minor

Test 3 (worktree submodule dirty, line 243) wraps the assertion in `if (worktree_path / "agent-core").exists()` and further `if (worktree_path / "agent-core" / ".git").exists()`. If submodule initialization fails silently, the test passes vacuously without testing anything. A `pytest.skip()` or explicit failure would be more appropriate than silent pass-through.

### F-10: No test for --task with non-default session-md path

- **File:** `tests/test_worktree_new_config.py:89-128`
- **Axis:** Functional completeness (gap)
- **Severity:** Minor

Design spec: "--session-md <path> (default agents/session.md) -- source for focus-session extraction." The `test_new_task_option` test verifies `--task` with default session path and checks that `--session` is ignored when `--task` is present. But no test provides a custom `--session-md` path pointing to a non-default location to verify the argument is correctly threaded through.

### F-11: test_rm_submodule_first_ordering tests internal function, not CLI behavior

- **File:** `tests/test_worktree_commands.py:246-281`
- **Axis:** Independence
- **Severity:** Minor

The test directly calls `_remove_worktrees()` (a private function imported from `cli.py`) with mock `subprocess.run` and checks command ordering. This tests implementation details rather than behavior. A behavioral test would invoke `worktree rm` via CliRunner on a repo with a submodule worktree, then verify the submodule worktree is no longer registered and the parent worktree is also gone. The companion test `test_rm_worktree_registration_probing` (line 197) does this correctly as an E2E test.

### F-12: Merge parent test does not verify branch deletion after merge

- **File:** `tests/test_worktree_merge_parent.py`
- **Axis:** Conformance
- **Severity:** Minor

The design spec merge operation (Mode C in skill) involves merge followed by `rm`. The merge tests verify the merge completes and tree is clean, but no merge test verifies whether the worktree branch still exists or was cleaned up. This is arguably outside merge scope (rm handles it), but there is no integration test that exercises the full merge+rm workflow.

### F-13: test_merge_precommit_validation docstring claims describe untested behavior

- **File:** `tests/test_worktree_merge_parent.py:89-159`
- **Axis:** Vacuity
- **Severity:** Major

The docstring (lines 95-103) specifies six behavioral conditions including "If precommit fails (exit != 0): exit 1 with failure message." The test body only exercises the happy path (precommit passes → exit 0 → merge commit created → tree clean). The docstring serves as a behavioral specification that the test does not fulfill. The specification-implementation gap makes the docstring misleading about test coverage.

---

## Gap Analysis: Design Requirements vs Test Coverage

### test_worktree_new.py (split across new_creation, new_config, submodule)

| Design Requirement | Test Coverage | File:Line |
|---|---|---|
| Sibling path creation (not wt/slug) | Covered | test_worktree_new_creation.py:144,178 |
| Container directory created if not in -wt parent | Covered | test_worktree_utils.py:64 |
| Worktree-based submodule (git -C agent-core worktree list) | Covered | test_worktree_submodule.py:184-190 |
| Sandbox registration (settings.local.json) | Covered | test_worktree_new_config.py:14 |
| Existing branch reuse | Covered | test_worktree_new_creation.py:100 |
| Env init (just setup invoked, warning if missing) | Covered | test_worktree_new_config.py:49,163 |
| --task mode: slug derivation | Covered | test_worktree_commands.py:116 |
| --task mode: focused session generation | Covered | test_worktree_commands.py:149-151 |
| --task mode: tab-separated output | Covered | test_worktree_commands.py:140-144 |

### test_worktree_rm.py (split across rm and commands)

| Design Requirement | Test Coverage | File:Line |
|---|---|---|
| Submodule-first removal ordering | Covered (unit) | test_worktree_commands.py:246 |
| Container cleanup (empty container removed) | Covered | test_worktree_commands.py:283 |
| Branch deletion: -d not -D, warning for unmerged | Covered | test_worktree_commands.py:363 |
| Graceful degradation: branch-only removal | Covered | test_worktree_rm.py:77 |

### test_worktree_merge.py (split across 5 merge files)

| Design Requirement | Test Coverage | File:Line |
|---|---|---|
| Phase 1: OURS clean tree with session exemption | Covered | test_worktree_clean_tree.py:110 |
| Phase 1: THEIRS strict clean tree (no session exemption) | Covered | test_worktree_clean_tree.py:172 |
| Phase 2: Submodule ancestry check | Partial (see F-04) | test_worktree_merge_submodule.py:15 |
| Phase 2: Submodule merge when needed | Covered | test_worktree_merge_submodule.py:305 |
| Phase 2: Skip when ancestor | Mocked only (see F-04) | test_worktree_merge_submodule.py:88-95 |
| Phase 2: Fetch when unreachable | Mocked (see F-05) | test_worktree_merge_submodule.py:163 |
| Phase 3: session.md auto-resolve | Covered | test_worktree_merge_conflicts.py:132 |
| Phase 3: learnings.md append theirs-only | Covered | test_worktree_merge_conflicts.py:261 |
| Phase 3: jobs.md keep-ours with warning | Covered | test_worktree_merge_jobs_conflict.py:13 |
| Phase 3: agent-core conflict auto-resolve | Covered | test_worktree_merge_conflicts.py:13 |
| Phase 3: Source file conflict abort | Covered | test_worktree_merge_validation.py:46 |
| Phase 3: Source file conflict cleanup (git clean) | **MISSING** (F-08) | -- |
| Phase 4: Precommit success | Covered | test_worktree_merge_parent.py:89 |
| Phase 4: Precommit failure (exit 1) | **MISSING** (F-01) | -- |
| Exit code 0 (success) | Covered | multiple merge tests |
| Exit code 1 (conflicts/precommit) | Partial (conflict yes, precommit no) | test_worktree_merge_validation.py:112 |
| Exit code 2 (fatal: branch not found) | Covered | test_worktree_merge_validation.py:27 |
| Exit code 2 (fatal: submodule failure) | **MISSING** (F-03) | -- |
| Idempotency (re-run after fix) | **MISSING** (F-02) | -- |

### test_focus_session.py

| Design Requirement | Test Coverage | File:Line |
|---|---|---|
| Task extraction | Covered | test_worktree_utils.py:163 |
| Blockers filtering | Covered | test_worktree_utils.py:181 |
| Reference files filtering | Covered | test_worktree_utils.py:181 (same test) |
| Missing task error | Covered | test_worktree_utils.py:212 |

Note: Focus session tests are in `test_worktree_utils.py`, not a separate `test_focus_session.py` as the design suggested. This is acceptable -- the split is different but coverage exists.

---

## Excess Tests (not in design, may be valid extensions)

| Test | File:Line | Assessment |
|---|---|---|
| test_package_import | test_worktree_commands.py:14 | Smoke test, low value but harmless |
| test_worktree_command_group | test_worktree_commands.py:19 | Help output structure, valid UX test |
| test_ls_empty | test_worktree_commands.py:27 | Not in design "Test updates" but ls is in-scope command |
| test_ls_multiple_worktrees | test_worktree_commands.py:41 | Same as above |
| test_new_directory_collision | test_worktree_new_creation.py:117 | Edge case not in design, valid defensive test |
| test_new_container_idempotent | test_worktree_new_config.py:199 | Container idempotency, valid edge case |
| test_new_session_handling_branch_reuse | test_worktree_new_config.py:131 | Session + branch reuse interaction, valid |
| test_wt_path_edge_cases | test_worktree_utils.py:81 | Deep nesting, special chars, empty slug validation |
| test_add_commit_nothing_staged | test_worktree_clean_tree.py:87 | add-commit idempotency, valid for merge flow |
| test_rm_post_removal_cleanup_idempotent | test_worktree_commands.py:339 | Idempotent rm, valid defensive test |
| test_rm_post_removal_cleanup_non_empty_container | test_worktree_commands.py:308 | Container preserved when siblings exist, valid |

All excess tests are reasonable extensions that cover edge cases or interaction scenarios. None test implementation details unnecessarily.

---

## Structural Observations

**Test distribution:** The 12 test files total ~2854 lines across a well-organized split. The merge tests are appropriately divided by concern (validation, submodule, parent, conflicts, jobs conflict). The new command tests are split by concern (creation/collision vs. configuration/setup vs. submodule).

**Fixture organization:** The `fixtures_worktree.py` provides `repo_with_submodule`, `init_repo`, `commit_file`, and `mock_precommit`. Good separation of concerns. However, the `commit_file` fixture is shadowed by module-level functions in 3 files (F-06).

**E2E approach:** Tests consistently use real git repos via `tmp_path`, matching the design's "E2E over mocked subprocess" principle. Exceptions are F-04 and F-05 which mock subprocess for verification, and F-11 which tests internal functions directly.
