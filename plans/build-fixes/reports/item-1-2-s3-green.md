# Item 1.2 / Slice 3 — GREEN report

`test_no_item_report_exits_1` in `tests/test_changed_files.py`.

## Mode

GREEN. Batch: one failing test, `test_no_item_report_exits_1`. Out of scope:
Item 1.3 (`triage-feedback.sh`) and every prose item, per the dispatch.

## Implementation

`plugin/skills/build/scripts/changed-files.sh`: inserted a check between the
`first_commit=${first_commit%%$'\n'*}` line and the existing parent-lookup
block. When `first_commit` is empty (no committed `plans/<job>/reports/item-*`
report at all), the script now prints
`NO-BASE: no committed plans/<job>/reports/item-* report` and exits 1, before
the parent lookup runs. A root commit that adds the report (`first_commit`
non-empty, but it has no parent) still falls through to the pre-existing
`git rev-parse --verify --quiet "${first_commit}^"` branch, unchanged, which
stays exit 2 `ERROR:`. Updated the preceding comment on that branch, and the
top-of-file header comment's KD-1 paragraph, to state the exit-1/exit-2 split
explicitly.

No other file touched. `scripts/exempt-paths.sh` and `verify-step.sh` were not
in this slice's scope and were not edited.

## Tests run, in order made to pass

1. `tests/test_changed_files.py::test_no_item_report_exits_1` — the batch's one
   failing test. Ran alone first, against the edited script: PASSED.
2. `tests/test_changed_files.py` (full module, all 3 tests) — PASSED, no
   regression on `test_base_is_parent_of_first_item_report_commit` or
   `test_exempt_paths_committed_in_the_run_are_dropped`.
3. `tests/test_verify_step.py` (full module, 8 tests) — PASSED. `verify-step.sh`
   was not touched by this slice; run to confirm no cross-script regression
   since both source `exempt-paths.sh`.
4. `shellcheck -x plugin/skills/build/scripts/changed-files.sh` — clean, no
   output, exit 0.
5. `just test` (full suite) — 372/373 passed, 1 xfail. Same counts as before
   this slice's edit.

## Gate verdict

`just lint`: `tests/line_limits_helpers.py:32:30: RUF100 [*] Unused `noqa`
directive (non-enabled: `PLR0913`)` — pre-existing, named in the dispatch as
known; not acted on. `just lint` recap: "372/373 passed, 1 xfail" / "✗ Lint
failed" (on that one RUF100 finding alone; nothing in this slice's diff
contributes to it).

`just precommit` recap:

```
[version consistency] Version consistent: 0.3.0
Tests cached (inputs unchanged)
[line limits] oversized-file: plugin/agents/corrector.md: 682 lines > 400
[line limits] oversized-file: plugin/agents/outline-corrector.md: 450 lines > 400
[line limits] oversized-file: plugin/agents/design-corrector.md: 460 lines > 400
[design links] design-links: 87 decisions indexed, defined once, conclusions match, 8 nodes present
✓ Precommit OK
```

The three `oversized-file` lines are pre-existing agent-definition files
unrelated to this slice's diff (`changed-files.sh` is 104 lines); recorded per
the dispatch's instruction, not acted on — a code-review judgement call, not
this dispatch's.

`tmp/.test-sentinel`: `1443406045 584538`

## Scope

Only `plugin/skills/build/scripts/changed-files.sh` was edited for
implementation. `tests/test_changed_files.py` is unchanged from the test
review's committed-pending state (no test file edited in this dispatch, per
the GREEN-mode prohibition). No commit made yet at report-write time; this
report rides the commit it names.
