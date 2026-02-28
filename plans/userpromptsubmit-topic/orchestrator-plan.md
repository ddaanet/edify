# Orchestrator Plan: userpromptsubmit-topic

Execute steps using per-phase agents.

Stop on error and escalate to sonnet for diagnostic/fix.

## Phase-Agent Mapping

| Phase | Agent | Type |
| --- | --- | --- |
| 1 | crew-userpromptsubmit-topic-p1 | tdd |
| 2 | crew-userpromptsubmit-topic-p2 | tdd |
| 3 | crew-userpromptsubmit-topic-p3 | tdd |


## Step Execution Order

## step-1-1 (Cycle 1.1)
Agent: crew-userpromptsubmit-topic-p1
Execution: steps/step-1-1.md

## step-1-2 (Cycle 1.2)
Agent: crew-userpromptsubmit-topic-p1
Execution: steps/step-1-2.md

## step-1-3 (Cycle 1.3)
Agent: crew-userpromptsubmit-topic-p1
Execution: steps/step-1-3.md

## step-1-4 (Cycle 1.4)
Agent: crew-userpromptsubmit-topic-p1
Execution: steps/step-1-4.md

## step-1-5 (Cycle 1.5) — PHASE_BOUNDARY
Agent: crew-userpromptsubmit-topic-p1
Execution: steps/step-1-5.md
[Last item of phase 1. Insert functional review checkpoint before Phase 2.]

## step-2-1 (Cycle 2.1)
Agent: crew-userpromptsubmit-topic-p2
Execution: steps/step-2-1.md

## step-2-2 (Cycle 2.2) — PHASE_BOUNDARY
Agent: crew-userpromptsubmit-topic-p2
Execution: steps/step-2-2.md
[Last item of phase 2. Insert functional review checkpoint before Phase 3.]

## step-3-1 (Cycle 3.1)
Agent: crew-userpromptsubmit-topic-p3
Execution: steps/step-3-1.md

## step-3-2 (Cycle 3.2)
Agent: crew-userpromptsubmit-topic-p3
Execution: steps/step-3-2.md

## step-3-3 (Cycle 3.3) — PHASE_BOUNDARY
Agent: crew-userpromptsubmit-topic-p3
Execution: steps/step-3-3.md
[Last item of phase 3. Insert functional review checkpoint before Phase 4.]


## Phase Models

- Phase 1: sonnet
- Phase 2: sonnet
- Phase 3: sonnet
