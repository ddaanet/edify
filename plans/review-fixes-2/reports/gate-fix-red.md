# RED report: gate-fix-red (D-90 re-invocation fix, option b)

Tests uncommitted. Scripts untouched except for mutation-and-restore.

## Tests

| Id | Result on unchanged scripts |
|---|---|
| A `tests/test_changed_files.py::test_pipeline_record_under_plans_reports_is_dropped` | FAILED on assertion |
| B `tests/test_triage_feedback.py::test_reports_exclude_the_tdd_audit_report` | FAILED on assertion |
| C `tests/test_triage_feedback_log.py::test_rerun_after_the_closing_commit_appends_no_row` | FAILED on assertion |
| D `tests/test_changed_files.py::test_paths_with_space_and_non_ascii_bytes_are_listed_whole` (amended) | passes; proven by mutation below |

A failure line (the three plans/reports paths are listed; git's sorted order of the expected list verified by the near-misses appearing in that order):

    At index 4 diff: 'plans/reports/explore-x.md' != 'plans/reportsx.md'
    Left contains 3 more items, first extra item: 'plans/reports/sub/x.md'

B failure line:

    assert '- Reports: 0' in [... '- Reports: 1' ..., verdict 'underclassified']

C failure line (second run, after the closing commit; evidence compare precedes the row count):

    At index 1 diff: '- Files changed: 2' != '- Files changed: 1'
    (second run also read Reports: 1, verdict match)

Module docstring of `tests/test_changed_files.py` now names `plans/reports/` among the dropped records (D-90). Line counts: test_triage_feedback.py 366, test_triage_feedback_log.py 239, test_changed_files.py 381. `ruff check` clean; `ruff format` applied to test_triage_feedback_log.py (only my additions changed).

## Fixtures tried and rejected

None. (C was written once as specified; the first-run `## Evidence`/`## Verdict` comparison reads the first run's stdout, not the log, so a verdict flip is caught on its own line.)

## Mutation proof

Test D, against `plugin/skills/build/scripts/changed-files.sh`, one mutation at a time by exact string replacement (each string occurred once, asserted by the replacement script), restored by the inverse replacement.

1. Newline read of `core.quotepath=off` diff.
   Replace `git diff --name-only --no-renames -z "$base_sha" HEAD -- | while IFS= read -r -d '' path; do` with `git -c core.quotepath=off diff --name-only --no-renames "$base_sha" HEAD -- | while IFS= read -r path; do`.
   D reds on its assertion: `At index 1 diff: '"back\\\\slash.txt"' != 'back\\slash.txt'` (café.txt and inbox/é.md handled; the backslash path C-quoted).
   Restore proof: grep `core.quotepath` in the script: 0 hits; D green (1/1 passed).
2. `read` without `-r`.
   Replace `while IFS= read -r -d '' path; do` with `while IFS= read -d '' path; do`.
   D reds: `At index 1 diff: 'backslash.txt' != 'back\\slash.txt'`.
   Restore proof: grep `read -d ''`: 0 hits; D green.
3. Outline's original word-split mutant (`$(git diff --name-only ...)`, NUL-fed to the same loop).
   Replace the diff line with `printf '%s\0' $(git diff --name-only --no-renames "$base_sha" HEAD --) | while IFS= read -r -d '' path; do`.
   D reds: `Left contains 2 more items, first extra item: 'my'` (also quoted names).
   Restore proof: grep `printf '%s\0'`: 0 hits; D green.
4. Outline's original `-z`-dropped newline read.
   Replace the diff line with `git diff --name-only --no-renames "$base_sha" HEAD -- | while IFS= read -r path; do`.
   D reds: `"caf\303\251.txt"`, `"inbox/\303\251.md"` leak, `"back\\slash.txt"` quoted.
   Restore proof: grep `HEAD -- | while IFS= read -r path`: 0 hits; D green.

## Script integrity

`git diff -- <file> | sha256sum`, before and after all mutations (equal):

- `plugin/skills/build/scripts/changed-files.sh`: `2e30796fa1a4942767faab9c39551463fbfd89e6bb393317ca9f091bc5d2d4c6`
- `plugin/bin/triage-feedback.sh`: `f8e5f9e896804df9ae430109ca90e89cf89303fd90ec6f639ab8d75fa7b5b141` (never mutated)

`git diff --stat` identical before and after: triage-feedback.sh 19 lines, changed-files.sh 4 lines (18 insertions, 5 deletions).
