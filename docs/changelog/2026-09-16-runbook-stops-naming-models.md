# 2026-09-16 — The runbook stops naming models

`Model:` is gone from the runbook item format. Two dispatches are now fixed and
unoverridable — `test-driver` at sonnet in both RED and GREEN, prose
deliverables at opus — and D-42's artifact-type override is stated by artifact
kind instead of by a list of edify's own paths.

The defect that surfaced it was precedence, not defaults. `delegation.md`
already had the right type defaults; what defeated them was the third rule on
the same list, that a `Model:` line wins. A live run over a consumer
repository's runbook had `Model: opus` on all three tdd items — copied from the
worked example in `runbook-format.md` — so every test-driver dispatch was headed
for opus. The same run dispatched a changelog entry under the consumer's `docs/`
at sonnet, because D-42's path list named only edify's directories and nothing
matched.

Demoting `Model:` below the new rules would have left the field that taught the
habit. It is removed instead: a planner cannot know the agent type or the real
shape of the work, so a model named at plan time is a guess. Escalation on
demand replaces it — the agent returns `escalated:`, the dispatcher
re-dispatches higher, which is what D-30 already did for `edify:refactor`. The
rule had been carried as a stopgap sentence in the shared `ddaanet` conventions
since 2026-09-07; that sentence is deleted here, now that the tooling states it.
