# Brief: Inline Lifecycle Gate

## Problem

/inline Phase 4a (corrector dispatch) has no structural enforcement. The skill says "Delegate to corrector agent" — imperative, no escape hatch documented. But the agent skipped corrector during bootstrap-tag-support execution with the rationalization "scope is small and well-tested." This is a prose-gate failure: no tool call proves corrector ran.

The recalled pattern ("when anchoring gates with tool calls"): prose-only gates get skipped under execution momentum. Every skill step must open with a concrete tool call.

Additionally, triage-feedback.sh (Phase 4b) checks classification divergence but not review report existence. There is no mechanical detection of corrector skips.

## Evidence

- bootstrap-tag-support execution: corrector skipped with "scope is small, well-tested" rationalization. Corrector later found 2 minor issues (silent degradation on malformed Bootstrap, missing test coverage).
- Recall: "when anchoring gates with tool calls" — escape hatch IS the failure mode. "when review gates feel redundant" — gates are non-negotiable checkpoints, not confidence-gated decisions.
- /inline SKILL.md Phase 4a (line 122-136): no tool call anchor, no file existence check, no skip-justification mechanism.

## Scope

### Edits

**/inline SKILL.md Phase 4a:**
- Add corrector gate with D+B anchor after Phase 3, before Phase 4b:
  - Corrector dispatched → `Read(plans/<job>/reports/review.md)` — structural proof corrector produced output
  - Corrector skipped → `Write` justification to `plans/<job>/reports/review-skip.md` — auditable skip
- Both branches require tool call on `plans/<job>/reports/`. Neither is skippable.
- The escape hatch exists but is gated: skipping requires producing an artifact that deliverable-review audits.

**triage-feedback.sh:**
- Add review artifact existence check: if neither `reports/review.md` nor `reports/review-skip.md` exists, emit signal (not blocker — Tier 1 work may legitimately skip corrector before this convention existed)
- Signal format: `"WARNING: No corrector report — review gate may have been bypassed"`

### Design Rationale

- **Why keep escape hatch:** Some work genuinely doesn't need corrector (trivial session.md-only edits, plan artifact cleanup). Forcing corrector universally adds cost with no benefit for these cases.
- **Why gate the skip:** The bootstrap-tag-support skip was unauthorized — no documented escape hatch exists. But banning skips entirely creates an incentive to produce hollow corrector dispatches. Gating with a Write creates an auditable trail: the skip justification must be specific enough to survive deliverable-review scrutiny.
- **Why defense-in-depth via triage-feedback.sh:** The D+B anchor prevents the behavioral skip in the skill. The script check catches cases where the skill itself is modified or the anchor is circumvented.

## Classification Hint

Agentic-prose edit (/inline SKILL.md) + script edit (triage-feedback.sh). Opus for skill, sonnet for script. Small scope — 2 files, well-specified from discussion. Single /inline execution.

## Dependencies

None. Independent of runbook-quality-directives batch.
