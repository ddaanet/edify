# GREEN report: gate-fix-green (D-90 re-invocation fix)

Nothing staged or committed (review-gate override). Edits left uncommitted.

## Edits (this dispatch's part of the diff)

`plugin/skills/build/scripts/changed-files.sh`:
- `case`: `"$exclude_prefix"*) continue ;;` -> `"$exclude_prefix"* | plans/reports/*) continue ;;`
- D-90 header paragraph now names `plans/reports/`: the pipeline's record across jobs, the triage log among it, so a re-invoked finished job's closing commit does not enter its re-run's list; dropped here, not exempted in `exempt-paths.sh`, which `verify-step.sh` also reads (D-91).
- (The `unset EXEMPT_PATHS_ALTERNATION` lines in the same diff are earlier uncommitted work, kept.)

`plugin/bin/triage-feedback.sh`:
- Reports exclusion `case`: `review.md | review-*.md | final-review.md) continue ;;` -> `... | final-review.md | tdd-audit.md) continue ;;`
- D-90 comment lists `tdd-audit.md` among the review-gate reports.

## Tests, made to pass in this order (each 1/1 passed)

1. tests/test_changed_files.py::test_pipeline_record_under_plans_reports_is_dropped
2. tests/test_triage_feedback.py::test_reports_exclude_the_tdd_audit_report
3. tests/test_triage_feedback_log.py::test_rerun_after_the_closing_commit_appends_no_row
4. tests/test_changed_files.py::test_paths_with_space_and_non_ascii_bytes_are_listed_whole (stayed green)

## Gate

- `just test`: 410/411 passed, 1 xfail.
- First `just precommit` failed on ruff D205 in the test docstring (tests/test_changed_files.py:133); the docstring was fixed outside this dispatch, and I did not edit tests.
- `just precommit` re-run: `Precommit OK`. Checks: version consistency (0.3.0), tests (410/411, 1 xfail), line limits, design links (94 decisions indexed, defined once, conclusions match, 9 nodes present).
- Warnings (for code review, not acted on): oversized-file plugin/agents/corrector.md 682, outline-corrector.md 450, design-corrector.md 460 (> 400).
- tmp/.test-sentinel: `3305904917 665846`.
- Note: `just lint` reformats files in place; it rewrote already-modified docs/decisions.md, docs/references/build-run-state.md, plugin/README.md, plugin/fragments/review-requirement.md, plugin/skills/build/references/phase-boundary.md and tests/test_changed_files.py.
