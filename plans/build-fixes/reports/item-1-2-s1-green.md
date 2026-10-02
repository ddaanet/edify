# Item 1.2 / slice 1 — GREEN report

## Scope

Implement in `plugin/skills/build/scripts/changed-files.sh` only slice 1's
test: `test_base_is_parent_of_first_item_report_commit` — the KD-1 base
derivation, the `BASE: <sha>` line, and the KD-6 NUL-delimited committed diff
with `plans/<job>/` dropped. Exempt-path dropping (`exempt-paths.sh`), the
`NO-BASE:` exit-1 path, and `verify-step.sh` are out of scope (slices 2 and 3,
Item 1.3 onward).

## Implementation

`plugin/skills/build/scripts/changed-files.sh` (new, executable):

- Usage check: exactly one argument (`<job>`); otherwise `ERROR: usage: …`,
  exit 2.
- Base: `git log --diff-filter=A --reverse --format=%H -- "plans/$job/reports/item-*"`,
  captured via command substitution with an explicit `||` check (exit 2 on
  git failure, never silently absorbed by `set -e`'s command-substitution
  blind spot); first line taken via `${first_commit%%$'\n'*}` rather than
  piping to `head` (`set -o pipefail` + an early-exit consumer like `head`
  kills the producer with SIGPIPE — avoided per
  `shell-scripting:shell-gotchas`). Its parent via `git rev-parse "${first_commit}^"`,
  again with an explicit `||` check, exit 2 on failure.
- `BASE: <sha>` printed via `printf`, never `echo` (gotcha: `echo` is
  implementation-defined on backslash/`-`-leading operands).
- Diff: `git diff --name-only -z "$base_sha" HEAD` piped into
  `while IFS= read -r -d '' path; do … done`, reading the NUL-delimited
  stream directly rather than capturing it into a variable first — a bash
  variable cannot hold NUL bytes, so a `var=$(git diff -z …)` capture would
  silently drop every delimiter. `case "$path" in "$exclude_prefix"*) continue ;; esac`
  drops `plans/$job/` paths; quoting `"$exclude_prefix"` in the pattern turns
  off globbing on it, so a job name holding a glob metacharacter still
  matches literally. The pipeline's own failure is caught by the trailing
  `|| { ERROR; exit 2; }`, which `set -o pipefail` makes visible (the `while`
  loop, as the pipe's last, non-early-exiting stage, drains it fully, so no
  SIGPIPE risk).
- `exec 2>&1` and `set -euo pipefail` at the top, matching `verify-step.sh`'s
  house style.
- `shellcheck` clean.

No stub code was carried over from RED beyond the shebang line; the whole
body is new growth against the one failing test in this batch.

## Tests run, in order

1. `PATH=/Users/david/code/edify/.venv/bin:$PATH python -m pytest tests/test_changed_files.py -vv`
   — `test_base_is_parent_of_first_item_report_commit` PASSED on the first
   implementation attempt (one test in this batch; no second attempt needed).
2. `PATH=/Users/david/code/edify/.venv/bin:$PATH just test` — 370/371 passed,
   1 xfail, green.

## D205 interruption (resolved by the orchestrator, not by GREEN)

The first `just lint` run in this dispatch failed on
`tests/test_changed_files.py:76:5: D205` — `_commit`'s original one-line
docstring (83 chars) was rewrapped into a non-compliant multi-line form by
`just lint`'s `format` dependency (`docformatter`, `wrap-summaries = 80`,
`in-place = true`), a mechanical side effect of the mandated gate, not an
edit I made. GREEN mode may not edit a test file to fix it, so this dispatch
stopped and reported `blocked: …` with the full diagnosis. The orchestrator
then edited `tests/test_changed_files.py:76` directly (restructured
`_commit`'s docstring into a one-line summary plus a blank-line-separated
description) and resumed this dispatch. GREEN made no edits to
`tests/test_changed_files.py` at any point in this dispatch.

## Gate verdict

- `PATH=/Users/david/code/edify/.venv/bin:$PATH just lint` — fails only on
  the known, pre-existing `tests/line_limits_helpers.py:32:30: RUF100`
  (named in the dispatch as known; recorded, not acted on here). No other
  finding.
- `PATH=/Users/david/code/edify/.venv/bin:$PATH just precommit` recap:
  `✓ Precommit OK`. `run-checks` (`ruff check`, `ruff format --check`,
  `docformatter -c`, `mypy`) clean; version consistency `0.3.0`; pytest
  sentinel-cached (inputs unchanged since the `just test` run above); line
  limits prints three pre-existing `oversized-file:` lines
  (`plugin/agents/corrector.md`, `plugin/agents/outline-corrector.md`,
  `plugin/agents/design-corrector.md`, all > 400 lines) — allowlisted,
  printed on every green run per the recipe's own comment, not new; design
  links `87 decisions indexed, defined once, conclusions match, 8 nodes
  present`.
- `tmp/.test-sentinel`: `3657500379 575846`.

## Files staged for this commit

- `plugin/skills/build/scripts/changed-files.sh` (new implementation)
- `tests/test_changed_files.py` (unedited by GREEN; its only mutation in this
  dispatch's lifetime was the orchestrator's docstring fix above)
- `plans/build-fixes/reports/item-1-2-s1-red.md`
- `plans/build-fixes/reports/item-1-2-s1-test-review.md`
- `plans/build-fixes/reports/item-1-2-s1-green.md` (this report)
