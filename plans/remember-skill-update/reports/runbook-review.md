# Runbook Review: remember-skill-update

**Artifact**: plans/remember-skill-update/runbook.md
**Date**: 2026-02-23T00:00:00-08:00
**Mode**: review + fix-all
**Phase types**: Mixed (2 TDD: Phases 1, 4; 3 general: Phases 2, 3, 6; 2 inline: Phases 5, 7)

## Summary

The runbook was promoted from a sufficiency-checked outline with 7 phases covering all 13 active FRs. Review identified four fixable issues: a Total Steps count that omitted Step 3.1 from the breakdown, FR-6 missing from the Requirements Mapping table, a deferred decision in Cycle 1.3 GREEN, and a conditional in Cycle 4.1 GREEN that was unresolved. One advisory finding flagged sonnet assignment on skill file edits in Phase 6 with an added justification note. All issues are fixed.

**Overall Assessment**: Ready

---

## Findings

### Critical Issues

None.

### Major Issues

1. **Total Steps metadata count incorrect — Step 3.1 omitted from breakdown**
   - Location: Weak Orchestrator Metadata, line 18
   - Problem: "15 (6 TDD cycles + 5 general steps + 2 inline phases + 2 general steps)" sums to 15 but the actual item count is 16: Cycles 1.1-1.3, 4.1-4.3 (6 TDD) + Steps 2.1-2.5, 3.1, 6.1-6.2 (8 total, not 7) + Phase 5, Phase 7 (2 inline) = 16. The breakdown "5 general steps + 2 general steps" = 7 general steps total, but lists them split awkwardly and omits Step 3.1 from the count.
   - Fix: Updated to "16 (6 TDD cycles + 6 general steps + 2 inline phases)"
   - **Status**: FIXED

2. **FR-6 missing from Requirements Mapping table**
   - Location: Common Context, Requirements Mapping table
   - Problem: FR-6 (Frozen-domain recall analysis) is listed in requirements.md but has no row in the runbook's Requirements Mapping table. Phase 7 covers FR-6 per the outline's mapping table. Missing row leaves FR-6 coverage unverifiable.
   - Fix: Added row `| FR-6 | 7 | Phase 7 inline |`
   - **Status**: FIXED

3. **Cycle 1.3 GREEN contains deferred decision**
   - Location: Phase 1, Cycle 1.3, GREEN phase
   - Problem: "Adjust implementation if any edge case isn't handled" — this is a deferred decision ("adjust if..."). An executor cannot verify completion unambiguously. The TDD test plan's own analysis resolves this: the logic from Cycles 1.1-1.2 is complete and no additional implementation is needed.
   - Fix: Replaced with "No implementation change required. Cycles 1.1-1.2 implement complete logic: prefix check rejects anything not starting with `When ` or `How to ` (covers `How encode`), content-word check covers all prefix-passing titles. Verify all 12 tests pass with no code changes."
   - **Status**: FIXED

4. **Cycle 4.1 GREEN contains unresolved conditional for when-resolve.py**
   - Location: Phase 4, Cycle 4.1, GREEN phase
   - Problem: "Update `agent-core/bin/when-resolve.py` if entry point args change" — the "if" condition defers the decision to execution time. Reading the file confirms: `when-resolve.py` is a thin wrapper that calls `when_cmd()` directly; Click handles all arg parsing. No code changes are needed. The docstring comment needs updating but that is deterministic.
   - Fix: Replaced conditional with concrete instruction: update docstring comment to new invocation format, no code change needed, with rationale.
   - **Status**: FIXED

### Minor Issues

5. **Phase 6 model assignment (advisory) — sonnet for skill file edits without justification**
   - Location: Phase 6 header / Execution Model
   - Problem: Advisory rule flags skill file edits assigned below opus. Phase 6 touches `agent-core/skills/remember/SKILL.md` (rename + all references). However, this phase is purely mechanical text substitution with no semantic content changes — the skill's behavioral guidance is unaffected. Sonnet is appropriate here, but the rationale was not stated.
   - Fix: Added inline note: "Advisory: artifact-type override rule recommends opus for skill file edits, but this phase is pure text substitution with no semantic content changes — sonnet assignment is appropriate exception."
   - **Status**: FIXED

---

## Fixes Applied

- Metadata (line 18): Total Steps corrected from 15 to 16; breakdown updated to "6 TDD cycles + 6 general steps + 2 inline phases"
- Requirements Mapping table: Added FR-6 row mapping to Phase 7 inline
- Cycle 1.3 GREEN: Replaced deferred "adjust if..." with concrete "no change required" + rationale
- Cycle 4.1 GREEN: Replaced conditional when-resolve.py update with concrete docstring-only update + no-code-change justification
- Phase 6 description: Added advisory note explaining sonnet exception for mechanical rename

---

## Outline Review Note

Outline review report exists at `plans/remember-skill-update/reports/outline-review.md` (naming convention: `outline-review.md` vs expected `runbook-outline-review.md`). Content confirms the outline was reviewed. No action needed.

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
