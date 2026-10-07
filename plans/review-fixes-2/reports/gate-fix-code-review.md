# Review: gate-fix-code-review — the D-90 re-invocation fix and Item 1.3's `back\slash.txt` amendment

**Scope**: this fix's hunks only, located with `git diff`. In
`changed-files.sh`: the `plans/reports/*` case arm and the D-90 header
paragraph. In `triage-feedback.sh`: `tdd-audit.md` in the Reports exclusion
and its D-90 comment. The three new or amended tests and the
`test_changed_files.py` module docstring. In `build-run-state.md`: D-90 and
the two new Rejected entries. In `decisions.md`: D-90's line and the
Build-run-state *Rejected:* line. The changelog sentence. The list
descriptions in `finishing.md` §1 step 1, `phase-boundary.md`,
`review-requirement.md` and `plugin/README.md`. The outline's KD-1 Reports
bullet and Item 1.3. The earlier review-gate hunks in the same files are OUT.
**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The fix implements my human partner's ruling (b). `changed-files.sh` drops
`plans/reports/*` beside `plans/<job>/`, in the same `case`. The drop is not
in `exempt-paths.sh`, so `verify-step.sh` still sees `plans/reports/` dirt
(D-91). Triage excludes `tdd-audit.md` from its Reports count. I read the
three surfaces of the contract against each other: the scripts, the tests,
and the consumers (D-90, `finishing.md`, `phase-boundary.md`,
`review-requirement.md`, README). Every site now states the same exclusions.

The seam that matters is this. `plans/reports/` is also the destination of
an Investigation's deliverable, and Investigation routes to `/build`. The
drop therefore removes such a deliverable from the review gate's list and
from triage. I stated that bound in D-90. Whether to narrow the drop is my
human partner's call, so that issue is UNFIXABLE (U-DESIGN). I fixed two
minor issues.

**Overall Assessment**: Needs Significant Changes. That rests on the one
U-DESIGN issue, Major 1, which needs a ruling. Everything else is Ready.

## Issues Found

### Critical Issues

None.

### Major Issues

1. **An Investigation run's deliverable under `plans/reports/` now escapes
   the review gate and triage**
   - Location: `plugin/skills/build/scripts/changed-files.sh:124` (the
     `plans/reports/*` arm), read against
     `plugin/skills/design/references/triage.md:51-52,66` and
     `docs/references/execution-routing.md:72` (D-82).
   - Problem: D-82 (and `route-to-execution.md:32`) sends Investigation and
     Exploration work to `/build`. `/design`'s artifact-destination table
     names `plans/reports/` as the Investigation destination.
     `delegation.md:50` says the same of research deliverables. Before this
     fix such a deliverable was on the list. Now it is dropped as pipeline
     record:
     - `finishing.md` §1 step 1 sees an empty list and takes the
       `review-skip.md` branch;
     - §3 step 1's final review skips an empty list too;
     - triage reads Files changed 0, so a Complex investigation logs
       `overclassified` on evidence that never saw its deliverable.

     The other writers under `plans/reports/` are no problem. Scout's ad-hoc
     `explore-*.md` and `/ground`'s grounding reports are research
     by-products or planning-time output, and the triage log is the record
     the fix targets. The dispatch's `plans/reports/` rationale ("pipeline
     record") holds for those writers but not for an Investigation's
     deliverable.
   - Suggestion: there are several valid paths, and each changes the ruling:
     - (i) narrow the drop to the triage log by name in `changed-files.sh`.
       Test A pins `explore-x.md` and `sub/x.md` as dropped, so A changes too.
     - (ii) keep the drop and move the Investigation destination to
       `plans/<job>/`, or treat it as the item's deliverable. That changes
       `/design`'s table and `delegation.md`, and `plans/<job>/` is dropped
       as well, so the deliverable stays unreviewed.
     - (iii) keep the drop and accept the bound, stated in the design
       record. I applied that statement.
   - **Status**: UNFIXABLE (U-DESIGN). I applied the stated bound, one
     sentence in D-90 (`docs/references/build-run-state.md`): "It is also
     where an Investigation's deliverable goes (`/design`'s
     artifact-destination table), and D-82 routes Investigation to `/build`,
     so a run whose deliverable lands there leaves it off the list: the
     review gate does not review it and triage does not count it." The
     behavioural choice among (i) to (iii) waits on my human partner.
   - **Investigation:**
     1. Scope OUT: not listed. The outline's OUT names M3, the two legacy
        log rows and the repo-relative invocation form.
     2. Design deferral: none. D-90 did not mention Investigation
        deliverables before this fix.
     3. Codebase patterns: `rg plans/reports` over `plugin/`, `docs/` and
        `tests/` finds the triage log, scout, `/ground`, `delegation.md`
        research deliverables and `/design`'s Investigation destination. No
        existing pattern separates deliverables from record under that
        directory. Option (i) contradicts the ruling's "every path under
        `plans/reports/`" and test A's pinned `explore-x.md` drop.
     4. Conclusion: narrowing or relocating is a ruling-level choice with
        downstream test and prose changes. Only the statement of the bound
        is in scope.

### Minor Issues

1. **Ragged reflow of the triage Reports comment**
   - Location: `plugin/bin/triage-feedback.sh:42-56`
   - Note: the inserted `tdd-audit.md`) left a short "`tdd-audit.md`).
     Slice," line, followed by lines wrapped at the old breaks.
   - **Status**: FIXED. I reflowed the paragraph to ~76 columns. The words
     are unchanged.
2. **Changelog asserted a re-run that only happened in a probe**
   - Location: `docs/changelog/2026-10-06-triage-measures-the-review-gates-set.md:20-23`
   - Note: "a finished job re-invoked ran triage again … and logged a second
     row" reads as an incident. The second row was found in review
     (`review-code.md` Major 1, a scratch-repo probe), and the same entry's
     earlier sentence already uses the conditional ("every Simple run would
     log").
   - **Status**: FIXED. It now reads "would run triage again … and log a
     second row".

## Checks requested by the dispatch

- **Exclusions agree at every site.** I grepped `plugin/`, `docs/` (minus
  older changelog entries) and `tests/` for "job's own", "own record",
  "final-review.md" and "plans/reports". Each site states the same list
  exclusions: `changed-files.sh` header, D-90, `finishing.md:37-40`,
  `phase-boundary.md:15-18`, `review-requirement.md:133-136`, README:84-87,
  and the `test_changed_files.py` docstring. Each site that states the count
  exclusions names `tdd-audit.md`: `triage-feedback.sh:45-46`, D-90,
  README:93-95 and outline KD-1. L-2 (`docs/design.md`) says "the review
  reports" generically, which still holds. `tdd-auditor.md:57` lists report
  inputs, not exclusions. `triage-feedback.sh:77` ("the job's own reports
  never count") stays true.
- **D-90 heading and line.** The `decisions.md` D-90 line matches the node
  heading word for word. `just design-links` reports "conclusions match".
  The two new Rejected entries appear in the same order in the node and in
  the *Rejected:* line.
- **`exempt-paths.sh` untouched.** `git diff` shows no change. The drop
  lives in `changed-files.sh`'s `case`, and its header says why (D-91).
- **Citations.** The fix's comments and docstrings cite D-88, D-89, D-90 and
  D-91. They cite no outline KD.
- **Portability.** A bash `case` alternation with `plans/reports/*` works in
  bash 3.2, and `*` crosses `/` in a `case` pattern, which test A's
  `sub/x.md` pins. No new external commands. `shellcheck` on both scripts
  reports only SC1091 (info), on the pre-existing `source` line.
- **Edge: a job named `reports`.** `exclude_prefix` becomes
  `plans/reports/`, which is the same drop. Harmless.

## Mutated-SUT run

Each mutation was an exact string replacement, asserted to occur once. I ran
the tests and then applied the inverse replacement. I compared the file's
sha256 before and after, and it was equal each time.

| Mutation | Tests run | Result |
|---|---|---|
| `changed-files.sh`: `"$exclude_prefix"* \| plans/reports/*)` → `"$exclude_prefix"*)` | A, C | both red |
| `changed-files.sh`: `\| plans/reports/*)` → `\| plans/reports*)` (no slash) | A | red |
| `triage-feedback.sh`: `final-review.md \| tdd-audit.md)` → `final-review.md)` | B, C | both red |

After restoring, all three modules passed (29/29). Every test redded. None
stayed green under its wrong implementation.

## Fixes Applied

- `plugin/bin/triage-feedback.sh:42-56`: reflowed the D-90 Reports comment.
- `docs/changelog/2026-10-06-triage-measures-the-review-gates-set.md`: the
  re-run sentence is now conditional.
- `docs/references/build-run-state.md` D-90: added a sentence stating that
  an Investigation deliverable under `plans/reports/` is off the list (Major
  1's stated bound).
- `just format` rewrapped both doc edits. `just precommit` is green with 410
  of 411 tests passing and 1 xfail. Line limits are within caps; the three
  oversized-file warnings are the pre-existing corrector agents. Design
  links report 94 decisions indexed, defined once, conclusions match, 9
  nodes present.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Ruling (b): the list drops every path under `plans/reports/` | Satisfied | `changed-files.sh:124`; test A, mutation-proven |
| Ruling (b): Reports excludes `tdd-audit.md` | Satisfied | `triage-feedback.sh:66`; test B, mutation-proven |
| m7/KD-2 holds across the closing commit | Satisfied | test C, red under either mutation alone |
| Item 1.3: `back\slash.txt` reds the `core.quotepath=off` and no-`-r` mutants | Satisfied | test D; the RED report's mutations 1–2 and the test review's fifth |
| D-91 is not widened | Satisfied | `exempt-paths.sh` unchanged |

**Gaps:** the review-gate coverage of Investigation deliverables (Major 1).

## Positive Observations

- The drop sits in the same `case` as `plans/<job>/`. The header comment
  says why it is not in `exempt-paths.sh`, which closes the D-91 widening
  the test review flagged as untestable by A.
- Test A puts a near-miss on each boundary of the prefix. Test C needs both
  halves of the fix to pass.
- D-90's body states the re-run rationale once. The changelog,
  `finishing.md`, README and the scripts point at it rather than re-arguing
  it.

## Recommendations

- My human partner: rule on Major 1, choosing among (i), (ii) and (iii).
  Under (i) or (ii), remove the stated-bound sentence from D-90.
- A final review's fixes land in the closing commit after triage ran, so a
  re-invocation measures them. The second row this can log reflects real
  new evidence, which KD-2 permits. It is noted here as a known
  difference, not a defect.
