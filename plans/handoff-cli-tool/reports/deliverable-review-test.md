# Test Review: handoff-cli-tool (RC11)

**Date:** 2026-03-25
**Scope:** 20 test files (+3665/-60 lines), full-scope review
**Axes:** conformance, functional correctness, functional completeness, vacuity, excess, specificity, coverage, independence

## RC10 Fix Verification

| Finding | Status | Evidence |
|---------|--------|----------|
| m-2: `overwrite_status` regex backreference | VERIFIED | test_session_handoff.py:157-167 — `test_overwrite_status_backreference_in_text` asserts `\g<1>` and `\g<3>` survive in output |
| m-6: Redundant `len > 0` removed | VERIFIED | test_session_parser.py:138 — no `len(...) > 0` patterns remain |
| m-7, m-8: `match=` added to bare `pytest.raises` | VERIFIED | test_session_commit.py:217 uses `match="no uncommitted changes"`, test_worktree_merge_errors.py:83 uses `match="non-zero exit"` |
| m-10: Disjunctive assertion replaced | VERIFIED | test_session_status.py:263 — asserts `"In-tree:" in result.output` (specific, not disjunctive) |
| m-11: Integration test plan dir | VERIFIED | test_session_integration.py:37-39 — creates `plans/widget/` with `brief.md` |
| m-13: Dead `return None` removed | N/A (code, not test) | — |

All RC10 test-related fixes verified.

## Findings

### Minor

[m-1] test_session_status.py:280-298 — conformance — `SESSION_FIXTURE` module constant defined after its first usage at line 253 (`test_session_status_cli`). Forward reference works in Python but violates conventional top-of-module placement for test fixtures. Carried from RC8/RC9/RC10.

[m-2] test_session_commit_pipeline.py:121-134 — specificity — `test_strip_hints_single_space_then_double` and related hint-stripping tests use assertion strings like `"continuation"` and `"single"` that are also substrings of docstrings and variable names. The tests verify behavior correctly but the assertion strings are generic words that could match unrelated content if the test data changed. Low risk since test data is inline.

[m-3] test_planstate_aggregation.py:102-197 — independence — `test_git_metadata_helpers` creates a second repo (`repo2`) within the same test function to test `_commits_since_handoff` with no session.md. This conflates two scenarios (positive path and negative path) in one test. Not a correctness issue but reduces isolation for failure diagnosis.

[m-4] test_session_handoff.py:235-261 — conformance — `test_write_completed_with_accumulated_content` and `test_write_completed_overwrites_not_appends` both test the same behavior (replacing section content), differing only in initial state. The docstrings adequately distinguish them, but the tests exercise the same code path — `_write_completed_section` always replaces. Not vacuous (they verify different initial states produce the same correct result), but close to redundant.

[m-5] test_session_commit_pipeline.py:157-212 — conformance — `test_submodule_clean_error_shows_full_path` uses `create_submodule_origin` + `add_submodule` helpers while other submodule tests in `test_session_commit_pipeline_ext.py` use `_init_repo_with_submodule`. Two different helper patterns for the same setup. Not a correctness issue but inconsistent.

## Coverage Assessment

| Design Scenario | Test File(s) | Status |
|----------------|-------------|--------|
| **H-2: Completed write modes** (overwrite, append, auto-strip) | test_session_handoff.py:205-288 | COVERED — Design note: implementation unified all three modes into simple section replacement (`_write_completed_section`). Tests verify: fresh write (overwrite), empty prior section, accumulated content replacement, idempotent overwrite, committed-state overwrite. All three prior-state variants exercised. |
| **C-1: Vet check** (unreviewed, stale, no patterns) | test_session_commit.py:263-362, test_session_commit_validation.py:217-257 | COVERED — `test_vet_check_no_config` (no patterns = pass), `test_vet_check_unreviewed` (no report = fail with reason), `test_vet_check_stale` (old report = fail), `test_vet_check_pass` (fresh report = pass). Stale info detail verified with file names and timestamps. |
| **C-2: Submodule 4-state matrix** (files x message) | test_session_commit_pipeline_ext.py:41-163 | COVERED — All four cells: (yes/yes) `test_commit_with_submodule`, (yes/no) `test_commit_submodule_no_message`, (no/yes) `test_commit_submodule_orphan_message`, (no/no) `test_commit_no_submodule_changes`. Multi-submodule ordering also covered at line 332. |
| **C-3: Clean files error + STOP** | test_session_commit.py:203-222, test_session_commit_cli.py:95-121 | COVERED — `test_validate_files_clean_error` asserts `CleanFileError` with `match="no uncommitted changes"`, checks `clean_files` list and `STOP` in string. CLI test `test_commit_cli_clean_file_exits_2` verifies exit code 2. |
| **C-4: Validation levels** (precommit, lint-only, no-vet, combined) | test_session_commit_validation.py:21-291 | COVERED — `test_commit_just_lint` (lint only, precommit not called), `test_commit_default_calls_vet` (default calls vet), `test_commit_skips_vet_when_no_vet` (no-vet skips), `test_commit_combined_options` (just-lint + amend), `test_commit_just_lint_no_vet` (just-lint + no-vet). All four validation levels plus combinations. |
| **C-5: Amend semantics** (amend + no-edit, amend without message, submodule amend) | test_commit_pipeline_errors.py:251-284, test_session_commit_pipeline_ext.py:165-327 | COVERED — `test_commit_amend_no_edit` (preserves message), `test_commit_amend_parent` (replaces commit), `test_commit_amend_submodule` (both amended), `test_commit_amend_validation` (HEAD files accepted). Amend without message: implicitly covered by `test_parse_commit_edge_cases` (amend + no-edit without Message = valid). |
| **ST-0: Worktree-destined tasks** (marker handling) | test_session_parser.py:75-84, test_status_rework.py:151-180 | COVERED — Parser extracts `worktree_marker` = `"my-slug"` and `"wt"`. `test_render_pending_skips_worktree_marked` verifies tasks with marker skip `Next:` selection, second task gets `▶`. |
| **ST-1: Parallel group detection** | test_session_status.py:165-225, test_status_rework.py:218-267 | COVERED — Tests: different plan_dirs form group, single task = None, shared plan = None, mixed plans with consecutive window, cap at 5, blocker excludes. CLI integration verifies blockers prevent parallel detection. |
| **ST-2: Missing session.md and old format** | test_session_status.py:266-277, test_status_rework.py:118-212 | COVERED — `test_session_status_missing_session` asserts exit 2 + "Error". `test_status_rejects_old_format` asserts exit 2 for tasks without metadata. `test_status_rejects_pending_tasks_section` asserts exit 2 for old section name. |
| **Error output format** (Header + STOP) | test_session_commit.py:203-222, test_session_commit_cli.py:49-60, test_commit_pipeline_errors.py:110-131 | COVERED — `**Error:**` format verified in clean-file errors, pipeline errors, CLI wiring. `STOP` directive verified in CleanFileError. `_error()` structured output tested with empty and populated stderr. |
| **S-2: git extraction + submodule discovery** | test_git_helpers.py:22-118 | COVERED — `_git_ok`, `discover_submodules` (none and present), `_is_submodule_dirty` (clean, dirty, nonexistent). |
| **S-3: Output conventions** (exit codes) | test_session_commit_cli.py, test_session_handoff_cli.py, test_session_status.py | COVERED — Exit 0 (success), exit 1 (pipeline failure), exit 2 (input validation) verified across all three subcommands. |
| **S-4: Session parser** | test_session_parser.py | COVERED — Status line, completed section, in-tree tasks with metadata, worktree tasks with markers, blockers extraction, date extraction, old format handling, missing file error. |
| **S-5: Git changes utility** | test_git_cli.py | COVERED — Clean repo, dirty repo, submodule with prefixed paths, clean submodule omitted. |
| **H-3: Diagnostic output** | test_session_handoff_cli.py:69-93 | COVERED — Fresh handoff verifies `**Git status:**` in output. |
| **H-4: State caching** | test_session_handoff.py:293-337, test_session_handoff_cli.py:96-137 | COVERED — save/load/clear lifecycle, resume from state file, no-stdin-no-state error, backward compatibility with unknown fields. |
| **Integration (Phase 7)** | test_session_integration.py | COVERED — Handoff-then-status round-trip verifying session.md updates propagate. |

## Notes

- Tests use real git repos via `tmp_path` fixtures throughout, consistent with the `testing.md` decision to prefer E2E over mocked subprocess (line 166).
- `_run_precommit` is consistently mocked across pipeline tests (cannot rely on `justfile` in test environment) while git operations use real repos.
- The `pytest_helpers.py` module provides shared helpers (`init_repo_at`, `init_repo_minimal`, `create_submodule_origin`, `add_submodule`) that avoid duplication across test files.
- Test files are well-organized by module: parser tests in `test_session_parser.py`, pipeline tests split across `test_session_commit_pipeline.py` (parent) and `test_session_commit_pipeline_ext.py` (submodule/amend), validation in `test_session_commit_validation.py`.
- All design scenarios from the outline (S-1 through S-5, H-1 through H-4, C-1 through C-5, ST-0 through ST-2) have test coverage.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 5 |

RC10 test fixes all verified. Five new minors: one carried-forward fixture ordering issue (m-1), one generic assertion string concern (m-2), one test isolation note (m-3), one near-redundancy observation (m-4), one inconsistent helper pattern (m-5). All are low-risk style/structure observations.

| Axis | Status |
|------|--------|
| Conformance | 2 minors (m-1 fixture ordering, m-5 helper inconsistency) |
| Functional correctness | Pass |
| Functional completeness | Pass — all design scenarios covered |
| Vacuity | Pass — no ceremonial tests |
| Excess | Pass — no unspecified test artifacts |
| Specificity | 1 minor (m-2 generic assertion strings) |
| Coverage | Pass — full design scenario coverage table above |
| Independence | 1 minor (m-3 conflated scenarios), 1 minor (m-4 near-redundancy) |
