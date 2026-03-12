**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Research Backlog

## Problem

Umbrella for five deferred research tasks, collapsed from individual tasks during prioritization consolidation. Each needs investigation before requirements can be written.

## Sub-problems

- **Ground state coverage:** Research state management coverage gaps across the workflow pipeline. Which state transitions are unmonitored? Where do agents lose track of workflow state?

- **Workflow formal analysis:** Apply formal analysis techniques to workflow state machines (design → runbook → orchestrate → inline). Identify unreachable states, deadlocks, missing transitions.

- **Design-to-deliverable (restart):** Research improvements to the design-to-deliverable pipeline. Current pipeline loses context across restarts. Requires session restart to investigate.

- **Behavioral design:** Research behavioral specification patterns for agent directives. Current approach (prose fragments) lacks formal rigor — are there established specification frameworks?

- **Compensate-continue skill:** Research compensation patterns for interrupted workflows. When a skill or agent is interrupted mid-execution, what recovery patterns exist?

## Success Criteria

Each sub-problem produces a research report in `plans/reports/` with findings and recommendations for whether to proceed to requirements capture.
