# Outline Review: Runbook Quality Gates

**Artifact**: plans/runbook-quality-gates/outline.md
**Date**: 2026-02-16
**Mode**: review + fix-all

## Summary

The outline demonstrates solid technical understanding and appropriate solution architecture. All functional requirements are addressed with clear implementation approaches. The design correctly partitions script-based validation (FR-3, FR-5, FR-4 structural) from agent-based optimization (FR-1, FR-2) and semantic analysis (FR-4 semantic). Pipeline integration points are well-defined.

Minor issues found: one FR partially addressed (FR-4 semantic agent integration vague), one requirements gap (NFR-2 incremental adoption mechanism not explicit), and several clarity improvements needed in script architecture section.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Phase 1.5, Architecture § Phase 1.5 | Complete | Consolidation patterns enumerated, delegation specified |
| FR-2 | Phase 1.5, Architecture § Phase 1.5 | Complete | Model review rules + opus delegation |
| FR-3 | Phase 3.5, Architecture § Phase 3.5 Scripts | Complete | File lifecycle validation in validate-runbook.py |
| FR-4 | Phase 3.5, Architecture § Phase 3.5 Scripts + Optional Agent | Partial | Structural checks detailed, semantic agent integration vague |
| FR-5 | Phase 3.5, Architecture § Phase 3.5 Scripts | Complete | Test count reconciliation detailed |
| FR-6 | Architecture § Scaling | Complete | Scaling table with size thresholds |
| NFR-1 | Approach § gate points, Architecture § Integration | Complete | Insertion points Phase 1.5 and 3.5 specified |
| NFR-2 | — | Missing | No explicit mechanism for incremental adoption |
| C-1 | Architecture § Phase 3.5 Scripts | Complete | Read-only analysis stated |
| C-2 | Key Decisions D-1, D-4 | Complete | Script vs agent boundary, reuse existing infrastructure |

**Traceability Assessment**: All requirements covered except NFR-2 (incremental adoption mechanism). FR-4 semantic agent integration needs elaboration.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **NFR-2 incremental adoption mechanism not specified**
   - Location: Out of Scope section (should be in Architecture)
   - Problem: NFR-2 states "each FR can be implemented independently" and "skills degrade gracefully when checks unavailable," but outline doesn't specify HOW this works. Are checks optional flags? Do scripts fail gracefully when missing dependencies? No implementation approach provided.
   - Fix: Added Architecture § Incremental Adoption section
   - **Status**: FIXED

2. **FR-4 semantic agent integration vague**
   - Location: Architecture § Phase 3.5, "Optional agent (FR-4 semantic extension)"
   - Problem: States "only triggered for large runbooks (FR-6) or when structural check finds ambiguous cases" but doesn't specify: (1) what are "ambiguous cases"? (2) how does the script signal ambiguity? (3) what's the delegation prompt structure? Contrast with Phase 1.5 agent delegation which is well-specified.
   - Fix: Expanded Phase 3.5 agent delegation section with exit code signaling and delegation prompt structure
   - **Status**: FIXED

### Minor Issues

1. **Scaling table doesn't match text description**
   - Location: Architecture § Scaling, table row "Large"
   - Problem: Table says "Optional per-phase delegation" for Phase 3.5 Agent. Text below says "Agent delegation scales with runbook complexity, not size" — but table shows it scales with SIZE (>3 phases or >15 items). Inconsistent.
   - Fix: Clarified rationale — size is proxy for complexity, agent delegation optional regardless
   - **Status**: FIXED

2. **Script name mismatch with architectural artifact policy**
   - Location: Architecture § Phase 3.5 Scripts, script name `validate-runbook.py`
   - Problem: Script placed in `agent-core/bin/` but subcommand interface (lifecycle/test-counts/red-plausibility) implies this is a user-facing CLI tool. Should follow CLI naming conventions from agents/decisions/cli.md if user-facing, or stay as internal script if orchestrator-only.
   - Fix: Added clarification that this is orchestrator-invoked (not user CLI), internal tooling
   - **Status**: FIXED

3. **Pipeline contracts update location unclear**
   - Location: Architecture § Integration into /runbook Skill, "Pipeline contracts update" bullet
   - Problem: Says "Add T2.5 (Phase files → Simplified phase files)" but doesn't specify WHERE in pipeline-contracts.md this goes. Existing transformations are T1-T6 in a specific table structure.
   - Fix: Added location reference (transformation table, between T2 and T3)
   - **Status**: FIXED

4. **Test strategy doesn't address agent-based checks**
   - Location: Implementation Notes § Test strategy
   - Problem: Says "Agent-based checks (FR-1, FR-2) validated via acceptance criteria on workwoods-scale runbook" but doesn't specify WHO validates (manual user check? orchestrator verification step? automated test harness?). Scripts get unit tests, but agent checks have no clear verification mechanism beyond "run on workwoods."
   - Fix: Clarified acceptance validation is manual inspection against FR-1 acceptance criteria
   - **Status**: FIXED

5. **References list incomplete**
   - Location: References section
   - Problem: Missing reference to runbook skill SKILL.md (primary integration target mentioned in Architecture § Integration). Skill dependencies in requirements.md say "Load runbook skill SKILL.md before design."
   - Fix: Added runbook skill SKILL.md to references
   - **Status**: FIXED

## Fixes Applied

- Architecture § Incremental Adoption — Added new section explaining skip conditions, --skip-* flags, exit code handling
- Architecture § Phase 3.5, Optional agent — Expanded with ambiguity detection (exit code 2), delegation prompt structure, and output format
- Architecture § Scaling, rationale — Clarified size as complexity proxy, agent delegation always optional
- Architecture § Phase 3.5 Scripts — Added note that validate-runbook.py is orchestrator-invoked internal tooling
- Architecture § Integration, pipeline contracts — Added location reference (transformation table between T2 and T3)
- Implementation Notes § Test strategy — Clarified agent-based check acceptance validation is manual inspection
- References — Added `agent-core/skills/runbook/SKILL.md` entry

## Positive Observations

- **Clear partitioning**: Script vs agent boundary (D-1) is well-reasoned and matches constraint C-2
- **Appropriate insertion points**: Phase 1.5 and 3.5 slot cleanly into existing pipeline without breaking current flow
- **Sound consolidation patterns**: FR-1 consolidation patterns (identical-pattern, independent functions, sequential additions) match the learnings from workwoods optimization
- **Realistic scaling**: FR-6 scaling approach matches deliverable-review pattern (single agent for small, delegation for large)
- **Implementation type awareness**: Notes section correctly classifies Phase 1.5 agent as general, validation scripts as general, and SKILL.md edits as opus-required architectural artifacts

## Recommendations

- During implementation: Verify validate-runbook.py subcommand interface against existing bin/ scripts (consistent flag patterns, output format, error codes)
- During Phase B discussion: Confirm NFR-2 incremental adoption mechanism (--skip-* flags vs skip conditions in skill logic vs graceful degradation in scripts)
- During Phase B discussion: Confirm FR-4 semantic agent optional delegation (always skip for small runbooks? or always run structural + skip semantic?)
- Consider: Should validation script failures block progression to Phase 4, or just emit warnings? Current outline implies blocking (exit 1), but NFR-2 incremental adoption suggests some checks might be advisory.

---

**Ready for user presentation**: Yes
