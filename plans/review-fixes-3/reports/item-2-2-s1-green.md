# Item 2.2 slice 1 GREEN

Test: `test_subdirectory_run_measures_the_repository_root`.

## Order made to pass
1. `test_subdirectory_run_measures_the_repository_root` (red on `- Reports: 1`).
   `plugin/bin/triage-feedback.sh`: `script_dir` resolved absolute with
   `cd ... && pwd`, then `repo_root=$(git rev-parse --show-toplevel)` and
   `cd "$repo_root"` before `changed-files.sh` runs (D-90). Passes.
2. Bash 3.2 parse defect found while checking: the bare `case` pattern
   `review.md | ... ) continue ;;` inside `$(...)` made `bash -n` fail under
   3.2.57 (present at HEAD, not introduced here). Outline note for Item 2.2
   requires the script to parse under 3.2, so the pattern got a leading `(`.

Not implemented (slice 2): guarding a failing `rev-parse`/`cd` with one
`ERROR:` line and exit 2, and the residual-bound comment.

## Bash 3.2
- `/tmp/claude-1000/bash32/bin/bash -n plugin/bin/triage-feedback.sh`: before
  the paren fix, syntax error at the `case` line (HEAD has the same error);
  after, exit 0.
- `bash --version` on that PATH: GNU bash 3.2.57(2).
- `PATH=bash32:$PATH pytest -p no:markdown_report tests/test_triage_feedback*.py`:
  before the paren fix 23 failed, 1 passed (all from the parse error); after,
  24 passed.
- Known `changed-files.sh` absent-`exempt-paths.sh` defect: not reached by the
  triage modules; not touched.

## Gate
- `just precommit` (default PATH): `Precommit OK`; recap `Version consistent`,
  `412/413 passed, 1 xfail`, line limits (warnings only: corrector.md 682,
  outline-corrector.md 450, design-corrector.md 460, none touched here),
  `design-links: 94 decisions indexed ... 9 nodes present`.
- `tmp/.test-sentinel`: `3466804110 675705`.
