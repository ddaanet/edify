# 2026-09-21 — `ruff format --check` joins the precommit gate

`just precommit` ran `ruff check` but never `ruff format --check`, so
format-dirty code passed the gate — and `just format` could not have cleaned it
either: both its `ruff`-sourced pipelines piped diffs into a bare `patch` that
cannot guess the strip level from ruff's prefix-free headers, and the helper
meant to print the reformatted files matched a quoted filename that `patch` does
not emit. Two independent defects, each masking the other's symptom. The check
now runs in `run-checks` in both the root `justfile` and `plugin/portable.just`,
since the root file carries its own copy and executes here.

`verify-step.sh` stopped signing off with a bare `CLEAN`, which is
indistinguishable from a check that never ran, and now prints
`CLEAN: tree clean, just precommit passed`. Exit codes are unchanged.
