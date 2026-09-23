# Phase Boundary

Reached at the end of each phase of a **phased runbook**. Work with no runbook
has no phases and never reaches this file; its whole diff is covered by the
review gate in `finishing.md` instead.

```bash
plugin/skills/build/scripts/verify-step.sh
git diff --name-only
```

Run `verify-step.sh` with `dangerouslyDisableSandbox: true`.

Read `references/dispatch-composition.md` and compose by it a checkpoint-form
dispatch of `edify:corrector`: scope IN/OUT from the phase's items, design and
recall artifact by path, changed-files list, report path from that reference's
§Prompt contents rule under the dispatch name `phase-P-corrector`. IN/OUT lists
must be non-empty and the changed-files list present — empty fields → STOP
before delegating. UNFIXABLE → STOP and escalate. When my human partner's
decision is a fix with no design impact, apply it — inline or by a fresh
executor dispatch — then resume `phase-P-corrector` by `SendMessage` with the
decision and the changed files, so the reviewer that raised it reviews the fix
inside its own scope; neither the orchestrator's own judgement nor the next
phase's reviewer stands in for that review. Otherwise commit and continue: the
corrector commits nothing, so that commit carries its report — with the fixes it
applied where there are any — and always happens.

The **final checkpoint** adds a lifecycle audit: verify all stateful objects
(MERGE_HEAD, staged content, lock files) cleared on success paths.
