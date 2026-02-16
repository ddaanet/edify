# Task Prioritization: Grounded Methodology

## Research Foundation

This methodology adapts **WSJF (Weighted Shortest Job First)** — Reinertsen's prioritization framework — to an internal tooling and agent orchestration context where "cost" is measured in developer friction, agent reliability, and token budget rather than revenue.

**Core formula:** `Priority = Cost of Delay / Job Size`

**Why WSJF over RICE/ICE:**
- RICE requires "Reach" (user count) — irrelevant for single-developer internal tooling
- ICE is too subjective ("low/medium/high" without decomposition)
- WSJF decomposes Cost of Delay into measurable components and naturally prioritizes high-value small work — exactly the batching behavior needed for a backlog mixing 30-minute fixes with multi-session design arcs

**Adaptation:** Reinertsen decomposes CoD into User-Business Value + Time Criticality + Risk Reduction/Opportunity Enablement. Below, each component is redefined with project-specific scoring criteria grounded in observable evidence.

### Sources

- [RICE vs WSJF comparison](https://www.centercode.com/blog/rice-vs-wsjf-prioritization-framework)
- [ICE, RICE, WSJF backlog organization](https://hackernoon.com/ice-rice-wsjf-or-how-to-organize-your-backlog-effectively)
- [13 prioritization techniques](https://www.ppm.express/blog/13-prioritization-techniques)
- [RICE vs WSJF detailed comparison](https://product-blueprint.com/rice-vs-wsjf/)
- [Cost of Delay without tangible metrics](https://liminalarc.co/2017/06/cost-delay-project-management-2/)
- [Cost of Delay for developer productivity](https://newsletter.getdx.com/p/cost-of-delay)

---

## Cost of Delay Components

CoD is decomposed into three components. Each is scored on a Fibonacci-capped scale (1, 2, 3, 5, 8) using relative estimation — the smallest item anchors at 1.

### Component 1: Workflow Friction (replaces User-Business Value)

**Definition:** How frequently the unresolved problem this task addresses is encountered during normal operation.

The "users" are agents and the developer. "Value" is friction removed from recurring workflows.

| Score | Criteria                          | Examples                                                   |
| ----- | --------------------------------- | ---------------------------------------------------------- |
| 8     | Every task execution (inner loop) | Commit flow, precommit, vet delegation, orchestration step |
| 5     | Every session boundary            | Handoff, status display, context recovery                  |
| 3     | Weekly or per-task-type           | Worktree setup, design sessions, memory consolidation      |
| 2     | Monthly or per-plan               | Plugin migration, formal analysis                          |
| 1     | One-time or rarely invoked        | External PR, infrastructure script used once               |

**Evidence source:** Count occurrences in recent session transcripts or estimate from workflow step frequency.

### Component 2: Decay Pressure (replaces Time Criticality)

**Definition:** How much more expensive the task becomes per unit time deferred, measured by drift in referenced artifacts and narrowing of decision windows.

Combines two observable phenomena:
- **Knowledge decay:** Design artifacts reference file structures, counts, or interfaces that change as other work lands
- **Decision lock-in:** Architectural decisions become load-bearing as dependent work accumulates on top

| Score | Criteria                                                                                                                            | Examples                                                                                                        |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 8     | Design explicitly flagged stale; target files changed in 3+ of last 10 commits; OR task produces decisions 5+ future tasks build on | Plugin migration (stale Feb 9, drift in counts); memory redesign (blocks 3+ tasks)                              |
| 5     | Target files changed in 1-2 of last 10 commits; design references shifting structures; OR decisions affect 2-4 future tasks         | Error handling design (outline exists, codebase evolving); pushback design (pushback-improvement depends on it) |
| 3     | Target area relatively stable; design references durable abstractions; decisions have limited blast radius                          | Commit CLI tool (commit patterns stable); continuation prepend                                                  |
| 2     | Self-contained with minimal external references                                                                                     | Precommit improvements (validators are stable)                                                                  |
| 1     | No external references that can drift; fully reversible                                                                             | Upstream skills field (external PR); infrastructure scripts                                                     |

**Evidence source:** `git log --oneline -10 -- <target-files>` for churn; count blocked tasks in session.md for lock-in.

### Component 3: Compound Risk Reduction (replaces Risk Reduction / Opportunity Enablement)

**Definition:** Degree to which completing this task prevents recurring defects, unblocks downstream work, or improves agent execution reliability across ALL future work.

Three sub-dimensions, take the maximum:

**A. Defect compounding** — Does the task fix a pattern that propagates through orchestrated execution?
| Score | Criteria                                                                      |
| ----- | ----------------------------------------------------------------------------- |
| 8     | Pattern in 3+ RCA findings (tmp/ refs, skill drift, confabulated methodology) |
| 5     | Pattern appeared twice or in high-throughput path                             |
| 3     | Pattern appeared once                                                         |
| 1     | Not a defect fix                                                              |

**B. Downstream unblock** — How many other tasks does this unblock?
| Score | Criteria           |
| ----- | ------------------ |
| 8     | Unblocks 4+ tasks  |
| 5     | Unblocks 2-3 tasks |
| 3     | Unblocks 1 task    |
| 1     | No dependents      |

**C. Agent reliability delta** — Does completing this reduce agent execution failures?
| Score | Criteria                                                |
| ----- | ------------------------------------------------------- |
| 8     | Directly reduces measured failure mode (3+ occurrences) |
| 5     | Addresses failure mode observed 1-2 times               |
| 3     | Proactive catch for a class of errors                   |
| 1     | No impact on agent reliability                          |

**Evidence source:** Search RCA reports in `plans/*/reports/`; count blockers in session.md; grep for failure patterns in learnings.md history.

---

## Job Size

Estimated cost to advance the task to completion. Scored on Fibonacci scale (1, 2, 3, 5, 8).

Two sub-dimensions, summed:

### Marginal Effort (inverse of artifact readiness)

| Score | Criteria                                              |
| ----- | ----------------------------------------------------- |
| 1     | `planned` — runbook exists, ready for orchestration   |
| 2     | `designed` — design.md vetted, needs runbook          |
| 3     | `requirements` — requirements.md exists, needs design |
| 5     | Problem statement only, no disk artifact              |
| 8     | Greenfield + requires external research               |

**Evidence source:** jobs.md status column.

### Context Recovery Cost

Capped at 5 — recovery cost rarely warrants an 8; the highest practical cost is cross-session research.

| Score | Criteria                                                                      |
| ----- | ----------------------------------------------------------------------------- |
| 1     | All context loaded via CLAUDE.md @-references                                 |
| 2     | Requires reading 1-3 known project files                                      |
| 3     | Requires reading 4+ files or git archaeology                                  |
| 5     | Requires external research or recovering conversation history across sessions |

**Evidence source:** Count file references in session.md task notes.

---

## Scheduling Modifiers

These do not affect priority score but constrain batching and ordering.

### Model Tier Cohort

Tasks requiring the same model tier should be batched to amortize session setup cost (especially opus).

### Restart Cohort

Tasks requiring restart should be batched adjacently.

### Self-Referential Flag

Tasks that modify their own execution path need special handling (manual verification, can't be validated by the system they change).

### Parallelizability

Tasks with low conflict (no shared plan directory, no shared target files, no dependency) can run in concurrent worktrees.

Conflict check: compare target file sets between tasks — empty intersection means parallelizable.

---

## Formula

```
Priority = Cost_of_Delay / Job_Size

Cost_of_Delay = Workflow_Friction + Decay_Pressure + Compound_Risk_Reduction

Job_Size = Marginal_Effort + Context_Recovery_Cost
```

Higher priority score = do first. For equal scores, prefer the task with higher Compound Risk Reduction (defect fixes compound).
