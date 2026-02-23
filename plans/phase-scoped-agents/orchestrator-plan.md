# Orchestrator Plan: phase-scoped-agents

Execute steps sequentially using phase-scoped-agents-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.

## Step Execution Order

## step-1-1 (Cycle 1.1)
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2)
Execution: steps/step-1-2.md

## step-1-3 (Cycle 1.3)
Execution: steps/step-1-3.md

## step-1-4 (Cycle 1.4) — PHASE_BOUNDARY
Execution: steps/step-1-4.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Cycle 2.1)
Execution: steps/step-2-1.md

## step-2-2 (Cycle 2.2)
Execution: steps/step-2-2.md

## step-2-3 (Cycle 2.3) — PHASE_BOUNDARY
Execution: steps/step-2-3.md
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## phase-3 (Phase 3 (inline))
Execution: inline
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]


## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: sonnet
