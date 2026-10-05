# Review: Item 1.1 slice 1 — code review (review-fixes-2)

**Scope**: `plugin/bin/triage-feedback.sh` as changed by `2a0a3ffa`, and the
whole script audited under `shell-scripting:shell-gotchas` rule 2 (bash 3.2 /
macOS portability included). Tests read for context and extended by one test
for the untested exit-1/2 handling, as the dispatch allowed.
**Date**: 2026-10-05
**Mode**: review + fix

## Summary

The GREEN implements slice 1's contract: `<job>`-only usage (exit 1, `Usage:`
on stderr), `changed-files.sh` located at `../skills/build/scripts/` by the
`verify-step.sh` idiom, `BASE:` and list parsed with parameter expansion,
Files changed = list length, `<base> HEAD` diff failure → `ERROR:` on stdout,
exit 2. The `changed-files.sh` failure path was correct but unpinned; a test now
pins it, proved by two mutations. One minor fix: data printed with `echo`.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`changed-files.sh` exit 1/2 handling untested**
   - Location: `plugin/bin/triage-feedback.sh:22-28`
   - Problem: the Interfaces block makes `NO-BASE:`/`ERROR:` from
     `changed-files.sh` an exit-2 contract with no log row, and the
     `|| status=$?` exists only because an unguarded capture under `set -e`
     exits 1 silently — the usage code, with the cause discarded. No test of
     Item 1.1's slices reaches it, so deleting the guard or the print stays
     green.
   - Fix: `test_no_base_is_an_error_with_no_log_row` in
     `tests/test_triage_feedback.py`. Fixture: no committed item report,
     `classification.md` at `Simple`, a committed `def` (a run reaching a
     verdict would log `underclassified`). Asserts a `NO-BASE: ` line, an
     `ERROR: ` line, no `## Evidence`, exit 2, no log file.
   - **Status**: FIXED

### Minor Issues

1. **`changed-files.sh`'s output printed with `echo`**
   - Location: `plugin/bin/triage-feedback.sh:25`
   - Note: shell-gotchas rule 5 — arbitrary data goes through `printf '%s\n'`;
     the output carries a job name and git diagnostics (merged by
     `changed-files.sh`'s `exec 2>&1` until Item 1.5).
   - **Status**: FIXED

## Fixes Applied

- `plugin/bin/triage-feedback.sh:25` — `echo "$changed_output"` →
  `printf '%s\n' "$changed_output"`.
- `tests/test_triage_feedback.py` — added
  `test_no_base_is_an_error_with_no_log_row` (module 153 → 184 lines; no
  helper needed).

Files changed: `plugin/bin/triage-feedback.sh`, `tests/test_triage_feedback.py`.

## Mutation proof

Each mutation an exact in-place replacement, run, then restored by the
inverse replacement; `git diff` after the last restore shows only the two
fixes above.

| Mutation | Tests run | Result |
|---|---|---|
| `"$job_dir") \|\| status=$?` → `"$job_dir")` (unguarded capture) | new test | RED at `NO-BASE:` assertion, empty stdout |
| delete `printf '%s\n' "$changed_output"` | new test | RED at `NO-BASE:` assertion; stdout only `ERROR: changed-files.sh exited 1` |
| list count → `git diff --name-only "$baseline_commit" HEAD \| wc -l \| tr -d ' '` (the raw diff the slice rules out) | whole module | RED: `test_files_changed_is_the_review_gates_list` (`Files changed: 6`) and `test_files_changed_counts_committed_changes_only`; other 4 green, as expected |

Not covered by the new test: removing only the `exit 2` from the guard. The run
then falls through to `git diff "NO-BASE: …" HEAD`, which fails and exits 2 via
the git-failure branch, so the observable contract (exit 2, `ERROR:`, no row)
still holds. No assertion was added for it: a single-`ERROR:` assertion would
pin message count, which the interface does not specify.

## Whole-script audit (shell-gotchas rule 2)

- `shellcheck` 0.10.0 default: clean. `--enable=all`: SC2250 (brace style,
  throughout, pattern-consistent) and SC2312 on line 117 (pre-existing).
- bash 3.2: `$'\n'` in `${var%%…}`/`${var#…}`, `[[ == *$'\n'* ]]`,
  `compgen -G`, `<<<` all exist in 3.2. No GNU-only flags; `wc -l | tr -d ' '`
  handles BSD padding; `date -u +%Y-%m-%d` portable; `find -maxdepth`/`-exec`
  exist on BSD.
- `BASH_SOURCE[0]` under PATH lookup is the full path; relative invocation
  resolves against the unchanged CWD. `changed-files.sh` is mode 100755.
- Any non-zero `changed-files.sh` status (126/127 included) takes the exit-2
  branch.
- Lines owned by later slices, not flagged: reports `find` and its stale `KD-3`
  comment (slice 2); diff without `--no-renames`, `--` and list pathspecs, so a
  tracked file named `HEAD` makes the diff ambiguous (slices 3/5); here-string
  and `xargs || true`, label fall-through to `match` (slices 4–5); log append
  (Item 1.2).
- Pre-existing, outside the change: a `set -e` exit from `mkdir`/log write
  exits 1, the usage code; `find … -name 'review-*.md' | wc -l` matches
  directories and overcounts a newline name. No caller branches on 1 vs 2
  (`finishing.md` §2 stops on any non-zero), so neither is flagged.

## Requirements Validation

| Requirement (slice 1 scope) | Status | Evidence |
|---|---|---|
| `<job>`-only call, usage exit 1 | Satisfied | `triage-feedback.sh:5-10` |
| list from `changed-files.sh` via `../skills/build/scripts/` | Satisfied | `:12-23` |
| Files changed = list length | Satisfied | `:29-40`; mutation-proved |
| git failure → `ERROR:` stdout, exit 2 | Satisfied | `:71-74`; `test_failing_diff_is_an_error_not_no` |
| `changed-files.sh` exit 1/2 → output, `ERROR:`, exit 2, no row | Satisfied | `:22-28`; new test, mutation-proved |
| Comments cite D-numbers (m8) | Satisfied for touched lines | `:18-21` cites D-88/D-90/D-91 (all in `docs/decisions.md`); `(KD-6)` removed from `:57-58` |

## Verification

- `tests/test_triage_feedback.py`: 6/6 passed.
- `just lint`: Lint OK.
- `just precommit`: version consistency, 384/385 passed + 1 xfail, line limits
  (three pre-existing `oversized-file` warnings on corrector agents), design
  links — Precommit OK.

## Positive Observations

- `|| status=$?` with a comment naming why — the `set -e` capture trap
  handled explicitly.
- Base and list parsed by parameter expansion, no subprocess.
- The newline-in-path residual bound is stated in a comment, not implied away.
