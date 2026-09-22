# 2026-09-01 — One-stage runbook replaces the two-stage expansion pipeline

The expanded-runbook stage — outline → phase files → assembled runbook → step
files and an orchestrator manifest — existed so a weak (haiku) orchestrator
could dispatch pre-written sub-agent prompts. The user's diagnosis from
operating the pre-teardown pipeline was that a strong orchestrator does not need
them and that pre-written prompts turn harmful the moment implementation
deviates; the revived two-stage pipeline had also never been run end to end
(`plans/pipeline-simplification/requirements.md`, C-1).

`/runbook` now writes `plans/<job>/runbook.md` as the terminal planning
artifact: typed phases of prose items with requirement IDs, `Interfaces:` blocks
where one item feeds another, and behaviour slices on tdd items.
`runbook-corrector` (the renamed outline corrector) and `runbook-simplifier`
gate it, `/proof` validates it, and `/orchestrate` composes every dispatch
prompt from it live. TDD runs four dispatches per slice — RED, test review,
GREEN, code review — with `refactor` on review signal and a list-revision step
after each slice; `test-driver` owns RED and GREEN as two named modes.

Deleted in one pass: `prepare-runbook.py`, `validate-runbook.py` and its tests,
`assemble-runbook.py`, `split-execution-plan.py`, `verify-red.sh`,
`/review-plan`, the old `runbook-corrector`, `plugin/docs/`, and the tier-3
runbook references — 7,029 lines / 97,724 tokens measured before deletion
(`plans/pipeline-simplification/reports/measurements.md`). Deterministic runbook
validation does not survive (D-51). FR-19, FR-20 and L-1 closed; D-31
superseded; D-24 to D-26, D-30, D-32 to D-35, D-39, D-49, D-69, L-2 and L-6
rewired; §7 records the rejected two-stage model, per-test dispatch and RED-less
whole-task batching.

The planning/execution session boundary lost one of its two grounds. It was kept
on model-tier and context-budget grounds in 2026-08-13; orchestration no longer
runs a tier below planning, so D-25 now rests on context budget alone.
