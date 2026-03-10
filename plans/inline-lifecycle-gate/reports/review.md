# Review: Inline lifecycle gate — Phase 4a corrector gate + triage-feedback.sh

**Scope**: agent-core/skills/inline/SKILL.md (Phase 4a) and agent-core/bin/triage-feedback.sh
**Date**: 2026-03-10
**Mode**: review + fix

## Summary

Two files changed: SKILL.md gains a structured Phase 4a corrector gate with D+B anchor enforcing both dispatch and skip paths via mandatory tool calls, and triage-feedback.sh gains a review artifact existence check emitting a WARNING signal. Both changes closely match the brief specification. One minor issue was found and fixed: the WARNING output is emitted after `## Verdict` but before the triage divergence message, causing inconsistent output ordering relative to other conditional signals.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **WARNING signal emitted before triage divergence message — inconsistent output ordering**
   - Location: agent-core/bin/triage-feedback.sh:73-81
   - Note: The WARNING block (lines 73-76) is placed between `## Verdict` output and the triage divergence message (lines 78-81). Both are conditional appends to the verdict section. Placing WARNING before the divergence message means a reader scanning the output sees an interrupt before the triage detail, while a skip+underclassified execution produces interleaved signals. Placing WARNING after divergence keeps all verdict-extensions together and matches the logical reading order: verdict → triage detail → meta-signal about gate bypass.
   - **Status**: FIXED

## Fixes Applied

- agent-core/bin/triage-feedback.sh:73-81 — Moved WARNING block to after the triage divergence message block, so all verdict extensions appear in logical order (verdict → triage detail → gate bypass warning).

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| SKILL.md Phase 4a: corrector dispatch path requires Read of review.md as structural proof | Satisfied | SKILL.md:140-146 — explicit `Read(plans/<job>/reports/review.md)` with prose explaining the proof semantics |
| SKILL.md Phase 4a: corrector skip path requires Write to review-skip.md | Satisfied | SKILL.md:150-160 — `Write(plans/<job>/reports/review-skip.md)` with content requirements and explicit non-valid justifications |
| Both paths require tool call on reports directory, neither is skippable | Satisfied | SKILL.md:124 — "Both paths require a tool call on `plans/<job>/reports/`. Neither is skippable." as the section opener |
| Skip justification specific enough to prevent rationalized skips | Satisfied | SKILL.md:158,160 — content requirements listed, explicit invalid examples ("Scope is small", "well-tested") |
| triage-feedback.sh: emit WARNING if neither review.md nor review-skip.md exists | Satisfied | triage-feedback.sh:55-76 — check implemented, signal matches brief exactly |
| triage-feedback.sh check is warning (not blocker) | Satisfied | Script continues to exit 0 after WARNING output |
| Review artifact reflected in Evidence section | Satisfied | triage-feedback.sh:68 — `- Review artifact: $review_artifact` |

---

## Positive Observations

- The D+B anchor pattern is correctly implemented: Path A uses Read (not just prose assertion), Path B uses Write (produces an artifact rather than logging a decision). Both require observable side effects.
- "Skip is not confidence-gated" with explicit invalid examples ("Scope is small", "well-tested") directly addresses the bootstrap-tag-support failure mode documented in the brief.
- `reports_dir` variable reuse in the review artifact check is consistent with the existing pattern — no re-derivation.
- WARNING message matches brief specification exactly: `"WARNING: No corrector report — review gate may have been bypassed"`.
- triage-feedback.sh exit 0 preserved — the check is genuinely defense-in-depth, not a new blocker.
