### Phase C: Generate Design

**Objective:** Produce full design document, review, fix, commit.

#### C.1. Create Design Document

**Recall diff:** Read `references/research-protocol.md` §A.5 and, by it,
re-invoke recall on what just changed and reconcile the artifact.

**Output:** `plans/<job-name>/design.md`

**Content rules:** Read `references/design-content-rules.md` for content
principles, density checkpoint, agent-name validation, classification table
format, structure guidance, requirements section format, TDD additions,
provenance/references/documentation perimeter sections, and
skill-loading/execution model directives.

#### C.2. Checkpoint Commit

**Objective:** Commit the design document before review.

**Process:** Stage and commit `plans/<job-name>/design.md` (and any reports from
Phase A).

**Why:** Preserves design state before review cycle. Enables diffing original vs
post-review version. Isolates review changes in separate commit for audit trail.

#### C.3. Review Design

**CRITICAL: Delegate to design-corrector for review.**

Use Agent tool with `subagent_type="edify:design-corrector"`:

```
Review plans/<job-name>/design.md — Critical Design Review (CDR) criteria:
- Decisions fully specified (implementer needs no inference)
- Interfaces and integration points defined
- Agent/tool names verified against disk
- Test strategy or verification approach specified
- Late-added requirements re-validated
- Each major decision includes accepted tradeoffs

Include review-relevant entries from plans/<job-name>/recall-artifact.md if present (failure modes, quality anti-patterns).

Write detailed review to: plans/<job-name>/reports/design-review.md

Return only the filepath on success, or 'Error: [description]' on failure.
```

The design-corrector (opus model) performs comprehensive architectural review
and writes a structured report with critical/major/minor issues categorized.

#### C.4. Check for Unfixable Issues

**Read the review report** from the filepath returned by design-corrector.

The design-corrector applies all fixes (critical, major, minor) directly. This
step handles residual issues:

- **No UNFIXABLE issues:** Proceed to C.5.
- **UNFIXABLE issues found:** Address manually or escalate to user.

**Re-review if needed:** If user manually addresses UNFIXABLE issues,
re-delegate to design-corrector for verification.

#### C.4.5. User Validation

Invoke `/edify:proof plans/<job-name>/design.md` — structured validation loop on
the completed design before routing to execution or /runbook. On terminal action
"apply", /proof dispatches design-corrector automatically.

This is the user's first review of the full design document. The corrector
review (C.3) checked mechanical quality; /proof validates design decisions and
completeness with the user.

#### C.5. Execution Route and Handoff

`Read plans/<job>/design.md` — load the design to ground the routing decision.

Design can resolve complexity — a job correctly classified as Complex may
produce Simple execution. Assess whether the completed design needs runbook
planning or goes straight to `/build`.

Read `references/route-to-execution.md` and route by it.

## Constraints

- High-capability model only (deep reasoning required)
- Delegate exploration (cost/context management)
- Dense output — omit obvious details planners can infer, focus on non-obvious
  decisions and constraints
- Design documents contain guidance (planners may adapt) and constraints
  (planners must follow literally). Classification tables are constraints.
