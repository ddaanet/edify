# Item 1.1/1 RED — review-fixes-2

Mode RED. SUT `plugin/bin/triage-feedback.sh` untouched (it exits 1 on usage
with one argument, which is the red). Files: `tests/test_triage_feedback.py`
(split), new `tests/triage_feedback_helpers.py`. No commit.

## Split

Helpers (`_run_git`, `_init_repo`, `_commit`, `_commit_item_report`,
`_run_triage`, `_triage_lines`, `_def_edits_pending`, `JOB = "j"`) moved to
`tests/triage_feedback_helpers.py`. The two-argument `<baseline>` parameter
is gone: calls are `triage-feedback.sh <job>`. `_commit_item_report` commits
`plans/j/reports/item-1-1.md` with the run's files, so the base is the
fixture's prior commit. Test module is 150 lines, helpers 106; no docstring
shaved. Comments cite D-88/D-90/D-91, no KD.

## Per-test output (all fail on assertion, none ERROR)

- `test_files_changed_is_the_review_gates_list` (new): stdout assertion,
  `assert '- Files changed: 2' in []`; script returned 1, stderr
  `Usage: triage-feedback.sh <job-dir> <baseline-commit>`.
- `test_files_changed_counts_committed_changes_only` (moved): `_triage_lines`
  exit assertion, same Usage output.
- `test_uncommitted_definition_is_not_behavioral` (moved): same, first call.
- `test_forced_color_does_not_hide_definitions` (moved): same.
- `test_failing_diff_is_an_error_not_no` (moved): `assert 1 == 2` on return
  code. Tightened from `!= 0` to `== 2` (interface: git failure is exit 2);
  the old `!= 0` passed on the usage exit and would have reached the stderr
  assertion only.

Deleted: `test_simple_with_review_reports_matches` (no item report; slice 2
replaces it). All other existing tests were moved; none left on the
two-argument form.

## Fixtures tried and rejected

- Keeping the old `_init_repo` seed as the base and putting the item report
  in the pre-run commit: rejected, the base is the parent of the first
  item-report commit, so the report must be in a run commit.
- Failing-diff test with `returncode != 0` kept: rejected, passes on the
  usage exit, so it would not red on the exit.

## Mutation proof

None needed; every test reds against the unchanged script.
