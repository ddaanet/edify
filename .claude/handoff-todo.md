## Remaining

- Task 8: fix `design-corrector.md:56` markers; resolve `review/SKILL.md:178` `common-scenarios.md` reference; scoped `manifest` grep; `just precommit`; after-measurement (`wc -l` + `edify tokens` over the surviving rewrite set plus the new `runbook-format.md` and `dispatch-composition.md`) appended under `## After` in `plans/pipeline-simplification/reports/measurements.md`; commit.
- Task 9 = `/inline` Phase 4a: `git diff --name-only a4aad0c8`, group by artifact type, dispatch per `plugin/fragments/review-requirement.md` routing table using `plugin/skills/inline/references/review-dispatch-template.md` (reports `plans/pipeline-simplification/reports/review-<type>.md`), Read each report, grep UNFIXABLE; Phase 4b `plugin/bin/triage-feedback.sh plans/pipeline-simplification a4aad0c8`; Phase 4c name `/deliverable-review plans/pipeline-simplification` as the follow-up; §Continuation per `plugin/fragments/continuation-passing.md`.
- Re-apply the parked memory edit from `tmp/memory-parked/` and clear the gitlore approval gate (summary blockquote → user approval → `.claude/gitlore-memory-message` → commit).
- Dogfood the pipeline end-to-end after pipeline-simplification lands.
- Consolidate `memory/MEMORY.md` (31.4KB vs 24.4KB loader cutoff) via `/gitlore:index-audit` — retire, don't shorten.
- FR-12 remainder: defect 21 (corrector skeleton, deletion not extraction) and per-class skill-body length targets (no calibration data).
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle; its FR-9/FR-12/NFR cross-refs were updated in `0bf8cc44`.