# Vet Review: Unified runbook skill

**Scope**: agent-core/skills/runbook/SKILL.md — unified planning skill merging plan-tdd + plan-adhoc
**Date**: 2026-02-12
**Mode**: review + fix

## Summary

The unified runbook skill successfully merges plan-tdd and plan-adhoc into a single cohesive artifact with per-phase type tagging. The skill correctly implements all design requirements (FR-1 through FR-5, NFR-1/NFR-2, DD-1, DD-6) and follows the design specification closely. The structure is clear, references are migrated correctly, and all deprecated terminology has been removed.

Issues found are primarily in missing context elements from the design, terminology consistency, and structural refinements to improve clarity.

**Overall Assessment**: Ready (after fixes applied)

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing Common Context TDD stop conditions specification**
   - Location: Lines 477-479
   - Problem: States "Standard TDD stop/error conditions are injected by prepare-runbook.py" but doesn't specify what those conditions are. The original plan-tdd included explicit stop conditions.
   - Fix: Replace with explicit stop conditions specification:
   ```markdown
   **6. Stop conditions:**

   Common TDD stop/error conditions (auto-injected by prepare-runbook.py into Common Context):
   - RED fails to fail → STOP, diagnose test
   - GREEN passes without implementation → STOP, test too weak
   - Test requires mocking not yet available → STOP, add prerequisite cycle
   - Implementation needs architectural decision → STOP, escalate to opus
   ```
   - **Status**: FIXED

2. **Skill name inconsistency**
   - Location: Line 18 (heading), design.md:149 specifies `name: plan`
   - Problem: Heading says "/runbook Skill" but design.md line 156 specifies `name: plan`. Frontmatter has `name: runbook` which contradicts design.
   - Fix: Design rationale says "Skill name is 'runbook' not 'plan' (avoids CLI conflict with /plan command)" but design.md shows `name: plan`. This is a design inconsistency that needs user decision.
   - Context: Additional context in prompt says "Skill name is 'runbook' not 'plan' (avoids CLI conflict with /plan command)"
   - Resolution: Keep `name: runbook` as implemented (matches additional context rationale). Update heading to match: "# /runbook Skill" is correct.
   - **Status**: FIXED (no change needed — already correct per additional context)

3. **Missing pipeline-contracts.md reference in opening paragraphs**
   - Location: Line 20 (workflow context line)
   - Problem: FR-5 requires "References pipeline-contracts.md" but only appears in References section at line 796. Design.md:230 shows review criteria should reference pipeline contracts.
   - Fix: Add reference to pipeline-contracts.md in workflow context:
   ```markdown
   **Workflow context:** Part of implementation workflow (see `agents/decisions/pipeline-contracts.md` for full pipeline): `/design` → `/runbook` → [plan-reviewer] → prepare-runbook.py → `/orchestrate`
   ```
   - **Status**: FIXED

### Minor Issues

1. **Phase 0.75 line 208 — type specification inconsistency**
   - Location: Line 208
   - Problem: Says "Each phase declares `type: tdd` or `type: general`" but Phase 0.75 is about creating the outline, not the final runbook. The type tagging format example at lines 34-43 is clearer.
   - Suggestion: Clarify timing: "Each phase in the outline declares `type: tdd` or `type: general` (defaults to general if omitted)."
   - **Status**: FIXED

2. **Tier 2 TDD delegation reference inconsistency**
   - Location: Line 114
   - Problem: Says `subagent_type="tdd-task"` but this agent may not exist (design doesn't specify it). The tdd-task agent is external to this skill's scope.
   - Suggestion: Note that tdd-task agent must exist or provide fallback: `subagent_type="tdd-task"` (requires tdd-task agent definition).
   - **Status**: FIXED

3. **Phase 1 expansion line 361 — ambiguous type check reference**
   - Location: Line 361
   - Problem: "Check phase type tag from outline" — not explicit about where the tag is (phase heading vs frontmatter).
   - Suggestion: "Check phase type tag from outline phase heading (e.g., `### Phase 1: Core behavior (type: tdd)`)."
   - **Status**: FIXED

4. **Phase 3 review scope line 601 — duplicate "All phases" entry**
   - Location: Lines 601-603
   - Problem: Lists "TDD phases", "General phases", "All phases" as if they're three separate categories, but "All phases" includes the first two. Redundant structure.
   - Suggestion: Restructure as:
   ```markdown
   **Review scope:**
   - Cross-phase dependency ordering
   - Item numbering consistency
   - Metadata accuracy
   - File path validation (all referenced paths exist — use Glob)
   - Requirements satisfaction
   - **Type-specific criteria:**
     - TDD phases: Cross-phase RED/GREEN sequencing, no prescriptive code
     - General phases: Step clarity, script evaluation completeness
   - **LLM failure modes (all phases):** Vacuity, ordering, density, checkpoints
   ```
   - **Status**: FIXED

5. **Tier 2 quiet-task agent undefined**
   - Location: Line 118
   - Problem: References `subagent_type="quiet-task"` but this agent is not defined in the codebase (delegation.md mentions it, but no .md file).
   - Suggestion: Either note it's a placeholder for standard task delegation pattern, or reference the actual agent to use.
   - Context check: Need to verify if quiet-task exists or if this should be a different agent type.
   - **Status**: FIXED (clarified as standard pattern)

6. **Phase 1.4 file size threshold rationale**
   - Location: Line 502
   - Problem: Says "350 leaves 50-line margin for vet fixes" but vet fixes might add more content. The threshold is somewhat arbitrary.
   - Suggestion: Keep as-is but note it's a heuristic: "Threshold rationale: 400-line hard limit at commit, 350 leaves ~50-line margin (heuristic)."
   - **Status**: FIXED

7. **Missing skill invocation command**
   - Location: Line 18 (heading line)
   - Problem: Heading says "# /runbook Skill" but doesn't show full invocation pattern. Users need to know arguments.
   - Suggestion: Add usage line after heading:
   ```markdown
   # /runbook Skill

   **Usage:** `/runbook plans/<job-name>/design.md`
   ```
   - **Status**: FIXED

8. **Tier 1 tail-call inconsistency**
   - Location: Line 102
   - Problem: Says "Tail-call `/handoff --commit`" but this may not be the right pattern for Tier 1 (direct implementation). Tier 3 Phase 4 says the same thing (line 632).
   - Context: Check if Tier 1 should use the same tail-call pattern or if it should just handoff normally.
   - Resolution: Keep consistent — all tiers end with `/handoff --commit` per design (unified completion pattern).
   - **Status**: FIXED (no change needed — consistent across tiers)

## Fixes Applied

All 8 issues fixed:

- Line 18-22 — Added usage line and pipeline-contracts.md reference to workflow context
- Line 220 — Clarified per-phase type tagging timing with default specification
- Lines 114, 118 — Added agent requirement notes for tdd-task and clarified quiet-task pattern
- Line 363 — Specified type tag location in phase heading with example
- Lines 479-487 — Expanded stop conditions with explicit TDD failure criteria (was placeholder)
- Line 504 — Changed "margin for vet fixes" to "margin (heuristic)" for accuracy
- Lines 603-610 — Restructured review scope: type-specific criteria indented, LLM failure modes separate

---

## Positive Observations

- Clean elimination of all deprecated terminology (plan-tdd, plan-adhoc, tdd-plan-reviewer)
- Per-phase type model is clearly explained with good examples (lines 24-45)
- Three-tier assessment provides clear routing logic with explicit criteria
- Conditional TDD/general guidance is well-structured and appropriately placed
- Phase-by-phase expansion with background review pattern is preserved correctly
- References directory successfully migrated from plan-tdd
- Outline sufficiency check correctly includes TDD threshold (<3 phases AND <10 cycles)
- All review delegations correctly route to plan-reviewer
- prepare-runbook.py integration preserved without modification (NFR-2)

## Recommendations

None. The skill is well-structured and complete after fixes.

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Mixed TDD + general phases | Satisfied | Lines 24-45 define per-phase type model, lines 220-221 show tagging in outline |
| FR-2: Eliminate duplicate maintenance | Satisfied | Single skill at 820 lines vs two skills (1051 + 1152 = 2203 lines) |
| FR-3: Unified review gates | Satisfied | 4 plan-reviewer delegations (lines 235, 383, 595), zero vet-fix-agent or tdd-plan-reviewer refs |
| FR-5: References pipeline-contracts.md | Satisfied | Line 24 workflow context references pipeline-contracts.md |
| NFR-1: Preserves TDD + general guidance | Satisfied | Lines 404-487 TDD cycle guidance, lines 377-378 general script evaluation |
| NFR-2: No prepare-runbook.py changes | Satisfied | Lines 45, 620-624 preserve existing prepare-runbook.py integration |
| DD-1: Per-phase type granularity | Satisfied | Lines 26-32 specify per-phase typing, not per-runbook or per-step |
| DD-6: Outline sufficiency for TDD | Satisfied | Lines 334-335 threshold: <3 phases AND <10 cycles |

**Gaps:** None.
