# Item 1.4 slice 1 — GREEN

Change: `plugin/skills/build/scripts/changed-files.sh` accepts an optional
second argument that must be exactly `--phase`; any other second argument or
more than two arguments is a usage `ERROR:` exit 2 (usage strings now
`changed-files.sh <job> [--phase]`). Under `--phase` the base stays the run
base; the boundary search is not implemented (slice b). Header comment gained
two lines on this behaviour only. No test file edited.

## Order made to pass

1. `test_phase_without_boundary_gives_run_base`: red (exit 2 usage) -> pass
   after the argument check change. The only failing test in the batch.

## Results

- `tests/test_changed_files.py`: 4/4 passed.
- `just test`: 375/376 passed, 1 xfail.
- `shellcheck -x changed-files.sh`: clean.
- `just lint`: only the known RUF100 at `tests/line_limits_helpers.py:32:30`
  (recorded, not acted on).

## Gate

- `just precommit` recap: `✓ Precommit OK` (version consistent 0.3.0; tests
  cached; line-limit warnings for `plugin/agents/corrector.md` 682,
  `outline-corrector.md` 450, `design-corrector.md` 460 lines > 400, for the
  code review to judge; design links 87 decisions indexed).
- `tmp/.test-sentinel`: `982532326 591119`
