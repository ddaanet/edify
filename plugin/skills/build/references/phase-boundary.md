# Phase Boundary

Reached at the end of each phase of a **phased runbook**. Work with no runbook
has no phases and never reaches this file; its whole diff is covered by the
review gate in `finishing.md` instead.

The changed-files list is the phase's committed diff against its base. It is
taken against `HEAD`, not the working tree, so the paths `verify-step.sh`
exempts stay out:

```bash
git diff --name-only <phase base> HEAD
```

For phase 1 the base is the commit in `tmp/build-baseline`. For phase P>1 it is
the commit that adds the previous phase's corrector report, which the commit
closing that phase always lands:

```bash
git log --diff-filter=A --format=%H \
    -- plans/<job>/reports/phase-<P-1>-corrector.md
```

Read `references/dispatch-composition.md` and compose by it a dispatch of
`edify:corrector` scoped to the phase's items: scope IN/OUT and the Requirements
summary from the phase's items, design and recall artifact by path, the changed
files as an explicit list, a Constraints section barring findings outside scope
OUT, and the report path from that reference's §Prompt contents rule under the
dispatch name `phase-P-corrector`. Before delegating, STOP on any field
`../../fragments/review-requirement.md` §Execution Context requires that is
empty or missing: scope IN, scope OUT, changed files, Requirements summary and
the Constraints section. UNFIXABLE → STOP and escalate. When my human partner's
decision is a fix with no design impact, apply it — inline or by a fresh
executor dispatch — then resume `phase-P-corrector` by `SendMessage` with the
decision and the changed files, so the reviewer that raised it reviews the fix
inside its own scope; neither the orchestrator's own judgement nor the next
phase's reviewer stands in for that review. Otherwise commit and continue: the
corrector commits nothing, so that commit carries its report — with the fixes it
applied where there are any — and always happens. Stage those paths by name and
commit with `git commit -- <paths>`. Then run `/build` §4.4's verification.

The **last phase's boundary** adds a lifecycle audit: verify all stateful
objects (MERGE_HEAD, staged content, lock files) cleared on success paths.
