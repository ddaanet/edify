# Orchestrator Plan: hook-batch

Execute steps sequentially using per-phase agents. Each phase has its own agent with phase-specific common context.

Stop on error and escalate to sonnet for diagnostic/fix.

## Phase-Agent Mapping

| Phase | Agent | Model | Type |
|-------|-------|-------|------|
| 1 (steps 1-1 to 1-5) | hb-p1 | sonnet | TDD |
| 2 (steps 2-1 to 2-2) | hb-p2 | sonnet | TDD |
| 3 (steps 3-1 to 3-2) | hb-p3 | haiku | General |
| 4 (steps 4-1 to 4-3) | hb-p4 | haiku | General |
| 5 (steps 5-1 to 5-4) | hb-p5 | haiku | General |

Exception: step-5-3 uses sonnet (override via Task model parameter).

## Step Execution Order

## step-1-1 (Cycle 1.1)
Agent: hb-p1
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2)
Agent: hb-p1
Execution: steps/step-1-2.md

## step-1-3 (Cycle 1.3)
Agent: hb-p1
Execution: steps/step-1-3.md

## step-1-4 (Cycle 1.4)
Agent: hb-p1
Execution: steps/step-1-4.md

## step-1-5 (Cycle 1.5) — PHASE_BOUNDARY
Agent: hb-p1
Execution: steps/step-1-5.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Cycle 2.1)
Agent: hb-p2
Execution: steps/step-2-1.md

## step-2-2 (Cycle 2.2) — PHASE_BOUNDARY
Agent: hb-p2
Execution: steps/step-2-2.md
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## step-3-1 (Step 3.1)
Agent: hb-p3
Execution: steps/step-3-1.md

## step-3-2 (Step 3.2) — PHASE_BOUNDARY
Agent: hb-p3
Execution: steps/step-3-2.md
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]

## step-4-1 (Step 4.1)
Agent: hb-p4
Execution: steps/step-4-1.md

## step-4-2 (Step 4.2)
Agent: hb-p4
Execution: steps/step-4-2.md

## step-4-3 (Step 4.3) — PHASE_BOUNDARY
Agent: hb-p4
Execution: steps/step-4-3.md
[Last item of phase 4. Insert functional review checkpoint before Phase 5.]

## step-5-1 (Step 5.1)
Agent: hb-p5
Execution: steps/step-5-1.md

## step-5-2 (Step 5.2)
Agent: hb-p5
Execution: steps/step-5-2.md

## step-5-3 (Step 5.3)
Agent: hb-p5 (model override: sonnet)
Execution: steps/step-5-3.md

## step-5-4 (Step 5.4) — PHASE_BOUNDARY
Agent: hb-p5
Execution: steps/step-5-4.md
[Last item of phase 5. Final review checkpoint.]
