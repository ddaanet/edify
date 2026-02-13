# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| continuation-prepend | requirements | Problem statement only |
| feature-requests | requirements | GH issue research (sandbox, tool overrides) |
| handoff-validation | requirements | Requires continuation-passing |
| orchestrate-evolution | designed | Design.md complete, vet in progress, planning next |
| parallel-orchestration | requirements | Deferred from orchestrate-evolution (worktree isolation needed) |
| plugin-migration | planned | Runbook assembled: 15 steps, haiku execution ready |
| reflect-rca-sequential-task-launch | requirements | RCA on Task parallelization + vet context issues |
| reports | — | Shared reports directory (not a plan) |
| requirements-skill | requirements | Evaluate with opus |
| tweakcc | requirements | Local instances research |
| when-recall | designed | `/when` memory recall system — design.md vetted, TDD runbook next |
| workflow-fixes | complete | Unified /runbook skill, plan-reviewer agent, review-plan skill, pipeline-contracts |
| worktree-update | planned | Recovery runbook ready (6 steps: C2, C3, M1, M2, C4, C5), orchestration next |
| workflow-skills-audit | designed | plan-adhoc alignment + design skill audit, 12 items |
| worktree-skill | complete | 42/42 cycles, all phases, pending merge to dev |
| worktree-skill-fixes | complete | 27 findings fixed (7 phases), T5 bug fix |

## Complete (Archived)

*41 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --online -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `continuation-passing` — Continuation passing protocol (15 steps, hook implementation, skill updates, 0% FP rate)
- `markdown` — Test corpus implementation (16 fixtures, 3 parametrized tests, all 5 FRs satisfied)
- `memory-index-recall` — Memory index recall analysis tool (7 modules, 50 tests)
- `reflect-rca-parity-iterations` — Parity test quality gap fixes (11 steps, 8 design decisions)
- `domain-validation` — Domain-specific validation infrastructure (validation skill, rules file, plan skill updates)
- `validator-consolidation` — Validators consolidated to claudeutils package
- `commit-unification` — Unified commit skills, inlined gitmoji, decoupled handoff
- `position-bias` — Fragment reordering by position bias + token budget script
- `prompt-composer` — Superseded by fragment system; research distilled
- `reflect-rca-prose-gates` — D+B hybrid fix implemented
- `statusline-wiring` — Statusline CLI with TDD (28 cycles, 6 phases)
- `statusline-parity` — All 14 cycles, 5 phases executed and validated
- `learnings-consolidation` — Learnings consolidation infrastructure (7 steps, 4 phases)
- `workflow-feedback-loops` — Feedback loop infrastructure (12 steps, 4 phases)
- `claude-tools-rewrite` — Infrastructure complete, recovery and parity followups
- `claude-tools-recovery` — Account/provider/model CLI wired
- `runbook-identifiers` — Cycle numbering gaps relaxed
- `robust-waddling-bunny` — Memory index D-3 RCA
- `review-requirements-consistency` — Requirements review
- `majestic-herding-rain` — Gitmoji integration
- `handoff-lite-issue` — RCA transcript for handoff-lite misuse
