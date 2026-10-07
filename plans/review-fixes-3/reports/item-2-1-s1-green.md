# Item 2.1 slice 1 — GREEN

## Changed

`plugin/skills/build/scripts/changed-files.sh`:

- The filtered list is captured in `paths=$(git diff ... | while ... done) || { ERROR: git diff failed; exit 2 }`.
  The NUL-delimited read (`git diff -z`, `read -r -d ''`) is unchanged. Under
  `pipefail` a failing `git diff` fails the substitution, so the `||` arm
  routes to exit 2.
- `BASE: <sha>` and the list print only after the capture succeeds. The list
  prints only when non-empty, so an empty list still gives `BASE:` alone. Both
  prints keep `|| exit 2`, so a write failure never exits 1. Exit 0 and exit 1
  output are unchanged.
- Header comment: states the order (list built in full before `BASE:` prints,
  so a failing diff leaves `ERROR:` alone on stdout), cites D-90. The D-90
  paragraph's over-80 line 26 is reflowed; no comment content removed. Over-80
  code lines left alone.
- shellcheck: only the pre-existing SC1091 info on the `source` line.

## Tests (order made to pass)

1. `tests/test_changed_files_errors.py::test_late_diff_failure_prints_error_alone` — passes.
2. `tests/test_changed_files*.py` — 16 passed.

No test file edited.

## Gate

`just lint`: Lint OK. `just precommit` recap: `Precommit OK` (411/412 passed,
1 xfail; version consistent; design-links 94 decisions).
Warnings (not acted on): oversized-file `plugin/agents/corrector.md` 682,
`outline-corrector.md` 450, `design-corrector.md` 460 > 400.
`tmp/.test-sentinel`: `1109836558 671832`
