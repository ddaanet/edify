# Deliverable Review: Worktree-Fixes Test Suite

**Scope:** 8 test files, 1,644 lines total
**Reference:** `plans/worktree-fixes/design.md` (Testing Strategy), `plans/worktree-fixes/requirements.md`

## Findings

### F-1: Missing `move_task_to_worktree` idempotent test
- **File:** `tests/test_worktree_session.py`
- **Axis:** Functional completeness
- **Severity:** Minor
- **Description:** Design specifies `move_task_to_worktree` must be tested for idempotent behavior. The implementation handles idempotency (returns silently if task already in Worktree Tasks, line 141-145 of `session.py`), but no test explicitly exercises this path. The closest test is `test_move_task_to_worktree_single_line` which tests the primary path, not the re-invocation case.

### F-2: `remove_worktree_task` idempotent test missing
- **File:** `tests/test_worktree_session_remove.py`
- **Axis:** Functional completeness
- **Severity:** Minor
- **Description:** Design specifies idempotent behavior for `remove_worktree_task` (no-op if slug not found). The implementation handles this (line 241-242 of `session.py`), but no test exercises the "slug not found" path explicitly.

### F-3: No `git branch -d` success verification after MERGE_HEAD empty-diff commit
- **File:** `tests/test_worktree_merge_merge_head.py`
- **Axis:** Functional completeness (FR-5 acceptance criterion)
- **Severity:** Major
- **Description:** FR-5 acceptance criteria explicitly state "`git branch -d` succeeds in `rm` after merge (branch is reachable from HEAD)." The design's testing strategy lists this as a Phase 1 test: "`git branch -d` succeeds after empty-diff merge." The `test_phase4_merge_head_empty_diff` test verifies MERGE_HEAD removal and merge commit creation but does not attempt `git branch -d` to verify the branch is an ancestor of HEAD. This is the core behavioral outcome FR-5 is solving.

### F-4: Phase 0 tests not parametrized as specified
- **File:** `tests/test_validation_task_format.py`
- **Axis:** Conformance
- **Severity:** Minor
- **Description:** Design specifies "Parametrized valid/invalid task names for `validate_task_name_format()`." Tests use inline multiple assertions per test method rather than `@pytest.mark.parametrize`. Functionally equivalent but less granular failure reporting. Not a correctness issue.

### F-5: FR-2 acceptance criterion "Scans both sections" not explicitly tested
- **File:** `tests/test_validation_task_format.py`
- **Axis:** Coverage (FR-2)
- **Severity:** Minor
- **Description:** FR-2 acceptance criteria state "Scans Pending Tasks and Worktree Tasks sections." The integration test (`test_validate_task_name_format_integration`) only creates a `Pending Tasks` section. The implementation does scan all task lines regardless of section (via `extract_task_names` which iterates all lines), but the test does not exercise a Worktree Tasks section with an invalid name to confirm coverage of both sections.

### F-6: `test_remove_worktree_task_reads_branch_state` has weak assertion
- **File:** `tests/test_worktree_session_remove.py:9-73`
- **Axis:** Vacuity
- **Severity:** Minor
- **Description:** The test comments state it "just verifies it doesn't crash." The function is called but no assertions check the outcome (task block presence/absence in session.md). The more specific tests (`test_remove_worktree_task_completed`, `test_remove_worktree_task_still_pending`) do verify outcomes, so this test adds minimal value beyond smoke-testing the `git show` path. Not harmful but effectively vacuous.

### F-7: `test_move_task_to_worktree_multiline` has a weak final assertion
- **File:** `tests/test_worktree_session.py:285`
- **Axis:** Specificity
- **Severity:** Minor
- **Description:** Line 285: `assert "**Task A**" not in pending_section or "Task B" in pending_section` — this disjunction always passes if Task B is in the pending section, regardless of whether Task A was removed. The intent is to verify Task A is not in Pending Tasks. Should be `assert "**Task A**" not in pending_section`.

### F-8: Design file naming deviation
- **File:** `tests/test_worktree_merge_merge_head.py`
- **Axis:** Conformance
- **Severity:** Minor
- **Description:** Design specifies MERGE_HEAD tests should be in `test_worktree_merge_parent.py`. Implementation places them in a separate file `test_worktree_merge_merge_head.py`. The existing `test_worktree_merge_parent.py` tests different concerns (merge initiation, precommit). Acceptable deviation — clearer separation of concerns.

## Gap Analysis

| Requirement | Acceptance Criterion | Test Coverage | Status |
|-------------|---------------------|---------------|--------|
| FR-1 | `derive_slug()` lossless round-trip | `test_derive_slug` in `test_worktree_utils.py:14-25` | COVERED |
| FR-1 | Remove `max_length` parameter | `derive_slug` signature confirmed, no `max_length` in tests or source | COVERED |
| FR-1 | `focus_session()` matches constrained names | `test_focus_session_multiline`, `test_focus_session_task_extraction`, `test_focus_session_section_filtering` | COVERED |
| FR-1 | Validation function exists | `TestValidateTaskNameFormat` class in `test_validation_task_format.py` | COVERED |
| FR-2 | Scans Pending Tasks and Worktree Tasks | Integration test covers Pending Tasks only | PARTIAL (F-5) |
| FR-2 | Rejects forbidden characters | `test_validate_task_name_format_invalid_chars`: `_`, `@`, `/`, `:` | COVERED |
| FR-2 | Clear error identifying offending name/char | Assertions check error message content | COVERED |
| FR-2 | Runs as part of `just precommit` | Integration test calls `validate()` (precommit entry point) | COVERED |
| FR-4 | New tasks include all continuation lines | `test_merge_conflict_session_md_multiline_blocks` | COVERED |
| FR-4 | Inserted before next `##` section header | `test_merge_conflict_session_md_insertion_position` | COVERED |
| FR-4 | Existing task detection by name | `test_merge_conflict_session_md` uses `extract_task_blocks` name comparison | COVERED |
| FR-5 | Phase 4 always commits (even empty diff) | `test_phase4_merge_head_empty_diff` | COVERED |
| FR-5 | `git branch -d` succeeds after merge | No test verifies `git branch -d` after empty-diff merge | GAP (F-3) |
| FR-5 | No behavior change for real changes | `test_merge_precommit_validation` in `test_worktree_merge_parent.py` | COVERED |
| FR-6 | `new --task` edits main repo session.md | `test_new_task_mode_moves_task_to_worktree` | COVERED |
| FR-6 | `rm` removes entry when task completed | `test_remove_worktree_task_completed`, `test_rm_e2e_removes_completed_task_from_worktree_tasks` | COVERED |
| FR-6 | `rm` preserves entry when task still pending | `test_remove_worktree_task_still_pending` | COVERED |
| FR-6 | Idempotent re-run | No explicit idempotency tests for `move_task_to_worktree` or `remove_worktree_task` | GAP (F-1, F-2) |

### Design Testing Strategy Cross-Reference

| Design-Specified Test | Actual Test | Status |
|----------------------|-------------|--------|
| Parametrized valid/invalid names | `TestValidateTaskNameFormat` (inline, not parametrized) | COVERED (style deviation) |
| `derive_slug` lossless round-trip | `test_derive_slug` | COVERED |
| `derive_slug` rejects invalid (ValueError) | `test_derive_slug_validates_format` | COVERED |
| Precommit integration | `test_validate_task_name_format_integration` | COVERED |
| `extract_task_blocks` single-line | `test_extract_single_line_task` | COVERED |
| `extract_task_blocks` multi-line | `test_extract_multi_line_task` | COVERED |
| `extract_task_blocks` mixed sections | `test_extract_section_filter` | COVERED |
| `_resolve_session_md_conflict` multi-line blocks | `test_merge_conflict_session_md_multiline_blocks` | COVERED |
| `_phase4` MERGE_HEAD detection | `test_phase4_merge_head_empty_diff` | COVERED |
| `git branch -d` succeeds after empty-diff merge | None | GAP |
| `move_task_to_worktree` moves block | `test_move_task_to_worktree_single_line`, `_multiline` | COVERED |
| `move_task_to_worktree` creates section | `test_move_task_to_worktree_creates_section` | COVERED |
| `move_task_to_worktree` idempotent | None | GAP |
| `remove_worktree_task` removes completed | `test_remove_worktree_task_completed` | COVERED |
| `remove_worktree_task` keeps pending | `test_remove_worktree_task_still_pending` | COVERED |
| `new --task` E2E | `test_new_task_mode_moves_task_to_worktree` | COVERED |
| `rm` E2E | `test_rm_e2e_removes_completed_task_from_worktree_tasks` | COVERED |

## Summary

- **1 Major finding** (F-3): Missing `git branch -d` success test for FR-5's core acceptance criterion
- **6 Minor findings**: idempotency gaps (F-1, F-2), weak assertions (F-6, F-7), style deviations (F-4, F-5), naming deviation (F-8)
- **0 Critical findings**
- **Test coverage is strong overall**: 20/23 design-specified test scenarios are covered with meaningful assertions
- **All FR acceptance criteria have at least partial coverage** except the `git branch -d` success scenario from FR-5
