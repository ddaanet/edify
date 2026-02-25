# Orchestrator Plan: recall-tool-anchoring

Execute steps using per-phase agents.

Stop on error and escalate to sonnet for diagnostic/fix.

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | crew-recall-tool-anchoring-p1 | general |
| 4 | crew-recall-tool-anchoring-p4 | general |


## Step Execution Order

## step-1-1 (Step 1.1)
Agent: crew-recall-tool-anchoring-p1
Execution: steps/step-1-1.md

## step-1-2 (Step 1.2)
Agent: crew-recall-tool-anchoring-p1
Execution: steps/step-1-2.md

## step-1-3 (Step 1.3) — PHASE_BOUNDARY
Agent: crew-recall-tool-anchoring-p1
Execution: steps/step-1-3.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## Phase 2: Reference manifest conversion — INLINE
Execution: inline
Model: sonnet
[Orchestrator-direct. Convert plans/recall-tool-anchoring/recall-artifact.md from content-dump to reference manifest format. See runbook Phase 2 for conversion mapping.]

## Phase 3: D+B restructure of recall gates — INLINE
Execution: inline
Model: opus
[Orchestrator-direct. Apply D+B tool-anchoring to 8 files (6 read-side + 2 write-side). See runbook Phase 3 for variation table and patterns.]

## step-4-1 (Step 4.1)
Agent: crew-recall-tool-anchoring-p4
Execution: steps/step-4-1.md

## step-4-2 (Step 4.2) — PHASE_BOUNDARY
Agent: crew-recall-tool-anchoring-p4
Execution: steps/step-4-2.md
[Last item of phase 4. Insert functional review checkpoint before Phase 5.]


## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet (inline)
- Phase 3: opus (inline)
- Phase 4: sonnet
