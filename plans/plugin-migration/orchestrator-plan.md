# Orchestrator Plan: plugin-migration

**Agent:** plugin-migration-task
**Corrector Agent:** plugin-migration-corrector
**Type:** general

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | plugin-migration-task | general |
| 2 | plugin-migration-task | general |
| 3 | plugin-migration-task | general |
| 4 | plugin-migration-task | general |
| 5 | plugin-migration-task | general |
| 6 | plugin-migration-task | general |


## Steps

- step-1-1.md | Phase 1 | sonnet | 30
- step-1-2.md | Phase 1 | sonnet | 30
- step-1-3.md | Phase 1 | sonnet | 30 | PHASE_BOUNDARY
- step-2-1.md | Phase 2 | sonnet | 30
- step-2-3.md | Phase 2 | sonnet | 30 | PHASE_BOUNDARY
- step-3-1.md | Phase 3 | opus | 30
- step-3-2.md | Phase 3 | opus | 30 | PHASE_BOUNDARY
- step-4-1.md | Phase 4 | sonnet | 30
- step-4-2.md | Phase 4 | sonnet | 30 | PHASE_BOUNDARY
- step-5-1.md | Phase 5 | sonnet | 30
- step-5-2.md | Phase 5 | sonnet | 30 | PHASE_BOUNDARY
- step-6-1.md | Phase 6 | sonnet | 30
- step-6-2.md | Phase 6 | sonnet | 30
- step-6-3.md | Phase 6 | sonnet | 30 | PHASE_BOUNDARY

## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: opus
- Phase 4: sonnet
- Phase 5: sonnet
- Phase 6: sonnet

## Phase Files

- Phase file: plans/plugin-migration/runbook-phase-1.md
- Phase file: plans/plugin-migration/runbook-phase-2.md
- Phase file: plans/plugin-migration/runbook-phase-3.md
- Phase file: plans/plugin-migration/runbook-phase-4.md
- Phase file: plans/plugin-migration/runbook-phase-5.md
- Phase file: plans/plugin-migration/runbook-phase-6.md

## Phase Summaries

### Phase 1:

- IN: Create the plugin structure inside existing `agent-core/` directory. Checkpoint at end gates all downstream phases.
- OUT: Phase 2, Phase 3, Phase 4, Phase 5, Phase 6

### Phase 2:

- IN: Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage.
- OUT: Phase 1, Phase 3, Phase 4, Phase 5, Phase 6

### Phase 3:

- IN: Create `/edify:init` and `/edify:update` skills — agentic prose artifacts requiring opus.
- OUT: Phase 1, Phase 2, Phase 4, Phase 5, Phase 6

### Phase 4:

- IN: Extract portable recipes and update root justfile.
- OUT: Phase 1, Phase 2, Phase 3, Phase 5, Phase 6

### Phase 5:

- IN: Wire version consistency and release coordination. Runs early — creates `.edify.yaml` before Phase 2's setup hook needs it.
- OUT: Phase 1, Phase 2, Phase 3, Phase 4, Phase 6

### Phase 6:

- IN: Execute after plugin verified working. Irreversible within session.
- OUT: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5
