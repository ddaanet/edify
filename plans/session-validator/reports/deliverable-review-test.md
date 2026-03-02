# Deliverable Review: Test Files

**Reviewer model:** claude-opus-4-6
**Design baseline:** plans/session-validator/requirements.md
**Date:** 2026-03-02

---

## FR-2 Coverage Analysis (Special Concern)

FR-2 acceptance criteria vs test coverage:

| Criterion | Tested? | Location |
|-----------|---------|----------|
| Task lines match `- [ ] **Name** -- description` or `- [x] **Name** -- description` | Yes | task_parsing tests (lines 9-52), section_aware (lines 9-17) |
| Worktree markers match arrow+slug format | Yes | task_parsing (lines 93-119), session_worktrees (lines 43-46) |
| Model tier validation (haiku/sonnet/opus) | Yes | task_parsing (lines 68-91), section_aware (lines 97-107, 170-179) |
| Task names unique across file | Yes | test_validation_tasks.py (lines 276-298), session_structure cross-section (lines 91-118) |
| Sub-items allowed but not validated | Yes | section_aware (lines 52-61) |
| Valid checkboxes | Yes | task_parsing (lines 9-46, 158-179), section_aware (lines 85-95, 156-168) |

FR-2 is fully covered across the shared parsing module and section-aware validator tests.

---

## File-by-File Review

### tests/test_validation_task_parsing.py

**Minor** line 30 -- Completeness -- `test_main_worktree_excluded` in `TestGetWorktreeslugs` (wrong file; see session_worktrees below). This file is clean.

No findings. 25 tests covering all `ParsedTask` fields, permissive parsing, valid/invalid checkboxes, old marker migration detection, restart/priority extraction. Coverage is thorough.

### tests/test_validation_session_structure.py

**Minor** lines 159-176 -- Conformance -- FR-1 requires "H1 header required as first line" but `check_section_schema` tests (lines 156-261) do not test for missing or invalid H1. This is acceptable because H1 validation lives in `check_status_line()` (tested separately in `test_validation_status_line.py`), not in `check_section_schema()`. The two validators compose in `validate()`. No gap.

**Minor** line 255 -- Specificity -- `test_duplicate_sections` asserts `len(errors) >= 1` rather than `== 1`. A more precise assertion would confirm exactly one error for a single duplicate. Low risk since the implementation produces exactly one.

**Minor** lines 337-352 -- Functional correctness -- `test_multiple_error_types` asserts `len(errors) == 3` for cross-section duplicate + missing ref + missing worktree. The count depends on `worktree_slugs=set()` causing a worktree marker error for `slug`. If the implementation changes how worktree_slugs=set() vs None behaves, this test becomes fragile. Currently correct.

### tests/test_validation_status_line.py

No findings. 11 tests covering: valid H1+status, missing H1, wrong H1 format, missing date, invalid date format, missing blank line, missing status line, non-bold status, empty status text, whitespace-only status, file too short. All FR-5 acceptance criteria covered.

### tests/test_validation_session_commands.py

No findings. 8 tests covering: no command, valid command, inline+execute anti-pattern, subpath variant, multiple tasks with one anti-pattern, inline without execute (negative case), non-task lines skipped, empty lines skipped. FR-7 acceptance criteria fully covered including extensibility (pattern list structure verified by test structure).

### tests/test_validation_session_worktrees.py

**Minor** lines 27-31 -- Vacuity/Specificity -- `test_main_worktree_excluded` has a weak assertion: `assert "main" in result or result == {"slug-1"}`. This always passes regardless of whether main is filtered. The test documents desired behavior (main exclusion per FR-4) but doesn't enforce it. Looking at the implementation, `get_worktree_slugs` returns the `worktree_slugs` parameter directly when provided (line 24 of session_worktrees.py), so this test exercises the passthrough path, not the main-exclusion logic. Main exclusion happens in the git-parsing path (`.claude/worktrees/` filter on line 48), which is untestable without real git infrastructure.

**Minor** lines 127-135 -- Specificity -- `test_line_numbers_in_errors` asserts `"line" in errors[0].lower() or "2" in errors[0]`. The `or` weakens this: any error containing "2" passes regardless of whether line numbers are actually included. Should be `and`.

### tests/test_validation_plan_archive.py

**Critical** lines 1-213 -- Convention -- FR-6 tests use `subprocess.run(["git", ...])` via the `_git` helper and create real git repos with `git init` in `tmp_path`. This *does* follow the project convention ("use real git repos, not subprocess mocks"). The `git_repo` fixture creates an actual repo. No violation here.

No findings on substance. 12 tests covering: no deletions, single deleted plan, multiple deletions, gitkeep-only plan exclusion, H2 heading extraction, case-insensitive matching, missing archive file, H1/H3 filtering, no-deleted-plans integration, covered plan, uncovered plan, mixed coverage. FR-6 acceptance criteria fully covered.

### tests/test_validation_section_aware.py

**Minor** lines 85-95 -- Functional correctness -- `test_invalid_checkbox_in_task_section_error` uses `[?]` and `[X]` as invalid checkboxes. `[X]` (uppercase) is a good edge case. However, the test asserts `len(errors) >= 2` rather than `== 2`. Same minor imprecision as the session_structure duplicate test.

**Minor** lines 97-107 -- Coverage -- `test_invalid_model_in_task_section_error` tests `gpt4` and `claude` as invalid models but doesn't test a near-miss like `Sonnet` (capitalized) or `OPUS`. The implementation lowercases before comparison (line 322 of session_structure.py: `seg_lower = seg.lower().strip()`), so capitalized valid models would pass. This is correct behavior, but a test confirming case-insensitivity would strengthen confidence. Not a gap, but a missed opportunity.

No other findings. 17 tests covering all task sections (In-tree, Worktree, Pending legacy), blank lines, indented sub-items, HTML comments, unparseable lines, invalid checkboxes, invalid models, non-task sections excluded, mixed valid/invalid, all valid checkboxes enumerated, all valid models enumerated, no-model tasks, empty input, no-task-sections.

### tests/test_validation_tasks.py

**Major** lines 57-68 -- Convention -- Uses `subprocess.run` mock via `@patch` for `get_session_from_commit`, `get_merge_parents`, `get_staged_session`, and `check_history`. This contradicts the project convention of real git repos over subprocess mocks. However, this is a pre-existing test file (`+3/-3` delta, consumer migration only), not new code for this branch. The migration correctly updated `[+]`/`[-]` markers. The mocking pattern is a pre-existing concern, not introduced by this deliverable.

**Minor** lines 120-131 -- Convention -- `TestGetSessionFromCommit` mocks `subprocess.run` rather than using a real git repo. Same as above: pre-existing.

No findings on the migration changes themselves. The `+3/-3` correctly updates task status markers from old format to new.

### tests/test_worktree_merge_session_resolution.py

No findings. The `+2/-2` delta correctly updates `[x]`/`[-]` markers in test fixtures. Tests use pure functions (`_merge_session_contents`) with string inputs -- no mocking concerns.

### tests/test_worktree_session.py

No findings. The `+3/-3` delta correctly updates task status markers. Tests use `tmp_path` fixtures for file operations. No mock concerns.

---

## Test Independence Check

All test classes use instance methods (no class-level shared state). Fixtures are `tmp_path` (pytest-provided, isolated per test) or `git_repo` (creates fresh repo per test via `tmp_path`). No global state mutation detected. No ordering dependencies.

One pattern worth noting: `test_validation_plan_archive.py` uses `subprocess.run(["git", ...])` in a helper function called from fixtures and tests. This is real git infrastructure, not mocking, so isolation is maintained through `tmp_path` uniqueness.

---

## Summary

| Severity | Count | Files |
|----------|-------|-------|
| Critical | 0 | -- |
| Major | 1 | test_validation_tasks.py (pre-existing mock pattern, not introduced by this branch) |
| Minor | 6 | session_structure (2), session_worktrees (2), section_aware (2) |

**Overall assessment:** Test suite is well-structured with strong coverage of all FR acceptance criteria. FR-2 is fully covered across task_parsing and section_aware tests. The one Major finding is pre-existing (not introduced by this deliverable). Minor findings are assertion imprecision (`>=` vs `==`, weak `or` conditions) and one vacuous test for main worktree exclusion. No test independence issues. No vacuous tests (all test meaningful behavior). No missing acceptance criteria coverage.

**Actionable items:**
- M-1 (pre-existing): Consider converting tasks.py tests from mocks to real git repos in a future cleanup pass
- m-1: Tighten `test_main_worktree_excluded` to actually test exclusion behavior, or document it as a passthrough-only test
- m-2: Change `assert "line" in errors[0].lower() or "2" in errors[0]` to use `and`
- m-3/m-4: Change `>=` assertions to `==` where exact count is known
- m-5: Add capitalized model name test case for case-insensitivity confidence
