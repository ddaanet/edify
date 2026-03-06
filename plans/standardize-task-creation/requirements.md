# Standardize Task Creation Across Skills

## Problem

Skills that create follow-up tasks do so inconsistently: different destinations (`todo.md`, implicit session.md, unspecified), inconsistent skill-invocation routing, and missing section targeting. This caused a concrete failure: `/deliverable-review` wrote a task to `todo.md`, then `/worktree` couldn't find it (looks in `session.md` Worktree Tasks only).

## Requirements

### Functional Requirements

**FR-1: Standardized task destination**
All task-producing skills write follow-up tasks to `agents/session.md`. No skill writes actionable follow-up tasks to `todo.md` or leaves destination unspecified. Target section determined by C-1 (context-aware).

Acceptance criteria:
- Every skill that creates a task writes it to session.md (section per C-1)
- `/worktree` and `/prioritize` can discover all pending tasks from session.md alone
- `/shelve` continues using `todo.md` for archival (not follow-up work — out of scope)

**FR-2: Mandatory skill invocation in task format**
Every created task includes a skill invocation as the entry command. This ensures recall, grounding, and planning run before execution. `/design` is the default entry point (its triage handles proportionality — routes Tier 1 to `/inline`, Tier 2-3 to full design).

Acceptance criteria:
- Task format: `- [ ] **Task Name** — \`/skill args\` | model`
- The skill invocation is never omitted
- `/design` is the default unless a more specific skill is appropriate (e.g., `/deliverable-review` for review tasks)

**FR-3: Terminal state exception**
Skills at terminal pipeline states do not create tasks when there is no follow-up work:
- Worktree: branch ready to merge (work complete, no pending tasks in worktree session)
- Main branch: no pending task produced by skill outcome

Acceptance criteria:
- Terminal skills (e.g., `/worktree` merge ceremony, `/deliverable-review` with 0 findings) produce no task
- Non-terminal outcomes always produce a task

### Constraints

**C-1: Context-aware section targeting**
Skills determine target section mechanically from tree context:
- On main → write to Worktree Tasks (main is worktree-tasks-only; skill-created tasks are never trivial fixes)
- In a worktree → write to In-tree Tasks (worktrees don't nest)

**C-2: Existing task format preserved**
The `- [ ] **Name** — \`command\` | model | restart?` format is already used by `/reflect` and `/inline`. Standardize on this exact format.

### Affected Skills

| Skill | Current behavior | Required change |
|---|---|---|
| `/deliverable-review` | Unspecified destination, has skill invocation | Add destination: session.md (section per C-1) |
| `/reflect` | session.md Pending Tasks, has format | Already compliant (verify) |
| `/orchestrate` | Implicit session.md, inconsistent routing | Specify destination + skill invocation |
| `/inline` | States task, handoff captures | Specify destination explicitly |
| `/release-prep` | Reads tasks, doesn't create | No change needed |
| `/worktree` | Consumes tasks from Worktree Tasks; merge ceremony may produce follow-up | Verify reads standardized format; merge ceremony follows FR-3 terminal state rules |

### Out of Scope

- `/shelve` archival to `todo.md` — different pipeline (archive + `/next` retrieval)
- Task prioritization or ordering — handled by `/prioritize`
- Manual worktree vs in-tree reclassification — C-1 makes this mechanical
- New skills or hooks — this is a documentation/format standardization pass

## Origin

RCA from devddaanet `/reflect` session (2026-03-05). `/deliverable-review` wrote fix task to `todo.md`, `/worktree new` failed because task wasn't in session.md Worktree Tasks.
