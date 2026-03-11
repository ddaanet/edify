# Design Backlog Review

17 UNREVIEWED plan files assessed. Verdicts: **approve** (proceed to design), **kill** (delete), **refine** (fix gaps before design).

## Requirements Files (10)

### cross-tree-operations — APPROVE
FR-1 (git show transport) and FR-2 (content-hash test sentinel) are concrete with acceptance criteria. FR-1 formalizes an existing `git show` pattern. Scope bounded, out-of-scope clear.

### gate-batch — KILL (absorbed)
FR-3 (design context gate) duplicates `plans/design-context-gate/brief.md` which already exists as a separate briefed plan. FR-1 (staleness gate), FR-2 (entry gate propagation), FR-4 (pre-inline commit) are independently scoped but loosely coupled. Recommend killing this plan and letting design-context-gate absorb FR-3. FR-1/2/4 can become standalone plans or be absorbed into hook-batch-2 if they're hook-implementable.

### health-check-ups-fallback — APPROVE
Single FR, concrete mechanism (flag-file coordination), bounded. Latency constraint (C-2) is measurable. Straightforward hook work.

### hook-batch-2 — APPROVE
Three independent hooks, each with clear trigger and acceptance criteria. C-1 (500ms budget) is measurable. Well-scoped.

### planstate-brief-inference — APPROVE
Single FR, precise code location (`planstate.py`), clear acceptance criteria. Mechanical fix.

### prose-infra-batch — KILL (delivered)
Already executed and delivered. Deliverable review completed (`plans/prose-infra-batch/reports/deliverable-review.md`). UNREVIEWED banner is stale.

### recall-pipeline — REFINE
FR-1 (dedup) and FR-3 (usage scoring) overlap with Active Recall sub-tasks (S-D hierarchy index, S-E trigger metadata). Need to clarify: does AR subsume these, or are they independent infrastructure? FR-2 (stdin parsing) is standalone. Recommend splitting FR-2 out as independent, and marking FR-1/FR-3 as blocked-by or absorbed-into AR.

### registry-cache-to-tmp — APPROVE
Single FR, clear convention alignment (tmp-directory rule), bounded scope. Mechanical relocation.

### review-gate — REFINE
FR-1 relies on "production artifact" classification that doesn't exist yet (acknowledged in out-of-scope). The gate can't be built without defining what it gates. Either: (a) define production artifact classification as an FR, or (b) scope to a hardcoded path list and iterate.

### small-fixes-batch — REFINE
Five unrelated fixes batched. Per composite task decomposition, each needs individual assessment:
- FR-1 (hook error after clear): investigation — approve
- FR-2 (upstream skills field): external PR — approve, but may be stale (check if filed already)
- FR-3 (prefix tolerance): code fix with acceptance criteria — approve
- FR-4 (session search CLI): code fix — approve
- FR-5 (context-fork model): exploration — approve, but should live in `plans/prototypes/` not here

No issue with individual items, but FR-5 doesn't belong in a fixes batch. Move to prototypes or drop if context-fork is documented elsewhere.

## Problem Files (7)

### design-pipeline-evolution — REFINE
Two sub-problems (decomposition tier, model directive pipeline) are loosely coupled — "both modify the same skill" isn't architectural coupling. Design skill already handles multi-sub-problem outlines (Phase A), which partially addresses decomposition tier. Model directive pipeline is vague — "mechanism to flag design sections" lacks concrete shape. Recommend: check if decomposition tier is already handled by current outline format; if so, kill that sub-problem and focus on model directives.

### diagnose-compression-loss — APPROVE
Investigation with specific commit reference (`0418cedb`), bounded scope, clear success criteria. May be stale (commit is old) — worth checking if compression quality has been addressed since.

### markdown-migration — KILL (absorbed)
Explicit overlap with `plans/markdown-ast-parser/` (briefed). Open question in the file itself asks whether markdown-ast-parser subsumes the parser sub-problem. Token cache sub-problem (`token_cache.py`) is independent but too small for a combined plan. Threshold migration is configuration work unrelated to markdown. Recommend: kill this plan, let markdown-ast-parser handle parser, spin off token-cache and threshold-config as separate small plans if still wanted.

### quality-grounding — APPROVE
Four `/ground` executions, each producing a report. Existing audit (`workflow-grounding-audit.md`) provides baseline. Investigation work with clear deliverables.

### research-backlog — APPROVE
Umbrella for five deferred research tasks. Explicitly framed as pre-requirements investigation. Each sub-problem produces a go/no-go report. Appropriate structure for research.

### review-agent-quality — APPROVE
Investigation with structured approach (evidence collection → categorization → RCA). Success criteria are measurable (10+ instances, top 3 categories). Existing diagnostic procedure in `agents/decisions/operational-practices.md` supports execution.

### skill-agent-bootstrap — REFINE
Four sub-problems with unclear coupling. "Skill-dev skill" may be superseded by `plugin-dev:skill-development` (platform plugin). "Agent rule injection" may overlap with skill-agent-bootstrap concepts in Claude Code's plugin system. Dependencies section acknowledges this but doesn't resolve it. Recommend: check platform capabilities before design (per project-tooling rule), then kill sub-problems that are platform-covered.

## Summary

| Verdict | Count | Plans |
|---------|-------|-------|
| **Approve** | 9 | cross-tree-operations, health-check-ups-fallback, hook-batch-2, planstate-brief-inference, registry-cache-to-tmp, diagnose-compression-loss, quality-grounding, research-backlog, review-agent-quality |
| **Kill** | 3 | gate-batch (absorbed by design-context-gate), prose-infra-batch (delivered), markdown-migration (absorbed by markdown-ast-parser) |
| **Refine** | 5 | recall-pipeline (AR overlap), review-gate (missing classification), small-fixes-batch (FR-5 misplaced), design-pipeline-evolution (partial overlap with existing), skill-agent-bootstrap (platform overlap) |

### Kill actions
- `plans/gate-batch/` — delete directory, remove task from session.md. Redistribute FR-1/2/4 or let them die.
- `plans/prose-infra-batch/requirements.md` — strip UNREVIEWED banner (plan is delivered, requirements file is historical).
- `plans/markdown-migration/` — delete directory, remove task from session.md.

### Refine actions needed
- **recall-pipeline**: Clarify AR boundary, split FR-2 out
- **review-gate**: Add production artifact classification as FR or hardcode path list
- **small-fixes-batch**: Move FR-5 to prototypes
- **design-pipeline-evolution**: Verify decomposition tier isn't already covered
- **skill-agent-bootstrap**: Platform capability check before design
