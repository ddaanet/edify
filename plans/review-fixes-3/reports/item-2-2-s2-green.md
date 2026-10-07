# Item 2.2 slice 2 GREEN

## Order made to pass

1. `test_outside_a_work_tree_is_one_error_line` (red): guarded `git rev-parse --show-toplevel` with `|| status=$?`, printing one `ERROR: not inside a git work tree` line on stdout and exiting 2 before `changed-files.sh` runs. Git's stderr passes through. Passed.
2. `test_cdpath_does_not_move_the_script_dir`: already green, kept green.

Also guarded the `cd "$repo_root"` (one `ERROR: cannot change to <root>` line, exit 2). The residual-bound comment (no test; needs fault injection) sits above it.

## Bash 3.2

- `/tmp/claude-1000/bash32/bin/bash -n plugin/bin/triage-feedback.sh`: syntax OK; bash --version on that PATH is 3.2.57(2).
- `PATH=/tmp/claude-1000/bash32/bin:$PATH .venv/bin/pytest -p no:markdown_report tests/test_triage_feedback*.py`: 26 passed.

## Gate

- `just precommit`: `Precommit OK`; test report 414/415 passed, 1 xfail (tests ran, not cached).
- Warnings (not acted on): oversized-file plugin/agents/corrector.md 682, outline-corrector.md 450, design-corrector.md 460 (> 400).
- tmp/.test-sentinel: 1557858877 679781
