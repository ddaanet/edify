# Review: review-fixes-2 — scripts, tests and plugin README (Items 1.1–1.6, 2.11)

**Scope**: `git diff 888eda7a..HEAD` over `plugin/bin/triage-feedback.sh`,
`plugin/skills/build/scripts/{changed-files,exempt-paths,verify-step}.sh`,
`plugin/README.md`, and the test modules and helpers the dispatch lists.
**Date**: 2026-10-06
**Mode**: review + fix

## Summary

The changes implement KD-1 (triage measures the review gate's list), KD-2
(idempotent log append), N-1, m1/m4/m5/m6/m8 and the test-hygiene items
closely to the outline. Tests are strong: each pins a named wrong
implementation, including decoys for the report regex, the `:(glob)` scope,
literal pathspecs, the SIGPIPE status and the unterminated log row. I read the
three surfaces of the changed-files contract against each other (the scripts,
the tests, and README plus D-90 and `finishing.md` as the consumers). That
turned up one major seam issue I could not fix: re-invoking a finished job
logs a second row, because the closing commit puts the triage log and
`tdd-audit.md` into the next measurement. It needs a design call. I fixed four
minor issues.

**Overall Assessment**: Needs Significant Changes. One major issue is
UNFIXABLE (U-DESIGN) and needs my human partner's call. Everything else is
fixed.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **A re-invoked finished job logs a second triage row with different
   evidence. KD-2 does not hold across the closing commit.**
   - Location: `plugin/bin/triage-feedback.sh` (list and reports
     measurement), together with `changed-files.sh`'s list definition (D-90)
     and `finishing.md` §§1–3.
   - Problem: KD-4 skips a landed §1 and §3 but not §2, so a re-invoked
     finished job runs triage again. By then the `<job> Finish` closing commit
     has committed `plans/reports/triage-feedback-log.md` and, on a TDD run,
     `plans/<job>/reports/tdd-audit.md`:
     - the log sits outside `plans/<job>/`, so `changed-files.sh` lists it and
       Files changed goes up by 1;
     - `tdd-audit.md` is not in D-90's exclusion list (`final-review.md` is),
       so Reports goes up by 1.

     The evidence differs from the first row, so KD-2's duplicate check passes
     and a second row is appended. m7 named exactly this scenario ("a
     re-invocation … logs a duplicate row"). Probed against the committed
     scripts in a scratch repo: a Complex run logged
     `| j | Complex | 1 | 0 | no | overclassified |`, and after a Finish
     commit carrying the log and `tdd-audit.md`, the re-run logged
     `| j | Complex | 2 | 1 | no | match |`. The verdict flipped as well as
     the row repeating. The KD-2 test re-runs without committing the log, so
     it cannot see this.
   - Suggestion: several valid paths, each with consequences outside this
     group's files:
     - (a) give `finishing.md` §2 a KD-4-style landed check, for example a
       commit after `<L>` touching the triage log (review-skill's file);
     - (b) drop `plans/reports/` from D-90's list, and add `tdd-audit.md` to
       the report exclusions next to `final-review.md`. This changes D-90 in
       `docs/` (review-design's) and the outline's enumerated exclusions;
     - (c) have triage drop its own log path, which comes close to the
       "second copy of D-90's filters" that KD-1 rejects.
   - **Status**: UNFIXABLE (U-DESIGN)
   - **Investigation:**
     1. Scope OUT: the defect shows in IN files (triage's measurement). Each
        coherent fix touches OUT files: `finishing.md` (review-skill), or
        D-90 in `docs/references/build-run-state.md` (review-design).
     2. Design deferral: not deferred. KD-2 and KD-4 do not address §2 on
        re-invocation. D-90 and KD-1 enumerate the report exclusions
        (`review.md`, `review-*.md`, `final-review.md`) and leave out
        `tdd-audit.md`, so a script-only change contradicts the documented
        list.
     3. Codebase patterns: KD-4's landed check
        (`git log -1 <L>..HEAD -- <report path>`) is the closest pattern. It
        fits option (a), but the triage log is shared across jobs and lives in
        `finishing.md`, outside this group.
     4. Conclusion: three valid approaches with different downstream effects
        on D-90, the review gate's list and `finishing.md`. This needs my
        human partner's call.

### Minor Issues

1. **An inherited `EXEMPT_PATHS_ALTERNATION` defeats both load guards, and
   `verify-step.sh` then fails open to `CLEAN:`.** (Known open observation 2:
   judged in scope as part of m23's guard.)
   - Location: `plugin/skills/build/scripts/changed-files.sh:66-71`,
     `plugin/skills/build/scripts/verify-step.sh:157-163`.
   - Problem: the guard checks `${EXEMPT_PATHS_ALTERNATION:-}` after
     `source`. When `exempt-paths.sh` defines nothing, an inherited value
     passes the check. Measured with `EXEMPT_PATHS_ALTERNATION=.*`:
     - `verify-step.sh` read an untracked file as exempt, ran `just` and
       printed `CLEAN: tree clean, just precommit passed`;
     - `changed-files.sh` exited 0 with `BASE:` alone.
   - Fix: `unset EXEMPT_PATHS_ALTERNATION` before the `source` in both
     scripts, with a comment. Both guard tests gained a
     `defines-nothing-inherited` case, set through `monkeypatch.setenv`. Both
     red on the unfixed scripts (exit 0) and pass now.
   - **Status**: FIXED

2. **A log write failure exits 1, the usage error's code.**
   - Location: `plugin/bin/triage-feedback.sh`, log block (`mkdir -p`, header
     write, row append).
   - Problem: the outline's interface reserves exit 1 for usage, and
     `finishing.md` §2 reads exit 1 as "a usage error". Under `set -e`, a
     failed redirection exits 1. The change guards the unreadable-log case
     with exit 2 but leaves the more common unwritable case (read-only
     `plans/reports/`, read-only log) at exit 1, with bash's message on stderr
     only.
   - Fix: each write is followed by
     `|| { echo "ERROR: cannot write $log_file"; exit 2; }`. The two header
     `echo`s became one `printf`, so the guard applies to a simple command
     (bash skips `!`/status handling on a failed compound redirection, as the
     existing comment notes). New test
     `test_unwritable_log_is_an_error_not_a_usage_exit[header|row]` reds on
     the unfixed script (exit 1, no `ERROR:`) and passes now.
   - **Status**: FIXED

3. **README misstates the report count.**
   - Location: `plugin/README.md`, `changed-files.sh` bullet.
   - Problem: it says the count covers "the reports the `<base> HEAD` range
     adds under `plans/<job>/reports/`". It leaves out D-90's exclusions (the
     per-item `item-<N>-<M>.md` and the review reports) and "directly under".
     A reader would expect every item report to count, which is exactly C1's
     defect.
   - Fix: the sentence now says "directly under" and names both exclusions,
     in D-90's terms.
   - **Status**: FIXED

4. **The `test_line_limits_wc_padding.py` docstring that Item 1.6 edited
   still states a false present-tense claim.**
   - Location: `tests/test_line_limits_wc_padding.py:3-14`.
   - Problem: the rewritten sentence still says
     `check_line_limits.sh:124` "feeds `wc -l`'s output … with no `tr -d ' '`
     guard", and that the test "is red on unchanged code … expected to stay
     red". The guard has landed (`check_line_limits.sh:143`,
     `wc -l <"$file" | tr -d ' '`) and the test passes. The contrast with
     triage that Item 1.6 corrected therefore compared against a false
     baseline.
   - Fix: past tense ("fed … ; the fix added the same guard"), the stale line
     number replaced by the call shape, and the stale RED-phase sentence
     dropped. The triage sites stay as Item 1.6 wrote them.
   - **Status**: FIXED

5. **`finishing.md` §2 proceeds silently on `no-classification`, so N-1's
   `unrecognised classification:` line never reaches my human partner.**
   - Location: `plugin/skills/build/references/finishing.md:122-127`
     (consumer of triage's output).
   - Problem: N-1 prints the unrecognised label so the bad label gets seen.
     §2 says "On match or no-classification with no warning → proceed
     silently", so the line is dropped at the consumer.
   - **Status**: OUT-OF-SCOPE. `/build` prose belongs to the review-skill
     group; noted here for routing.

### Known open observations — decisions

- **Item 1.3's fixture vs the `quotepath=off` and no-`-r` mutants**: no
  finding. Item 1.3's requirement is that both of the review's mutants red,
  and both do. The outline pins the fixture, so adding `back\slash.txt` is
  the design question already recorded, not a defect against the spec. Left
  unchanged.
- **Load guards and an inherited `EXEMPT_PATHS_ALTERNATION`**: judged in
  scope and fixed (Minor 1). It is not hypothetical in effect: `verify-step.sh`
  failed open to `CLEAN:` on a dirty tree.
- **`verify-step.sh` keeps `exec 2>&1`**: no finding. m1 targeted
  `changed-files.sh` because its stdout is parsed data (`BASE:` plus paths)
  that git's stderr corrupted. `verify-step.sh`'s output is a single
  diagnostic stream the agent reads whole, including `just precommit`'s
  stderr after `PRECOMMIT:`. Keeping stderr on stdout there is deliberate and
  correct.

## Fixes Applied

- `plugin/skills/build/scripts/changed-files.sh:58-68` — `unset
  EXEMPT_PATHS_ALTERNATION` before sourcing, with an extended comment.
- `plugin/skills/build/scripts/verify-step.sh:157-161` — the same.
- `plugin/bin/triage-feedback.sh` log block — `mkdir -p`, header `printf` and
  row append each exit 2 with `ERROR: cannot write <log>` on failure; one
  comment line on why.
- `plugin/README.md` `changed-files.sh` bullet — the report count says
  "directly under" and names D-90's exclusions.
- `tests/test_changed_files.py`, `tests/test_verify_step.py` — the guard
  tests are parametrized on `(exempt_paths, inherited)` with a
  `defines-nothing-inherited` case. The environment is cleared or set through
  `monkeypatch`, and the docstrings name the wrong implementation it reds.
- `tests/test_triage_feedback_log.py` — new
  `test_unwritable_log_is_an_error_not_a_usage_exit` (`header`, `row`).
- `tests/test_line_limits_wc_padding.py` — docstring made accurate (Minor 4).

Verification:

- The four new test cases redded on the pre-fix scripts on their assertions:
  exit 0 or 1 where 2 was expected, and no `ERROR:` line.
- The targeted modules give 48/48 passed after the fixes.
- `shellcheck` is clean on all four scripts.
- `just precommit`: version consistency, 407/408 passed with 1 xfail, line
  limits (only the three `plugin/agents/*corrector.md` files, unrelated to
  this change), design links. It ended "Precommit OK".

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| C1 (Simple runs no longer always underclassified) | Satisfied | Reports exclude `item-<N>-<M>.md` and the review reports (`triage-feedback.sh:56-72`); `test_reports_exclude_the_per_item_report` |
| M1 (evidence is the review gate's list) | Satisfied | Runs `changed-files.sh`, counts its list, diffs only `:(literal)` list paths (`:22-40`, `:92-133`); `test_files_changed_is_the_review_gates_list`, `test_behavioral_code_reads_the_lists_paths_only` |
| M6 (NUL read pinned) | Satisfied | `test_paths_with_space_and_non_ascii_bytes_are_listed_whole` |
| m1 (`exec 2>&1` dropped from `changed-files.sh`) | Satisfied | Header comment updated to match |
| m4 (`--` before pathspecs) | Satisfied | Every triage git call; `head-file` case |
| m5 (no here-string; grep 1 vs ≥2) | Satisfied | `PIPESTATUS[1]` form, `:122-132`; `test_early_match_in_a_large_diff_is_not_an_error` |
| m6 (no `xargs`, no `\|\| true`) | Satisfied | `sed` prefix strip and trim; apostrophe and colon cases |
| m7 / KD-2 (one row per evidence) | Partial | Holds for re-runs before the closing commit. Fails for a re-invoked finished job (Major 1, UNFIXABLE U-DESIGN) |
| m8 (durable D-IDs in script comments) | Satisfied | No `KD-` left in the four scripts |
| m20, m21, m22 | Satisfied | Docstrings state the split reasons and D-91's exemption; `test_git_failure_is_error_not_no_base` split out |
| m23 (load guard tested) | Satisfied | Both guard tests, now including the inherited-value case |
| N-1 | Satisfied in the script | `test_unrecognised_label_is_no_classification`. The consumer drops the line (Minor 5, OUT-OF-SCOPE) |
| KD-1 failure exits | Satisfied | NO-BASE and ERROR → exit 2 with no row; git and grep failure tests. Log write failure now exit 2 too (Minor 2) |
| KD-6 / m13 README call sites | Satisfied | README lists the refactor and list-revision commits, matching `SKILL.md` §4.4 |
| m9 README | Satisfied | `sandbox-lies` named optional, with its consequence |

**Gaps:** KD-2 across the closing commit (Major 1).

---

## Positive Observations

- Every new test docstring names the wrong implementation it reds, and the
  fixtures carry decoys for each one: `item-1-12.md` against a single-digit
  regex, `explore/notes.md` against a glob-less pathspec, a revised planning
  report against a touched-path count, `*.md` against non-literal pathspecs,
  and an unterminated last row.
- Shell failure handling is consistent: `PIPESTATUS[1]` to survive SIGPIPE
  under `pipefail`, braces around the `while … < log` so the `!` applies
  (verified on bash 5.2), and no `|| true` or `2>/dev/null` anywhere.
- Bash 3.2 safety holds: no `mapfile`; the pathspec array is only expanded
  when non-empty, which avoids bash < 4.4's `set -u` empty-array error; the
  regexes are held in variables.
- The split modules (`_behavioral`, `_log`, helpers) keep each file well under
  400 lines along clear seams.

## Recommendations

- Settle Major 1 together with the review-skill group's `finishing.md` §2
  (Minor 5 lands in the same paragraph). If option (a) is chosen, that one
  paragraph's edit takes the §2 landed check and the surfacing of the
  `unrecognised classification:` line together.
