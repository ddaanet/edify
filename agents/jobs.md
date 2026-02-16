# Jobs

Plan lifecycle tracking. Updated when plans change status.

**Status:** `requirements` → `designed` → `planned` → `complete`

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| continuation-prepend | requirements | Problem statement only |
| error-handling | requirements | Outline complete, Phase B blocked on workflow improvements |
| feature-requests | requirements | GH issue research (sandbox, tool overrides) |
| orchestrate-evolution | designed | Design.md complete, vet in progress, planning next |
| parallel-orchestration | requirements | Deferred from orchestrate-evolution (worktree isolation needed) |
| plugin-migration | planned | Runbook assembled: 15 steps, haiku execution ready |
| reports | — | Shared reports directory (not a plan) |
| tweakcc | requirements | Local instances research |
| when-recall | complete | `/when` memory recall system — 12 phases, merged to main, 2 deliverable reviews |
| worktree-skill | complete | Design.md retained on disk for reference |
| worktree-update | complete | 40 TDD cycles, recovery (C2-C5), merged to main |
| worktree-merge-data-loss | complete | 13 TDD cycles + 1 general step, merged to main, deliverable review done |
| workwoods | requirements | Cross-tree worktree awareness, vet tracking, plan state inference, bidirectional merge |
| prototypes | requirements | Session extraction feature gap, multi-project scanning |
| remaining-workflow-items | complete | 5 FRs: reflect task output, tool-batching, delegate resume, agent output, commit simplification |
| remember-skill-update | requirements | Outline + requirements.md complete, Phase B discussion next |

## Complete (Archived)

*48 plans completed and deleted. Git history preserves all designs/reports.*

Use `git log --all --online -- plans/<name>/` to find commits, `git show <hash>:<path>` to retrieve files.

**Recent:**
- `remaining-workflow-items` — 5 FRs: reflect task output, tool-batching, delegate resume, agent output, commit simplification
- `worktree-merge-data-loss` — Removal guard + merge correctness (13 TDD cycles, deliverable review)
- `grounding-skill` — Ground skill with diverge-converge research procedure
- `pushback` — Two-layer anti-sycophancy: fragment + hook, S1/S2/S4 validated
- `pushback-improvement` — Implemented Tier 1 direct from pushback worktree
- `workflow-rca-fixes` — 20 FRs: skill composition, type-agnostic review, vet taxonomy, outline enhancements
- `worktree-fixes` — All 4 phases done, 5 FRs satisfied, 25 TDD cycles + 4 prose edits
- `workflow-fixes` — Unified /runbook skill, plan-reviewer agent, review-plan skill, pipeline-contracts
- `process-review` — RCA: 5 plans examined, root cause in planning skill, 5 recommendations
- `memory-index-recall` — Bug fixes + reanalysis (M-1, M-2 fixed, 0.2% recall confirmed)
- `workflow-skills-audit` — Superseded by runbook unification (all 12 items landed)
- `reflect-rca-sequential-task-launch` — Subsumed into process-review worktree
- `requirements-skill` — Dual-mode extract/elicit requirements skill, empirical grounding
- `worktree-skill` — Worktree skill implementation (42/42 cycles, merged to dev)
- `worktree-skill-fixes` — Worktree skill findings (27 fixes across 7 phases, merged to dev)
- `handoff-validation` — Killed: problems resolved by existing tooling
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
