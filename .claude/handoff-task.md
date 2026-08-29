## Current task

Pipeline simplification: replacing the two-stage runbook / step-file / manifest model with a single `runbook.md` that a strong orchestrator composes dispatch prompts from live, with slice-batched TDD keeping RED and GREEN as separate dispatches. `plans/pipeline-simplification/requirements.md` is /proof-validated (7 FRs, 5 constraints, 2 open questions on the GREEN role and refactor placement); the next stage is `/design`, and per its C-5 the work executes as an inline task sequence on a branch, not through the pipeline it changes.
