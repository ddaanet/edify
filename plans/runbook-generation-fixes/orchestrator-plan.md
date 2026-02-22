# Orchestrator Plan: runbook-generation-fixes

Execute steps sequentially using runbook-generation-fixes-task agent.

Stop on error and escalate to sonnet for diagnostic/fix.

## Step Execution Order

## step-1-1 (Cycle 1.1)
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2)
Execution: steps/step-1-2.md

## step-1-3 (Cycle 1.3) — PHASE_BOUNDARY
Execution: steps/step-1-3.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Cycle 2.1)
Execution: steps/step-2-1.md

## step-2-2 (Cycle 2.2)
Execution: steps/step-2-2.md

## step-2-3 (Cycle 2.3)
Execution: steps/step-2-3.md

## step-2-4 (Cycle 2.4)
Execution: steps/step-2-4.md

## step-2-5 (Cycle 2.5) — PHASE_BOUNDARY
Execution: steps/step-2-5.md
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## step-3-1 (Cycle 3.1)
Execution: steps/step-3-1.md

## step-3-2 (Cycle 3.2)
Execution: steps/step-3-2.md

## step-3-3 (Cycle 3.3) — PHASE_BOUNDARY
Execution: steps/step-3-3.md
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]

## step-4-1 (Cycle 4.1)
Execution: steps/step-4-1.md

## step-4-2 (Cycle 4.2) — PHASE_BOUNDARY
Execution: steps/step-4-2.md
[Last item of phase 4. Insert functional review checkpoint before Phase 5.]

