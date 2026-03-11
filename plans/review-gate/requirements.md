# Review Gate

Precommit gate enforcing review coverage on production artifacts.

## Requirements

### Functional Requirements

**FR-1: Review timestamp validation**
Add a precommit step that verifies review report timestamp >= production artifact edit timestamp. No triviality exception — all production artifact edits require a review report.
- Acceptance: Production artifact modified after last review report → precommit fails with "review report stale for <file>"
- Acceptance: Production artifact modified with current review report → precommit passes
- Acceptance: Non-production files (tests, tmp/, plans/reports/) exempt from gate

### Constraints

**C-1: Implements defense-in-depth decision**
Gate enforces the "gate at chokepoint" pattern from `agents/decisions/defense-in-depth.md`.

### Evidence

JIT expansion commit skipped vet checkpoint — no automated enforcement existed.

### Out of Scope

- Defining what constitutes a "production artifact" (use existing classification if available, otherwise define during design)
- Review quality assessment (gate checks existence and recency, not content)
