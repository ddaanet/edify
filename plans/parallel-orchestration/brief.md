# Parallel Orchestration

## Problem

Orchestrate skill executes runbook steps sequentially. For plans with independent steps (e.g., multiple modules with no shared files), this wastes wall-clock time. Parallel dispatch would batch independent Task calls in a single message.

**Blocker:** Concurrent agents editing files and committing in the same git repo causes race conditions. All execution agents (implementation and vet-fix) mutate the working tree. Parallel execution requires worktree isolation.

## Requirements

- FR-1: Parallel dispatch of independent runbook steps via multiple Task calls in single message
- FR-2: Worktree isolation per parallel agent — each agent works in its own worktree
- FR-3: Merge worktrees back after parallel group completes
- FR-4: Handle merge conflicts (file overlap detection before dispatch, conflict resolution after)
- FR-5: Orchestrator plan format declares parallel groups with explicit execution order

- NFR-1: Depends on worktree-skill completion (currently 38%)
- NFR-2: Depends on orchestrate-evolution completion (sequential execution must work first)

## Design Decisions (from orchestrate-evolution)

### Execution order format

Orchestrator plan declares parallel groups:
```
## Execution Order

### Group 1 (sequential)
- step-0-1 (model: sonnet)

### Group 2 (parallel)
- step-1-1 (model: sonnet)
- step-1-2 (model: sonnet)
- step-1-3 (model: sonnet)

### Group 3 (sequential)
- step-2-1 (model: sonnet)
```

Sequential groups: one Task call per step. Parallel groups: batch all Task calls in single message. Phase boundary checkpoints between groups.

### prepare-runbook.py

Emits execution order with explicit grouping based on runbook parallelism annotations.

### No read-only parallel operations

All agents during orchestration mutate the working tree (vet-fix-agent applies fixes, implementation agents edit and commit). No safe parallelism without isolation.
