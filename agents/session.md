# Session: Worktree — Workflow improvements

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Workflow improvements** — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
  - RCA blocker resolved — reports at `plans/reports/rca-*-opus.md`
  - Input: `plans/orchestrate-evolution/design.md`, `plans/process-review/rca.md`
  - Orchestrate evolution — designed, stale Feb 10, refresh after RCA
  - Fragments cleanup — remove fragments duplicating skills/workflow
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work
  - Agent output optimization — remove summarize/report language from agents
  - Investigation prerequisite rule review
  - Design skill: Phase C density checkpoint (TDD non-code marking handled by per-phase typing)
  - Workflow fixes from RCA — `plans/reports/rca-*-opus.md`, normalize runbook-review axes, execution-time split, vet investigation protocol, orchestrate template
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit
  - Fix skill-based agents not using skills prolog section — `skills:` frontmatter
