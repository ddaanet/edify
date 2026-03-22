# Deliverable Review: Tests (Layer 1)

**Plan:** handoff-cli-tool
**Reviewer model:** opus
**Date:** 2026-03-21

## Summary

15 test files reviewed against the design outline. The test suite is structurally sound with good specificity and real-git-repo integration tests. Several coverage gaps exist against design-specified scenarios, two of which are critical (missing exit code verification, untested design requirement). The remaining findings are major-level coverage gaps and minor style issues.

## Critical Findings

### C-1: Commit CLI does not verify exit codes match S-3 convention

**File:** `tests/test_session_commit_cli.py`
**Axis:** conformance, functional correctness
**Severity:** critical

Design S-3 specifies exit code semantics: 0=success, 1=pipeline error, 2=input validation. The CLI test `test_commit_cli_success` checks exit 0, `test_commit_cli_validation_error` checks exit 2, and `test_commit_cli_vet_failure` checks exit 1. However, the implementation at `src/claudeutils/session/cli.py:28` calls `commit_pipeline(ci)` without passing `cwd`, meaning it operates on whatever the current directory is. More critically, the pipeline errors (CleanFileError from C-3, missing submodule message from C-2) are not tested through the CLI layer. A `CleanFileError` raised inside `commit_pipeline` is caught internally and returned as `CommitResult(success=False)`, which the CLI translates to exit 1 -- but the design specifies exit 2 for clean-file errors ("Clean-files error (exit 2)"). The CLI unconditionally exits 1 for all pipeline failures, conflating input validation errors (exit 2) with runtime pipeline errors (exit 1).

**Design reference:** Outline lines 217-223 specify clean-files as exit 2 with STOP directive.

### C-2: No test for `no-edit` + `amend` commit (no message, keep existing)

**File:** `tests/test_session_commit_pipeline_ext.py`
**Axis:** functional completeness
**Severity:** critical

Design C-5 specifies: "`no-edit` keeps existing commit message -- `## Message` section omitted." The parser test (`test_parse_commit_input_edge_cases` line 98-104) validates that `amend` + `no-edit` without `## Message` parses correctly. But no pipeline test exercises the actual `git commit --amend --no-edit` path through `commit_pipeline`. The `_git_commit` function passes `--no-edit` when the flag is set, but this code path has zero integration coverage.

## Major Findings

### M-1: `test_commit_no_vet` tests the wrong thing

**File:** `tests/test_session_commit_validation.py:70-92`
**Axis:** specificity, vacuity
**Severity:** major

The test is named `test_commit_no_vet` and its docstring says "Default pipeline calls vet_check." This tests that vet_check IS called when `no-vet` is NOT in options -- it does not test the `no-vet` option itself. There is no test verifying that when `no-vet` IS in options, `vet_check` is NOT called. The `no-vet` option path from C-4 is untested at the pipeline level.

### M-2: Session continuation header not tested

**File:** `tests/test_session_status.py`
**Axis:** functional completeness
**Severity:** major

Design specifies: "When git tree is dirty, prepend `Session: uncommitted changes -- /handoff, /commit`." And: "If any plan-associated task has status `review-pending`, append `/deliverable-review plans/<name>`." Neither the session continuation header rendering nor its conditional display is tested. The `status/cli.py` implementation also does not implement this feature, suggesting a gap in both implementation and test.

### M-3: `_git changes` output does not include diff content in dirty-repo test

**File:** `tests/test_git_cli.py:86-106`
**Axis:** specificity
**Severity:** major

The assertion at line 106 uses `or`: `assert "modified content" in result.output or "diff" in result.output.lower()`. This disjunction weakens the test -- it passes if either condition holds. The design (S-5) says output "includes both the file list and the diff." The test should verify both are present, not either/or.

### M-4: Handoff H-2 committed detection modes not fully tested

**File:** `tests/test_session_handoff.py`
**Axis:** functional completeness
**Severity:** major

Design H-2 specifies three modes based on diff against HEAD: (1) no diff = overwrite, (2) old removed + new present = append, (3) old preserved with additions = auto-strip. The tests exercise mode 1 (overwrite in `test_write_completed_replaces_section`) and mode 3 partially (`test_write_completed_with_accumulated_content`), but the implementation delegates all three modes to a single overwrite operation (`_write_completed_section`). While this is a valid simplification, mode 2 (append) is never tested -- the test `test_write_completed_with_empty_section` tests empty-section overwrite, not the append-after-agent-cleared-old scenario with git diff detection.

### M-5: No test for `_validate` dispatch function

**File:** `tests/test_session_commit_validation.py`
**Axis:** coverage
**Severity:** major

The `_validate()` function in `commit_pipeline.py:151-184` is the central dispatch that routes between `_run_precommit` / `_run_lint` and `vet_check`. While `test_commit_just_lint` and `test_commit_no_vet` indirectly test parts of it, there is no direct test for:
- `_validate` returning vet failure with "stale" reason formatting (lines 175-176)
- `_validate` returning vet failure with unknown reason (line 178)

### M-6: Status CLI does not populate plan_states from filesystem

**File:** `tests/test_session_status.py:277-291`
**Axis:** conformance
**Severity:** major

The `status/cli.py` sets `plan_states` by iterating tasks and defaulting to empty string (line 34: `plan_states.setdefault(task.plan_dir, "")`). The design specifies: "claudeutils _worktree ls for plan states and worktree info" -- plan states should come from filesystem discovery, not empty defaults. The test passes because it doesn't verify plan state values. The CLI comment on line 59 acknowledges this: "Plan discovery deferred to Phase 4+". This is an incomplete implementation that the test accepts.

### M-7: `format_diagnostics` tested but not wired into handoff CLI

**File:** `tests/test_session_handoff.py:287-334`, `src/claudeutils/session/handoff/cli.py`
**Axis:** excess (test for unused code path)
**Severity:** major

The `format_diagnostics` function from `handoff/context.py` is tested with three tests (precommit pass, precommit fail, learnings age). However, the handoff CLI (`handoff/cli.py`) does not call `format_diagnostics` -- it manually constructs git output with inline `subprocess.run` calls (lines 57-72). The diagnostic tests cover code that is not integrated into the CLI pipeline. The design (H-3) specifies diagnostic output should include git status/diff, which the CLI does produce, but through a different code path than the tested function.

### M-8: No test for old format tasks causing fatal error in status

**File:** `tests/test_session_status.py`
**Axis:** functional completeness
**Severity:** major

Design ST-2 specifies: "Old format (no metadata) -> fatal error (exit 2). Mandatory metadata (command, plan reference) enforces plan-backed task rule." The test `test_parse_session_old_format` in `test_session_parser.py` shows old-format tasks parse with `model=None`. But no test verifies that status CLI rejects old-format sessions with exit 2. The current implementation silently accepts them.

## Minor Findings

### m-1: Duplicated `_init_repo` helper across 6 test files

**Files:** `test_session_commit.py:163`, `test_session_commit_cli.py:15`, `test_session_commit_pipeline.py:15`, `test_session_commit_pipeline_ext.py:15`, `test_session_commit_validation.py:15`, `test_session_handoff.py:155`
**Axis:** independence (structural, not behavioral)
**Severity:** minor

Six test files define their own `_init_repo` helper. `test_git_cli.py` imports from `tests.pytest_helpers`. The commit-related helpers are nearly identical (some include `README.md` creation, some don't). Should use the shared `tests.pytest_helpers.init_repo_at`.

### m-2: `test_detect_parallel_blocker_excludes` uses fragile blocker format

**File:** `tests/test_session_status.py:263-271`
**Axis:** specificity
**Severity:** minor

The blocker input `[["Blocker: Alpha blocks Beta"]]` is a single string containing both task names. The implementation (`_build_dependency_edges`) joins all blocker text and checks if both names appear anywhere. This means two unrelated blockers mentioning different tasks would falsely create a dependency. The test doesn't exercise this edge case and the blocker format doesn't match the session.md Blockers/Gotchas section format.

### m-3: `SESSION_FIXTURE` defined after its first use

**File:** `tests/test_session_status.py:308-326`
**Axis:** clarity
**Severity:** minor

`SESSION_FIXTURE` is used at line 281 in `test_session_status_cli` but defined at line 308. This is valid Python but reduces readability.

### m-4: Weak assertion on vet check CLI failure

**File:** `tests/test_session_commit_cli.py:103`
**Axis:** specificity
**Severity:** minor

The assertion `assert "unreviewed" in result.output.lower() or "Vet" in result.output` uses a disjunction. The design specifies the exact output format `**Vet check:** unreviewed files`. The test should match the expected format specifically.

### m-5: `test_commit_amend_parent` uses `len(commits) == 2` without explaining init commit

**File:** `tests/test_session_commit_pipeline_ext.py:282`
**Axis:** clarity
**Severity:** minor

The assertion `assert len(commits) == 2` is correct (init + amended) but the test creates three logical commits (init from `_init_repo`, "original", then amend replaces "original"). Expected count 2 is: init + amended-original. A comment would clarify.

## Verdict

**Result:** Rework required

Two critical findings (C-1: exit code mismatch for clean-file errors, C-2: missing no-edit+amend pipeline test) and five major findings with coverage gaps against design-specified scenarios. The test suite has good structural coverage of the happy paths and parser edge cases, but several design-specified behaviors (session continuation header, plan state discovery, old-format fatal error, no-vet option verification) lack test coverage.

Priority for rework:
1. C-1: Fix exit code semantics for clean-file errors (implementation + test)
2. C-2: Add no-edit+amend pipeline integration test
3. M-1: Add actual no-vet test (vet_check NOT called when no-vet specified)
4. M-7: Either wire format_diagnostics into CLI or remove dead code + tests
5. Remaining major items based on implementation completeness decisions
