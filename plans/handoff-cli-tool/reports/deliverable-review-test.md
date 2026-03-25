# L1 Test Review: handoff-cli-tool (RC13)

**Date:** 2026-03-25
**Scope:** 21 test files (~3901 lines), full-scope review
**Axes:** conformance, functional correctness, functional completeness, vacuity, excess, specificity, coverage, independence
**Prior:** RC12 deliverable-review.md (1C/0M/22m), deliverable-review-test.md (0C/0M/10m)

## RC12 Critical Verification

**C-1** `session/cli.py:33-34` — CommitInputError uncaught in commit_cmd

**Status: FIXED**

Evidence: `test_session_commit_cli.py:129-155` `test_commit_cli_submodule_missing_message_exits_2` exercises the full propagation path:
- Sets up a parent repo with real submodule via `create_submodule_origin` + `add_submodule`
- Creates dirty submodule file (`agent-core/new.md`)
- Sends stdin with submodule file listed but NO `## Submodule` section
- `commit_pipeline()` -> `_validate_inputs()` -> raises `CommitInputError`
- New `except CommitInputError` at cli.py:33-34 catches it
- Asserts: exit code 2, `**Error:**` in output, `no ## Submodule` in output

All three S-3 axes verified:
- Output channel: stdout (via `_fail` -> `click.echo`) -- not stderr
- Output format: `**Error:**` structured markdown -- not Click's "Error:" prefix
- Exit code: 2 (input validation) -- not 1 (pipeline error)

**Test quality:** Non-vacuous -- uses real git submodule setup, exercises the full CLI path through CliRunner. Specific -- asserts the exact error message substring (`no ## Submodule`), not just generic error presence.

## RC12 Minor Findings (Test) Status

| RC12 Finding | Status | Evidence |
|---------|--------|----------|
| m-8: SESSION_FIXTURE defined after first usage | NOT FIXED | test_session_status.py:280 -- constant defined at line 280, first usage at line 253. Forward reference still present. |
| m-9: Generic assertion words | NOT FIXED | test_session_commit_pipeline.py:108-125 -- `"continuation"`, `"other line"` unchanged. |
| m-10: Conflated positive/negative paths | NOT FIXED | test_planstate_aggregation.py:102-197 -- two repos in one test function. |
| m-11: Near-redundant tests | NOT FIXED | test_session_handoff.py:217-248 -- both tests still exercise same code path. |
| m-12: Inconsistent submodule helpers | NOT FIXED | test_session_commit_pipeline_ext.py:22-35 local helper vs pytest_helpers imports. |
| m-13: Misleading comment | NOT FIXED | test_session_handoff_committed.py:99-100 -- describes agent behavior, not mode detection. |
| m-14: Autostrip error fallback gap | NOT FIXED | No test for `_find_repo_root` ValueError or `git show` failure in autostrip mode. |
| m-15: Resume from write_session gap | NOT FIXED | No test for resume with `step_reached="write_session"`. Only diagnostics-skip tested. |
| m-16: Pre-H-2 redundant test | NOT FIXED | test_session_handoff.py:217 still present. |
| m-17: No _detect_write_mode unit test | NOT FIXED | Grep confirms zero test references to `_detect_write_mode`. |

Expected: session.md stated m-8 through m-17 were not addressed in the C-1 fix scope. The fix scope was limited to adding the `except CommitInputError` clause and its CLI-level test.

## Coverage Checklist

| # | Scenario | Covered | Test Reference |
|---|----------|---------|----------------|
| 1 | H-2 overwrite (no prior diff) | Y | test_session_handoff_committed.py:46-60 |
| 2 | H-2 append (old cleared, new present) | Y | test_session_handoff_committed.py:88-116 |
| 3 | H-2 autostrip (old preserved with additions) | Y | test_session_handoff_committed.py:122-151 |
| 4 | H-2 committed-state overwrite verification | Y | test_session_handoff_committed.py:66-82 |
| 5 | H-4 step_reached resume: skip to diagnostics | Y | test_session_handoff_cli.py:291-315 |
| 6 | H-4 step_reached: value persistence | Y | test_session_handoff_cli.py:318-338 |
| 7 | H-4 backward compat (missing step_reached) | Y | test_session_handoff.py:313-332 |
| 8 | C-1 vet check: no config passes | Y | test_session_commit.py:263-268 |
| 9 | C-1 vet check: unreviewed fails | Y | test_session_commit.py:295-309 |
| 10 | C-1 vet check: stale fails | Y | test_session_commit.py:312-336, test_session_commit_validation.py:217-257 |
| 11 | C-2 submod files+msg -> both committed | Y | test_session_commit_pipeline_ext.py:41-81 |
| 12 | C-2 submod files, no msg -> error | Y | test_session_commit_pipeline_ext.py:84-106 |
| 13 | C-2 no submod files, msg present -> warning | Y | test_session_commit_pipeline_ext.py:109-136 |
| 14 | C-2 no submod files, no msg -> parent-only | Y | test_session_commit_pipeline_ext.py:139-162 |
| 15 | C-2 multi-submodule ordering | Y | test_session_commit_pipeline_ext.py:332-393 |
| 16 | C-2 missing submodule message through CLI -> exit 2 | Y | test_session_commit_cli.py:129-155 **(C-1 fix test)** |
| 17 | C-3 clean files exit 2 + STOP directive | Y | test_session_commit.py:203-222, test_session_commit_cli.py:101-126 |
| 18 | C-3 clean submodule file shows full path | Y | test_session_commit_pipeline.py:157-212 |
| 19 | C-4 default (precommit + vet) | Y | test_session_commit_validation.py:48-72 |
| 20 | C-4 no-vet | Y | test_session_commit_validation.py:75-98 |
| 21 | C-4 just-lint | Y | test_session_commit_validation.py:21-45 |
| 22 | C-4 just-lint + no-vet | Y | test_session_commit_validation.py:259-291 |
| 23 | C-4 just-lint + amend combined | Y | test_session_commit_validation.py:101-151 |
| 24 | C-5 amend parent-only | Y | test_session_commit_pipeline_ext.py:168-210 |
| 25 | C-5 amend submodule+parent | Y | test_session_commit_pipeline_ext.py:213-284 |
| 26 | C-5 amend validation (HEAD files clean) | Y | test_session_commit_pipeline_ext.py:287-326 |
| 27 | C-5 amend+no-edit | Y | test_commit_pipeline_errors.py:251-284 |
| 28 | C-5 no-edit without amend error | Y | test_session_commit.py:86-88 |
| 29 | C-5 no-edit with message contradicts | Y | test_session_commit.py:100-104 |
| 30 | ST-0 worktree marker skip in Next | Y | test_status_rework.py:151-180 |
| 31 | ST-1 parallel: consecutive independent group | Y | test_session_status.py:165-174 |
| 32 | ST-1 parallel: single task returns None | Y | test_session_status.py:177-180 |
| 33 | ST-1 parallel: shared plan returns None | Y | test_session_status.py:183-189 |
| 34 | ST-1 parallel: cap at 5 | Y | test_session_status.py:208-213 |
| 35 | ST-1 parallel: blocker exclusion | Y | test_session_status.py:216-224, test_status_rework.py:218-267 |
| 36 | ST-2 missing session.md exit 2 | Y | test_session_status.py:266-277 |
| 37 | ST-2 old format exit 2 | Y | test_status_rework.py:118-145 |
| 38 | ST-2 old section name ("Pending Tasks") exit 2 | Y | test_status_rework.py:186-212 |
| 39 | S-3 exit 0 success (commit) | Y | test_session_commit_cli.py:24-52 |
| 40 | S-3 exit 1 pipeline error (vet failure) | Y | test_session_commit_cli.py:69-95 |
| 41 | S-3 exit 2 input validation (empty stdin) | Y | test_session_commit_cli.py:55-66 |
| 42 | S-3 exit 2 input validation (clean file) | Y | test_session_commit_cli.py:101-126 |
| 43 | S-4 parser: all sections | Y | test_session_parser.py:47-84 |
| 44 | S-4 parser: blockers extraction | Y | test_session_parser.py:169-191 |
| 45 | S-4 parser: missing file error | Y | test_session_parser.py:143-146 |
| 46 | S-5 git changes: clean repo | Y | test_git_cli.py:70-83 |
| 47 | S-5 git changes: dirty repo | Y | test_git_cli.py:86-107 |
| 48 | S-5 git changes: submodule | Y | test_git_cli.py:110-134 |
| 49 | S-2 submodule discovery | Y | test_git_helpers.py:49-94 |
| 50 | S-2 git_status porcelain format | Y | test_git_helpers.py:123-155 |
| 51 | Integration: handoff then status | Y | test_session_integration.py:17-80 |

All design-specified scenarios have test coverage. Item 16 (C-1 fix test) is new in RC13.

## Findings

### Carried Minors (from RC12 m-8 through m-17, unaddressed as expected)

**m-8** `test_session_status.py:280` -- conformance -- SESSION_FIXTURE defined after first usage at line 253.
Severity: Minor

**m-9** `test_session_commit_pipeline.py:108-125` -- specificity -- Generic assertion words ("continuation", "other line") in `test_strip_hints_filters_continuation_lines`.
Severity: Minor

**m-10** `test_planstate_aggregation.py:102-197` -- independence -- `test_git_metadata_helpers` conflates positive/negative paths in one function.
Severity: Minor

**m-11** `test_session_handoff.py:217-248` -- independence -- Two tests exercise same `write_completed` -> `_write_completed_section` code path.
Severity: Minor

**m-12** `test_session_commit_pipeline.py:157-212` / `test_session_commit_pipeline_ext.py:22-35` -- conformance -- Inconsistent submodule setup helpers across test files.
Severity: Minor

**m-13** `test_session_handoff_committed.py:99-100` -- functional correctness -- Comment describes agent behavior but not mode-detection rationale for the append test.
Severity: Minor

**m-14** `test_session_handoff_committed.py` -- coverage -- Autostrip error fallback path (`_find_repo_root` ValueError or `git show` failure at pipeline.py:217) has no dedicated test.
Severity: Minor

**m-15** `test_session_handoff_cli.py` -- coverage -- No test for resume from `step_reached="write_session"` (writes performed during resume). Only diagnostics-skip path tested.
Severity: Minor

**m-16** `test_session_handoff.py:217` -- excess -- Pre-H-2 accumulated content test now redundant with committed detection tests in test_session_handoff_committed.py.
Severity: Minor

**m-17** `test_session_handoff_committed.py` -- coverage -- No direct `_detect_write_mode` unit test. Integration tests verify output but don't assert mode selection.
Severity: Minor

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 10 (all carried) |

**C-1 fix verification:** FIXED. `test_commit_cli_submodule_missing_message_exits_2` exercises the full CLI path: `commit_cmd` -> `commit_pipeline` -> `_validate_inputs` raises `CommitInputError` -> caught by new `except CommitInputError` at cli.py:33-34 -> exit 2 with `**Error:**` structured markdown on stdout. All three S-3 axes (channel, format, exit code) verified.

**RC12 minor status:** All 10 test minors (m-8 through m-17) carried unchanged. Expected per session.md scope statement -- the C-1 fix was scoped to adding the except clause and its CLI-level test only.

**New findings:** None. The C-1 fix test is well-constructed: uses real git submodule setup (not mocks), exercises the full CLI pipeline, and makes specific assertions on exit code, output format, and error message content.

**Trend:** RC12 0C/0M/10m -> RC13 0C/0M/10m (same 10 carried minors, no new findings, critical regression closed).
