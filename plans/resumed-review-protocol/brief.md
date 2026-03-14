## 2026-03-10: Evolved review model — resumed reviewer ping-pong

### Origin

Archeology session on pipeline-review-protocol MA2 (phase-file separation) led to broader discussion of the review model. Phase files exist for authoring efficiency (avoid rewriting full runbook when changing one phase), not review granularity. This surfaced that the current review model (fresh corrector per artifact) doesn't match the user's evolved perspective.

### User braindump (verbatim)

> Instead of batch review, use one resumed reviewer (not corrector!), that feeds back to the (resumed) executor agent (tentatively: FIX/PASS), then review the fixed artefact (fix/pass again). The reviewer decides whether all issues have been adressed.
>
> If second fix (so, third review, second resume of reviewer) did not address all issues, there is a drift problem, orchestrator interrupts execution and start agent to diagnose the issues. If file and history examination is not sufficent, use session scraping to finer detail.
>
> No filtering, the executor must adress all concerns at fix time. Adress does not always mean execute suggested fix, it could be adding to the reviewed artefact a clarification that changes the reviewer position.
>
> Ping-pong TDD is a generalization. Orchestrator should have instruction to run a reviewer sub agent in addition to the tester and implementer agents. The review-fix cycle is run after each step, red (reviewing tests) or green (reviewing implementation).
>
> Checkpoint commit every review-implement cycle.
>
> Reviewer remains anchored on requirements because it does not see think blocks, only commits.
>
> Executor receives targeted feedback it can apply for the following run.
>
> Review cycles are context efficient. Reuse agents until 150ktok context.
>
> Following agents get access to the reviews of all the previous cycles, so agent restart is efficient context truncation.
>
> The only obvious drawback is the added latency in the critical path.

### Two distinct features (user correction)

1. **Runbook skill's own corrector usage (plan artifacts):** When runbook generates phase files, it currently runs fresh correctors per phase. Should reuse the same corrector across phases. Holistic review remains but with a fresh agent as safety net (catches what the resumed reviewer normalized).

2. **Runbook step templates for orchestration (deliverable artifacts):** How steps describe the review-fix protocol for the orchestrator to execute during implementation. This is where the ping-pong FIX/PASS loop goes. Touches step template references in general-patterns.md and related files.

### Key design properties from discussion

- **Resumed reviewer accumulates understanding** — builds model of artifact state across cycles, doesn't reconstruct from scratch
- **Commit-only visibility** — reviewer sees commits not think blocks, stays anchored on observable output
- **Drift detection** — third review still failing triggers diagnostic agent with fresh context
- **Diagnostic escalation** — file/history examination first, session scraping for finer detail
- **"Address" not "execute"** — executor can clarify the artifact instead of applying the suggested fix, changing the reviewer's position
- **Context budget** — reuse agents until 150K tokens, then restart with review history as context seed
- **Checkpoint commits** — every review-implement cycle commits, creating clean truncation boundaries
- **TDD generalization** — reviewer is third agent alongside tester and implementer, runs after both RED and GREEN steps

## 2026-03-14: Rework artifact model gaps

Discussion during handoff-cli-tool runbook preparation surfaced two gaps in the brief's coverage.

### Rework reports as named artifacts

Reviewer feedback needs a concrete artifact type. Per-cycle, reviewer produces 1-3 rework reports — one per reviewed work item (tester output, coder output). Reports use PASS/REWORK verdicts. Naming convention undecided — needs design (e.g., `reports/phase-N/cycle-M-tester-rework.md`, or structured differently).

Cardinality: 1-3 rework reports per TDD cycle (one per agent's work item reviewed). Each rework round produces a new report if verdict is REWORK. Reports accumulate per phase.

### Restarted agents consume rework reports

Brief says restarted agents get "access to the reviews of all the previous cycles" — but doesn't distinguish between review reports (reviewer's assessment) and rework reports (reviewer's feedback to authors). When tester or coder agents restart at 150K context, they need the rework reports specifically (targeted feedback for their role), not just the reviewer's assessment. Reviewer on restart reads all reports from the phase (both its own assessments and the rework artifacts).
