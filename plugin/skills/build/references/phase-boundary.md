# Phase Boundary

Reached at the end of each phase of a **phased runbook**. Work with no runbook
has no phases and never reaches this file; its whole diff is covered by the
review gate in `finishing.md` instead.

## Base and changed files

At every boundary, one call gives the phase base and the changed-files list:

```bash
plugin/skills/build/scripts/changed-files.sh <job> --phase
```

Exit 0 prints `BASE: <sha>`, the phase base, then one path per line: the
committed diff from that base to `HEAD`, minus the paths `verify-step.sh`
exempts and the pipeline's record: the job's own `plans/<job>/` and the triage
log, `plans/reports/triage-feedback-log.md`. The `HEAD` form keeps uncommitted
dirt out, but not the exempt paths a `/handoff` or memory-pointer commit lands
during the run; the script drops those by name, since they are not the run's
work. Exit 1 (`NO-BASE:`, no committed item report) or exit 2 (`ERROR:`) → STOP.
Never substitute an empty base or a working-tree diff:
`git diff --name-only HEAD` passes an empty-field check with the wrong list.

The phase base is the latest commit in the run touching a
`plans/<job>/reports/phase-*-corrector.md` report, or the run base when none
does: `--phase` reads boundaries from report history by the rule for when one
has landed. Phase P has landed when

```bash
git log -1 --no-show-signature --format=%H <run base>..HEAD \
    -- plans/<job>/reports/phase-<P>-corrector.md
```

prints a hash, `<run base>` being the `BASE:` that `changed-files.sh <job>`
prints without `--phase`. The key is the report's path, never the commit
subject: a boundary always commits its corrector report. The range excludes an
earlier run's commit, the query counts a report the run modified as well as one
it added, and `-1` takes the later of two commits of one report.

**At P>1, check the base before using it.** Run the landed query for phase P-1.
An empty result means phase P-1's boundary commit was skipped → STOP. `--phase`
cannot tell: with that commit missing it falls back to an earlier base, which
would widen this phase's review over phase P-1's work. A hash other than
`--phase`'s `BASE:` → STOP as well: a later commit touched another phase's
report, and the two disagree on the base.

## Review

Read `references/dispatch-composition.md` and compose by it a dispatch of
`edify:corrector` scoped to the phase's items: scope IN/OUT and the Requirements
summary from the phase's items, design and recall artifact by path, the changed
files as an explicit list, a Constraints section barring findings outside scope
OUT, and the report path from that reference's §Prompt contents rule under the
dispatch name `phase-P-corrector`. Before delegating, STOP on any field
`../../fragments/review-requirement.md` §Execution Context requires that is
empty or missing: scope IN, scope OUT, changed files, Requirements summary and
the Constraints section.

Read the report and check it for UNFIXABLE by that fragment's §UNFIXABLE
Detection Protocol. An UNFIXABLE that fails validation goes back to
`phase-P-corrector`, resumed by `SendMessage` with the protocol's
reclassification guidance. One that holds → STOP and escalate with the report
path. When my human partner's decision is a fix with no design impact, apply it
— inline or by a fresh executor dispatch — then resume `phase-P-corrector` by
`SendMessage` with the decision and the changed files, so the reviewer that
raised it reviews the fix inside its own scope; neither the orchestrator's own
judgement nor the next phase's reviewer stands in for that review.

## Commit

Commit once no validated UNFIXABLE stands: none was raised, or the resumed
corrector has reviewed the fix. The corrector commits nothing, so this commit
carries its report, with every fix still uncommitted — the corrector's own and
any applied for a decision — and always happens. Stage those paths by name and
commit with `git commit -- <paths>`, subject `<type>: <job> Phase P boundary`.
Then run `/build` §4.4's verification.

The **last phase's boundary** adds a lifecycle audit: verify all stateful
objects (MERGE_HEAD, staged content, lock files) cleared on success paths.
