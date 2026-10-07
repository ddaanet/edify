# Review: gate-fix-narrow — D-90 drops the triage log by name

**Scope**: the amendment answering `gate-fix-code-review.md` Major 1 with my
human partner's option (i), and nothing else in the tree:

- `changed-files.sh`: the read loop's `case` arm and the header's D-90
  paragraph.
- `tests/test_changed_files.py`: test A (`test_triage_log_is_dropped_by_name`),
  its fixture and docstring, and the module docstring's D-90 sentence.
- Prose:
  - D-90 body and the new Rejected entry in `docs/references/build-run-state.md`;
  - the *Rejected:* line in `docs/decisions.md`;
  - the list descriptions in `finishing.md` §1 step 1, `phase-boundary.md`,
    `review-requirement.md` and `plugin/README.md`;
  - the changelog's second paragraph;
  - the outline's KD-1 Reports bullet.

**Date**: 2026-10-07
**Mode**: review + fix

## Summary

The case arm is `"$exclude_prefix"* | plans/reports/triage-feedback-log.md)`.
A `case` pattern matches the whole string, so a glob-free alternative is
anchored at both ends. It uses no bash-4 feature, so it is portable to bash 3.2
on macOS. Test A put a near-miss on every boundary of that path. Six in-place
mutations of the arm each turned the test red.

All the surfaces state the same rule: the script, D-90, its *Rejected:* line and
Rejected entry, the four list descriptions, the changelog and the outline. The
list drops the job's `plans/<job>/`, the triage log by name, and the exempt
paths. The rest of `plans/reports/` stays on the list.

I found three minor issues and fixed all of them: an incomplete account in the
test docstring, one inaccurate sentence in the script comment, and two ragged
wraps.

**Overall Assessment**: Ready.

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Test A's docstring misattributed what some wrong implementations drop**
   - Location: `tests/test_changed_files.py`, test A docstring.
   - Note:
     - It said a drop of all of `plans/reports/` "drops the two deliverables
       and `.orig`". That drop also removes
       `plans/reports/sub/triage-feedback-log.md`, as the RED run's actual
       output shows.
     - It credited "unanchored or by suffix" with dropping both the `docs/`
       copy and the `sub/` copy. A full-path suffix match
       (`*plans/reports/triage-feedback-log.md`) drops only the `docs/` copy,
       and a name match under `plans/reports/` drops only the `sub/` copy. The
       mutation runs below confirm both.
     - It listed `plans/other/reports/item-1-1.md` as a "near-miss of the exact
       path", which it is not. It is the near-miss for a drop of every job's
       record.
   - **Status**: FIXED. The docstring now names each guard's own wrong
     implementation: all of `plans/reports/`, a prefix match, a suffix match, a
     name match under `plans/reports/`, and every job's record or all of
     `plans/`. Each matches a mutation in the table below.
2. **The script comment said the closing commit "does not enter" the re-run's
   list**
   - Location: `plugin/skills/build/scripts/changed-files.sh`, the header's
     D-90 paragraph.
   - Note: the drop removes one path. The closing commit's other changes still
     enter the list, including `final-review`'s fixes outside `plans/<job>/`.
     The sentence claimed more than the code does.
   - **Status**: FIXED. It now reads: "a finished job's closing commit lands
     it, and a re-invocation would otherwise list it". The paragraph tail,
     which had a short "(D-91). Paths come from a NUL-delimited" line, is
     reflowed. No other words changed.
3. **Ragged wrap in the outline's KD-1 Reports bullet**
   - Location: `plans/review-fixes-2/outline.md:43-44`.
   - Note: a short line, "`plans/reports/triage-feedback-log.md`, so a
     re-invoked", was left by the edit.
   - **Status**: FIXED. Reflowed, with the words unchanged.

## Checks requested by the dispatch

- **Anchoring and portability.** `case` matches the whole word, and the pattern
  `plans/reports/triage-feedback-log.md` holds no `*`, `?` or `[`, so it is an
  exact literal. Neither `.` nor `-` is special in a pattern. Alternation with
  `|` inside `case` is POSIX, so it is safe in bash 3.2. `shellcheck` reports
  only the existing SC1091 info, on the `source` line, which is outside this
  delta.
- **Edge case: a job named `reports`.** `exclude_prefix` becomes
  `plans/reports/`, which is that job's own record, so the whole directory is
  dropped for it alone. This is consistent with D-90's `plans/<job>/` drop, and
  it is not a finding.
- **Comment against code.** After fix 2, the header matches the arm. It states
  the triage log by name, gives the reason, says the rest of `plans/reports/`
  stays, and says the drop lives here, not in `exempt-paths.sh` (D-91).
  `exempt-paths.sh` is untouched.
- **The closing commit lands no other `plans/reports/` path.** `finishing.md`
  §3 step 3 lists the commit's contents: the triage log line,
  `final-review.md` with its fixes, and `tdd-audit.md`. Both reports are under
  `plans/<job>/reports/`, so the "only the triage log" claim in D-90 and in the
  test docstring holds.
- **Test C** (`test_rerun_after_the_closing_commit_appends_no_row`) commits the
  log at the exact path `plans/reports/triage-feedback-log.md`, so the narrowed
  drop still removes it, and the test passes. Its docstring names that exact
  path, so it needs no change.
- **Cross-surface grep.** I searched `plugin/`, `docs/`, `plans/review-fixes-2/`
  (excluding `reports/`) and `tests/` for `plans/reports`, "pipeline's record",
  "triage log" and `reports/*`. Nothing remaining claims that the list drops all
  of `plans/reports/`. The only mention of that rule is the new Rejected entry,
  in the node and in `decisions.md`, which gives it as rejected.
- **The four list descriptions agree word for word in their key clause.** Each
  of `finishing.md:37-40`, `phase-boundary.md:15-18`,
  `review-requirement.md:134-137` and `README.md:84-87` says "the pipeline's
  record: the job's own `plans/<job>/` and the triage log,
  `plans/reports/triage-feedback-log.md`".
- **D-90 and its records.**
  - The node body drops the triage log by name and gives the reason: an
    Investigation's deliverable goes to `plans/reports/`, and D-82 routes
    Investigation to `/build`. The earlier stated-bound sentence is gone.
  - The new Rejected entry ("The list dropping all of `plans/reports/`") holds
    the same position in the node and in the `decisions.md` *Rejected:* line:
    after "triage dropping its own log path from the list" and before
    "filtering or gitignoring the sandbox-mask names".
  - `just design-links` reports that the conclusions match.
  - The edits follow `craft:design-doc-writing`. The rejected alternative is
    recorded with its reason. The body is in the present tense and carries no
    status narration or mutable figure.

## Mutated-SUT run

Each mutation was an exact string replacement of the `case` arm, asserted to
occur once. I then ran `just test tests/test_changed_files.py -k
triage_log_is_dropped` and applied the inverse replacement. After each restore
the file's sha256 matched the original
(`35909c42…cd8a5b`).

| Mutation (arm alternative) | Wrong implementation | Path that leaked or dropped | Test A |
|---|---|---|---|
| `*plans/reports/triage-feedback-log.md` | unanchored, full-path suffix (dispatch's first) | `docs/plans/reports/triage-feedback-log.md` dropped | red |
| `plans/*` | drop all of `plans/` (dispatch's second) | `plans/other/…`, deliverables and every near-miss under `plans/` dropped | red |
| `plans/*/reports/*` added beside the arm | drop every job's record | only `plans/other/reports/item-1-1.md` dropped | red |
| `plans/reports/*triage-feedback-log.md` | name match under `plans/reports/` | `plans/reports/sub/triage-feedback-log.md` dropped | red |
| `plans/reports/triage-feedback-log.md*` | prefix match | `.orig` dropped | red |
| arm removed (`"$exclude_prefix"*)` alone) | no drop | the triage log listed | red |

The dispatch's `plans/*` mutation also drops the deliverables, so its red does
not isolate the `plans/other/` guard. The `plans/*/reports/*` row does isolate
it: the only listed path that mutation drops is `plans/other/reports/item-1-1.md`.
Every listed near-miss therefore reds a wrong implementation on its own.

Restore proof: `grep -nF` finds the arm
`"$exclude_prefix"* | plans/reports/triage-feedback-log.md) continue ;;` at
`changed-files.sh:125`. `tests/test_changed_files.py` and
`tests/test_triage_feedback_log.py` passed 17/17 after the fixes, and the full
suite passed in `just precommit` (below).

## Fixes Applied

- `tests/test_changed_files.py`, test A docstring: each near-miss is now
  attributed to the wrong implementation it catches (minor 1).
- `plugin/skills/build/scripts/changed-files.sh`, header's D-90 paragraph: the
  rationale sentence is corrected and the paragraph tail reflowed (minor 2).
- `plans/review-fixes-2/outline.md`, KD-1 Reports bullet: reflowed (minor 3).

The gate ran in the foreground, with full output:

- `just precommit` exited 0 and printed `Precommit OK`.
- Version consistency: 0.3.0.
- Tests: 410/411 passed, 1 xfail.
- Line limits: three oversized-file warnings, all for corrector agent files
  outside this delta: `corrector.md` 682, `outline-corrector.md` 450 and
  `design-corrector.md` 460.
- Design links: 94 decisions indexed, defined once, conclusions match, 9 nodes
  present.

Nothing was staged or committed.

## Requirements Validation

| Requirement | Status | Evidence |
|---|---|---|
| Ruling (i): the list drops the triage log by exact path only | Satisfied | `changed-files.sh:125`; test A, with all six mutations red |
| An Investigation deliverable under `plans/reports/` stays listed, reviewed and counted | Satisfied | test A lists `explore-x.md` and `sub/x.md`; D-90 body |
| m7/KD-2 holds across the closing commit | Satisfied | test C green; its fixture commits the log at the exact path |
| D-91 is not widened | Satisfied | `exempt-paths.sh` unchanged; the header says why |
| The surfaces agree | Satisfied | the script, D-90, its *Rejected:* line and Rejected entry, the four list descriptions, the changelog and the outline |

## Positive Observations

- The RED report recorded which near-misses could not red against the old
  script and asked for a mutation proof of each. Each listed path guards exactly
  one wrong implementation, and the table above shows each one alone.
- D-90 keeps a single rationale for the by-name drop. The changelog's clause
  ("by name, since an Investigation's deliverable also lands under
  `plans/reports/`") points at it rather than arguing it again.
