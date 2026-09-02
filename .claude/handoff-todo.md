## Open decisions

- Slice commit convention for the fix: `<type>: Item N.M/k — <title>` with the type the executor's choice (fix, docs, perf, test, build, chore all legitimate), and `tdd-auditor` identifying slice commits from the GREEN report (transcript under the session's `subagents/` dir as fallback), matching at most the `Item N.M/k` marker — the user's direction of 2026-09-02; confirm before rewriting `tdd-auditor.md:57,72,88-91`, `test-driver.md:60-63`, `dispatch-composition.md:19-21`, D5/D14 in `outline.md`, `docs/design.md` §5.3/D-26.
- Who commits the per-slice code-review fixes (Critical 1): the orchestrator after (d), as it already does at phase boundaries, or a commit contract in `corrector.md`.
- Whether the pre-existing findings (Critical 3 continuation hook; Major 11–13 `Session.md`, `Task` tool, D-5/D-1 cross-refs) ride in this fix pass or become their own tracked task — D-58 says every finding resolves to a fix or a task.

## Remaining

- Deliver the fixes in `plans/pipeline-simplification/reports/deliverable-review.md` via opus agents grouped by artifact (orchestrate loop + dispatch-composition + verify-step; the five agents; fragments + `/inline` routing; `docs/design.md` + `plugin/README.md` + outline D5/D14), each agent writing its report under `plans/pipeline-simplification/reports/`; then `just precommit`.
- Delete the untracked `plugin/scripts/__pycache__/` (D10 residue).
- Dogfood the simplified pipeline end to end (`/design` → `/runbook` → `/orchestrate`) on a real plan; L-6 records it as unexercised, FR-5's slice-batching claims unvalidated until it supplies counts.
- Consolidate `memory/MEMORY.md` (32,4xx bytes vs the 24.4KB loader cutoff) via `/gitlore:index-audit` — retire, don't shorten; fix `docs/design.md` L-5's stale "~28.9 KB" in the same pass (Major 10 of the review).
- Pilfer defect 21 (corrector-skeleton dedup), carrying: unreachable "when reviewing runbooks/plans" criteria in `corrector.md` ~293–304; the corrector family's `Skill(edify:recall)` vs the flat-list Read in `delegation.md`/`dispatch-composition.md` (now Major 2 of the review).
- FR-12 remainder beyond defect 21: per-class skill-body length targets (no calibration data).
- `/design plans/pilfer-superpowers/` once Q-1 and Q-3 settle.
- Report-only reviewers (`plugin-dev:skill-reviewer`, no Write) get truncated at ~4,000 chars in the reply; give `plugin/skills/inline/references/review-dispatch-template.md` a chunked-return instruction or route skill definitions to a Write-capable reviewer.
