## Current task

`/build plans/design-routing-and-provenance` is **complete** — both items executed, all three review groups dispatched and their findings applied, triage verdict `match`, tree clean. The job's remaining step is its named follow-up: `/deliverable-review plans/design-routing-and-provenance`, opus, in a fresh session.

The review range that command needs is `926e372d02a0366202b2bb6a684551128d1f2a66..HEAD`, read from the outline's own `## Provenance` section — that outline is the first artefact written under the provenance contract this job introduced, so the follow-up is also the contract's first dogfooding. The design artefact is `plans/design-routing-and-provenance/outline.md` (no `design.md`); `deliverable-review` now takes whichever exists.

Three reviewer reports sit in `plans/design-routing-and-provenance/reports/` — `review-skills.md`, `review-agents.md`, `review-docs.md`. They are inputs to the deliverable review, not substitutes for it: each saw one artifact group against the baseline, none saw the whole diff.

This run was also the first exercise of the merged `/build` skill, so anything awkward in its lifecycle is a finding about the skill, not just about this job.

### Operational note

`plugin/skills/build/scripts/verify-step.sh` and `just precommit` must run with `dangerouslyDisableSandbox: true`. Sandboxed, `git status` invents untracked `.claude/` phantoms and the gate returns a false `DIRTY`.