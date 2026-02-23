# Session: Worktree — Phase-scoped agent context

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Phase-scoped agent context** — `/design` | sonnet
  - prepare-runbook.py emits per-phase agents with phase-scoped shared context instead of one agent per runbook
  - Same base type can serve multiple phases — differentiator is injected context, not protocol
  - Orchestrate-evolution depends on this for dispatch side
