# Gate Batch

Mechanical checkpoints at skill entry/exit/transition points. Prevent stale artifacts, missing context, and uncommitted state from propagating through the workflow pipeline.

## Requirements

### Functional Requirements

**FR-1: Artifact staleness gate**
Verify plan artifacts (design.md, outline.md, runbook files) are current relative to their inputs before skill execution. Gate fires at skill entry for `/runbook`, `/orchestrate`, and `/inline`. Staleness detection uses git commit history first (committed input newer than committed artifact), file timestamps second (for uncommitted changes).
- Acceptance: Stale artifact detected → skill halts with message identifying which artifact is stale and what changed since it was written
- Acceptance: Git history checked before filesystem timestamps (committed state is source of truth)

**FR-2: Entry gate propagation**
Propagate gate checks across skill boundaries when one skill chains to another (e.g., `/design` → `/runbook` → `/orchestrate`). Downstream skill inherits upstream's gate results rather than re-running.
- Acceptance: Chain of 3 skills runs gate once at entry, not 3 times

### Out of Scope

- Runtime validation during execution (these are entry/exit gates only)
- Modifying the skill execution model — gates are pre/post checks, not middleware

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (gates may be implemented as hooks)
