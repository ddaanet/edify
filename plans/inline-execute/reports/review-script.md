# Review: triage-feedback.sh + test_triage_feedback.py

**Scope**: `agent-core/bin/triage-feedback.sh` (84 lines), `tests/test_triage_feedback.py` (581 lines)
**Date**: 2026-02-27
**Mode**: review + fix

## Summary

Script implements FR-5, FR-6, FR-7 correctly at the behavioral level — evidence collection, classification comparison, and log append all work. Two bash safety bugs (missing `-e`, wrong exit code for usage error) match project conventions violations confirmed by comparing all peer scripts in `agent-core/bin/`. Test file is 45% over the 400-line soft limit due to repeated git add/commit boilerplate; a helper function would eliminate ~150 lines. All issues fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

1. **Missing `-e` (errexit) in `set` options**
   - Location: `agent-core/bin/triage-feedback.sh:3`
   - Problem: `set -uo pipefail` omits `-e`. If git fails (bad baseline commit SHA, not a git repo), subsequent variables get empty string values and the script continues silently. Every peer script in `agent-core/bin/` uses `set -euo pipefail`.
   - Fix: Add `-e` to match project convention. Add `|| true` to grep commands in subshell assignments where non-zero exit is expected (empty diff, missing classification pattern).
   - **Status**: FIXED

2. **Usage error exits 0 instead of 1**
   - Location: `agent-core/bin/triage-feedback.sh:10`, `tests/test_triage_feedback.py:93`
   - Problem: `exit 0` on missing args signals success to callers. The `/inline` skill and any CI integration that checks exit codes will interpret a bad invocation as success. All peer scripts (`task-context.sh`, `recall-check.sh`) exit 1 on usage error. The test asserts `returncode == 0`, reinforcing the bug.
   - Fix: Change `exit 0` to `exit 1` in script; update test assertion to `returncode == 1`.
   - **Status**: FIXED

### Major Issues

1. **Test file at 580 lines — 45% over soft limit**
   - Location: `tests/test_triage_feedback.py:1-581`
   - Problem: The 400-line limit exists to keep test files navigable (per testing.md: "Maintain 400-line limit while keeping related tests together"). The excess came from repeated git add/commit boilerplate: every test that staged a file ran the same 3 `subprocess.run` calls (add, commit) across 8 test functions — roughly 150 lines of duplication.
   - Fix: Extracted `_git_add_commit(repo_path, filename, content, message)` helper. Used across all 7 tests that staged files. File reduced from 581 to 423 lines. Residual 23 lines over limit is from test function bodies themselves (13 tests × ~30 lines), not duplication — cannot split further without separating coherent groups.
   - **Status**: FIXED

### Minor Issues

1. **Trivial docstring on `_init_repo` restates return annotation**
   - Location: `tests/test_triage_feedback.py:12-15`
   - Note: "Returns (repo_path, commit_sha)" duplicates the `-> tuple[Path, str]` annotation. Per project conventions: "Docstrings only for non-obvious behavior."
   - **Status**: FIXED

2. **Behavioral code grep has false positives for comments**
   - Location: `agent-core/bin/triage-feedback.sh:27`
   - Note: Pattern `^\+.*(def |class |function )` matches removed-then-added comment lines like `+# def old_function():` or added strings containing `def `. This produces `behavioral_code="yes"` for prose files that happen to mention these keywords. Divergence heuristics are initial estimates per C-3 (scope OUT), but the grep pattern correctness is IN scope.
   - Fix: Exclude comment lines from behavioral code detection.
   - **Status**: FIXED

## Fixes Applied

- `agent-core/bin/triage-feedback.sh:3` — `set -uo pipefail` → `set -euo pipefail` (errexit)
- `agent-core/bin/triage-feedback.sh:10` — `exit 0` → `exit 1` (usage error signals failure)
- `agent-core/bin/triage-feedback.sh:15` — `|| true` on `grep -v "file.*changed"` pipeline — grep exits 1 on empty diff with no lines to filter; expected non-zero per error-handling rules
- `agent-core/bin/triage-feedback.sh:27` — behavioral code grep excludes comment lines (`^\+[^#]*`)
- `agent-core/bin/triage-feedback.sh:35` — `|| true` on classification grep — grep exits 1 if classification pattern absent from file
- `tests/test_triage_feedback.py:93` — test assertion updated: `returncode == 1` for missing-args case
- `tests/test_triage_feedback.py:11-76` — `_init_repo` docstring trimmed; `_git_add_commit` helper extracted; all 7 test functions using add/commit boilerplate updated; test file reduced from 581 to 423 lines

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-5: evidence collection (files changed, report count, behavioral code) | Satisfied | Script lines 15, 22, 27; tests `test_files_changed_count`, `test_report_count_excludes_preexecution`, `test_behavioral_code_detected` |
| FR-6: classification comparison + verdicts | Satisfied | Script lines 37-51; tests `test_underclassified_simple_with_behavioral_code`, `test_overclassified_complex_minimal_changes`, `test_match_moderate` |
| FR-7: log append, silent skip on no-classification | Satisfied | Script lines 69-81; tests `test_log_created_with_entry`, `test_log_appends_multiple_entries`, `test_no_classification_skips_log` |
| D-2: script interface `triage-feedback.sh <job-dir> <baseline-commit>` | Satisfied | Script lines 5-11 |
| D-2: structured output (evidence + verdict) | Satisfied | Script lines 55-66; test `test_basic_invocation_produces_output` |
| D-2: missing classification.md → silent skip | Satisfied | Script line 34; test `test_no_classification_skips_log` |

---

## Positive Observations

- E2E test approach with real git repos in `tmp_path` matches the project's "when preferring e2e over mocked subprocess" decision exactly.
- `_init_repo` helper cleanly isolates setup boilerplate and is called consistently across tests.
- Report exclusion test (`test_report_count_excludes_preexecution`) verifies behavior, not just structure — asserts the exact count after including and excluding pre-execution artifacts.
- Log append test verifies two separate rows, not just file existence — catches accumulation bugs.
- Test setup failures use `check=False` + explicit assertions with stderr, matching the project's "When Test Setup Steps Fail" pattern.

## Pre-existing Lint Failure (Out of Scope)

`just check` fails on `agents/session.md:37` — task name "Process execution feedback" is 26 characters, one over the 25-character limit. This is a pre-existing modification to `agents/session.md` introduced by the task execution agent before this corrector review. Not in scope (reviewed files: `agent-core/bin/triage-feedback.sh`, `tests/test_triage_feedback.py`). Confirmed pre-existing: `git stash` + `just check` passes cleanly.
