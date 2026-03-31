# Review: Phase 4 Checkpoint — Justfile Modularization

**Scope**: Phase 4 changes: `plugin/portable.just` (created), `justfile` (modified), `.cache/just-help.txt` (regenerated)
**Date**: 2026-03-21
**Mode**: review + fix

## Summary

Phase 4 extracted the portable recipe stack from the root `justfile` into `plugin/portable.just` and updated the root justfile to import it. The migration is mechanically correct: all required recipes are present, the import works, `set allow-duplicate-variables` ensures the root `bash_prolog` overrides the portable module's, and `just precommit` passes. The `.cache/just-help.txt` was regenerated with `--unsorted` output matching the `help` recipe's invocation.

The `just dev` output shows `patch: invalid option -- 'C'` during `format` — this error was present in the root `justfile` before Phase 4 and is a pre-existing platform mismatch (BSD `patch` option on a GNU `patch` system). Not a Phase 4 regression.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **run-pytest sentinel monitors project-specific paths in portable module**
   - Location: `plugin/portable.just:84`
   - Note: `run-pytest` sentinel computes a hash over `plugin/hooks/` and `plugin/bin/` — these are paths specific to this project. In a consumer project importing `portable.just`, those paths don't exist, and `git ls-files` would silently omit them from the hash, producing a sentinel that ignores actual test input changes.
   - **Status**: DEFERRED — Consumer mode is explicitly deferred (D-8). The function is correct for this project (dev mode). The portability issue is a known consequence of D-8 deferral.

## Fixes Applied

None.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-6: Portable justfile recipes importable by any project | Partial | `portable.just` exists and imports correctly in dev mode; consumer portability deferred (D-8) |

**Gaps:** FR-6 consumer portability is deferred per D-8. `run-pytest` sentinel in portable.just monitors project-specific paths (`plugin/hooks/`, `plugin/bin/`).

## Deferred Items

- **run-pytest sentinel portability** — Reason: Consumer mode path resolution deferred per D-8. Only dev mode (submodule) is in scope for this migration.

---

## Positive Observations

- `set allow-duplicate-recipes` and `set allow-duplicate-variables` correctly configured; root `bash_prolog` overrides portable module's prolog in root context.
- `portable.just` is self-contained: defines its own `bash_prolog` with all required shell functions (`safe`, `end-safe`, `visible`, `fail`, `wt-path`, `add-sandbox-dir`, `sync`, `set-tmpfile`, `report`, `run-checks`, `run-lint-checks`, `run-pytest`, `run-line-limits`, `report-end-safe`).
- All portable recipes specified in outline D-5 are present: `claude`, `claude0`, `lint`, `format`, `check`, `red-lint`, `precommit`, `precommit-base`, `test`, `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge`.
- Project-specific recipes correctly retained in root justfile: `release`, `line-limits`, `green`, `dev`, `setup`, `help`.
- `.cache/just-help.txt` matches `just --list --unsorted` output exactly.
- `just precommit` passes end-to-end.
- Step 4.1 validation passes: `just --justfile plugin/portable.just --list` shows all expected recipes; `just --justfile plugin/portable.just --evaluate bash_prolog` succeeds.
