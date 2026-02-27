# Outline Review: Inline Execution Lifecycle Skill

**Artifact**: plans/triage-feedback/outline.md
**Date**: 2026-02-27
**Mode**: review + fix-all

## Summary

Solid outline with clear decisions, rationale for each, and correct scope boundaries. The original lacked a workflow sequence section (decisions were documented but the execution flow connecting them was implicit) and had gaps in corrector scope clarity and constraint coverage. All issues fixed — outline is ready for user presentation.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-3 | Complete | Classification persistence stays in /design Phase 0 |
| FR-2 | D-1, Workflow Phase 2 | Complete | Cold-start steps now enumerated explicitly |
| FR-3 | Workflow Phase 3 | Complete | By design: lifecycle wrapper, not implementation prescriber |
| FR-4 | D-4, Workflow Phase 4a | Complete | Corrector scope constraint added |
| FR-5 | D-2, Workflow Phase 4b | Complete | Deterministic script per recall entry |
| FR-6 | D-2, Workflow Phase 4b | Complete | Comparison in same script |
| FR-7 | D-2 script interface | Complete | Log append in script output |
| FR-8 | D-5, Workflow Phase 4c | Complete | Handoff continuation mechanism |
| FR-9 | Integration Points table | Complete | /design Phase B + C.5 routes |
| FR-10 | Integration Points table | Complete | /runbook Tier 1 route |
| NFR-1 | Overhead budget section | Complete | ~3-4 tool calls quantified |
| NFR-2 | D-2 | Complete | Script handles deterministic operations |
| NFR-3 | D-4 | Complete | Single corrector template |
| C-1 | D-3 | Complete | Skill reads, /design writes |
| C-2 | D-3 | Complete | Verbatim block format |
| C-3 | D-2 | Complete | Initial estimates note added |
| C-4 | Scope OUT | Complete | Tier 2/3 excluded |

**Traceability Assessment**: All 17 requirements (10 FR, 3 NFR, 4 C) traced and covered.

## Recall-Informed Checks

Four failure modes from recall entries were checked against the outline:

- **"When choosing script vs agent judgment"**: D-2 correctly routes all three evidence signals and comparison heuristics to a deterministic script. No agent judgment for mechanical operations. PASS.
- **"When corrector rejects planning artifacts"**: D-4 originally lacked scope constraint. Fixed: corrector template now explicitly states "implementation changes only" with routing note for planning artifacts. PASS (after fix).
- **"When design resolves to simple execution"**: FR-9/FR-10 integration is correct. /fulfill is the execution endpoint after design resolves complexity — the skill doesn't re-assess complexity. PASS.
- **"When placing quality gates"**: Corrector dispatch (D-4) is structural, embedded in the post-work pipeline — not an ambient rule. Triage feedback (D-2) is scripted at a chokepoint. Both are structural enforcement, not ambient. PASS.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Missing workflow sequence section**
   - Location: Between Approach and Key Decisions
   - Problem: Outline documented decisions (D-1 through D-6) but lacked a linear workflow showing Phase 1 → 2 → 3 → 4 execution order. An implementer could reconstruct the flow from decisions, but it required cross-referencing multiple sections.
   - Fix: Added "Workflow Sequence" section with Phase 1 (Entry), Phase 2 (Pre-work), Phase 3 (Execute), Phase 4 (Post-work with sub-steps 4a/4b/4c), each with FR references.
   - **Status**: FIXED

2. **FR-2 cold-start path not enumerated**
   - Location: D-1 (chain detection)
   - Problem: D-1 covered the `--chain` flag mechanism but the cold-start path (what happens WITHOUT the flag) was only implied. The 4 specific steps from FR-2 (task-context.sh, brief.md, recall-artifact, lightweight recall) were not listed.
   - Fix: Phase 2 in Workflow Sequence enumerates all 4 cold-start pre-work steps with explicit FR-2 reference.
   - **Status**: FIXED

3. **Corrector dispatch scope ambiguity**
   - Location: D-4 (single corrector template)
   - Problem: Template said "uncommitted changes" without clarifying this means implementation changes only. When `/fulfill --chain` follows /design, the diff could theoretically include design artifacts. Per "when corrector rejects planning artifacts" recall entry, corrector agent rejects planning artifacts — this constraint was not reflected in the template.
   - Fix: Added "implementation changes only" constraint to template. Added note explaining baseline capture mechanism excludes design-phase artifacts from scope. Added routing note for planning artifacts (runbook-corrector).
   - **Status**: FIXED

### Minor Issues

1. **C-3 (divergence heuristics are initial estimates) not addressed**
   - Location: D-2
   - Problem: Requirements constraint C-3 explicitly states heuristics are initial estimates. Original D-2 described the heuristics as deterministic without acknowledging their provisional nature.
   - Fix: Added paragraph after D-2 description noting heuristics are initial estimates per C-3, with triage-feedback-log.md as the calibration data source.
   - **Status**: FIXED

2. **NFR-1 overhead budget not quantified**
   - Location: (missing)
   - Problem: Requirements specify "3-4 tool calls" overhead. Original outline mentioned "zero tool calls" for chain path but didn't quantify total overhead.
   - Fix: Added "Overhead budget" subsection in Workflow Sequence with specific call count breakdown.
   - **Status**: FIXED

3. **No requirements traceability section**
   - Location: (missing)
   - Problem: FR references were scattered across decisions and integration points. No single mapping showing coverage of all 17 requirements.
   - Fix: Added "Requirements Traceability" section at end with full matrix (10 FR + 3 NFR + 4 C).
   - **Status**: FIXED

4. **Risk section lacks rollback strategy**
   - Location: Risk Assessment
   - Problem: Mitigation mentioned additive changes but no rollback plan if integration edits regress existing paths.
   - Fix: Added rollback bullet noting independent revertibility of /design modifications, /runbook modifications, and new files.
   - **Status**: FIXED

## Fixes Applied

- Workflow Sequence section added (Phases 1-4 with FR references, overhead budget)
- D-2: C-3 initial estimates acknowledgment added
- D-4: Corrector scope constraint ("implementation changes only") added to template
- D-4: Baseline mechanism explanation added (excludes design artifacts)
- D-4: Planning artifact routing note added
- Risk Assessment: Rollback strategy added
- Requirements Traceability: Full 17-row matrix added

## Positive Observations

- Decisions include rationale AND rejected alternatives — good PDR practice
- D-2 correctly applies "script vs agent judgment" principle (deterministic operations scripted)
- Scope IN/OUT is explicit and well-bounded
- Integration Points table clearly maps consumers, changes, and mechanisms
- Open questions all resolved with clear answers
- Quality enforcement is structural (corrector in pipeline, scripted evidence) not ambient

## Recommendations

- **Naming decision**: `/fulfill` with `f` shortcut is well-reasoned. The naming agent's methodology (11 candidates, 3 criteria) provides good audit trail. Worth confirming with user during discussion.
- **Corrector template examples**: D-6 references `references/corrector-template.md` for "full template with examples." During implementation, ensure the examples cover both chained (post-/design) and cold-start (from session.md) scenarios since the corrector scope differs.
- **Triage-feedback.sh testing**: The script is the most testable artifact. Consider writing the script with test cases before the skill prose — the script interface is fully specified (D-2).

---

**Ready for user presentation**: Yes
