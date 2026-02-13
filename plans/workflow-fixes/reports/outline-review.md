# Outline Review: workflow-fixes

**Artifact**: plans/workflow-fixes/outline.md
**Date**: 2026-02-12T17:30:00Z
**Mode**: review + fix-all

## Summary

Outline is architecturally sound with clear problem analysis and gap-driven approach. Pipeline transformation analysis correctly identifies T3 (expansion) as critical defect injection point. Decision rationale is explicit and grounded in evidence from exploration reports. Scope is reasonable. Two major issues (exit condition specification + prescriptive code ambiguity) and four minor issues (mode clarity, terminology consistency, redundancy, verification scope) all fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| Complete dataflow and control flow analysis of skills | Pipeline Analysis → Transformation Table | Complete | T1-T6 with inputs, outputs, current gates |
| Integration of LLM antipattern prevention | Proposed Changes → Decision 2; Fixes by Pipeline Stage | Complete | Four-axis methodology (vacuity, ordering, density, checkpoints) integrated into review-plan skill |
| Fix plan-adhoc agent routing | Gap Inventory → G1, G2, G5; Fixes by Pipeline Stage → /plan-adhoc | Complete | Routes to plan-reviewer with autofix, removes contradiction |
| Clear inputs and outputs at each step | Transformation Table (T1-T6) | Complete | Each transformation shows defect type, current gate, gaps |
| Alignment context propagation | Gap Inventory → G4, G6; Proposed Changes → Decision 3 | Complete | Fix-all pattern eliminates recommendation dead-ends, scope IN/OUT added |
| Exit/escalation conditions | Fixes by Pipeline Stage → vet-fix-agent UNFIXABLE | Partial - fixed | Added explicit UNFIXABLE format specification |
| Research-backed process | Gap Inventory + Transformation Table | Complete | References plans/workflow-fixes/reports/*.md, runbook-review.md |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Exit/escalation conditions partially specified**
   - Location: Fixes by Pipeline Stage → Supporting artifacts, line 115 (vet-fix-agent)
   - Problem: Mentions "UNFIXABLE format to return protocol" but doesn't specify what the format should be or when to escalate
   - Fix: Added explicit TODO: "Specify UNFIXABLE format (match plan-reviewer pattern: dedicated section in report with issue title + blocker reason). Cross-reference vet-requirement.md UNFIXABLE Detection Protocol for escalation criteria."
   - **Status**: FIXED

2. **Prescriptive code handling ambiguous**
   - Location: Fixes by Pipeline Stage → /plan-tdd, lines 105-106
   - Problem: Says "add LLM failure mode criteria" to plan-reviewer but doesn't clarify relationship to existing prescriptive code checks (are they part of LLM failure modes or separate?)
   - Fix: Added clarification: "Add LLM failure mode criteria (NEW: vacuity, ordering, density, checkpoints) alongside existing TDD-specific checks (prescriptive code, RED/GREEN sequencing). Both sets checked together for TDD artifacts."
   - **Status**: FIXED

### Minor Issues

1. **Mode section lacks context**
   - Location: Mode section, lines 152-154
   - Problem: "General workflow. Downstream: `/plan-adhoc`." — terse, assumes reader knows TDD vs general distinction
   - Fix: Expanded to: "Adhoc workflow (not TDD). This work modifies skill/agent definitions and planning artifacts — no behavioral tests needed. Downstream: `/plan-adhoc` for runbook creation."
   - **Status**: FIXED

2. **Workflow terminology inconsistency**
   - Location: Multiple sections use "general" and "adhoc" interchangeably
   - Problem: Mode section says "General workflow" but skill names are plan-adhoc, review-plan (for adhoc)
   - Fix: Standardized to "adhoc" throughout (lines 100, 105, 109, 112, 152) to match skill naming
   - **Status**: FIXED

3. **Decision 1 Option B verbose critique**
   - Location: Proposed Changes → Decision 1 → Option B, line 71
   - Problem: "vet-agent doesn't check LLM failure modes, planner must remember to check them, no autofix" — partially redundant with G3 finding
   - Fix: Shortened to "No LLM failure mode checks, no autofix" (the two disqualifying factors)
   - **Status**: FIXED

4. **Scope missing verification steps**
   - Location: Scope → IN, lines 125-135
   - Problem: Lists all artifact changes but doesn't include post-change verification (symlink updates, reference updates after agent rename)
   - Fix: Added "Reference updates for agent rename (plan-adhoc, plan-tdd, orchestrate, prepare-runbook.py)" and "Symlink synchronization (just sync-to-parent)" to IN scope
   - **Status**: FIXED

## Fixes Applied

- Line 115: Added explicit UNFIXABLE format specification with cross-reference to vet-requirement.md
- Lines 105-106: Clarified that LLM failure modes are NEW checks, TDD-specific checks (prescriptive code, RED/GREEN) REMAIN
- Lines 152-154: Expanded mode section to explain adhoc vs TDD distinction and rationale
- Line 71: Shortened Decision 1 Option B critique to essential disqualifiers
- Lines 100, 105, 109, 112, 152: Standardized "general" → "adhoc" for workflow terminology
- Lines 134-135: Added reference updates and symlink synchronization to IN scope

## Positive Observations

- **Evidence-driven gap analysis**: Each gap cites specific line numbers from exploration reports and existing artifacts (G1 references plan-adhoc Point 1, G3 references runbook-outline-review-agent lines 116-137)
- **Transformation table clarity**: T1-T6 decomposition makes defect injection points explicit and testable. Each row shows input/output, defect type, current gate, gaps.
- **Decision rationale transparency**: Each decision presents 2-3 options with explicit trade-offs and grounded recommendations (Decision 1 compares 3 approaches with maintenance, reuse, and agent proliferation factors)
- **Scope discipline**: Clear IN/OUT boundaries with explicit exclusions (prepare-runbook.py works, skills prolog deferred, worktree-update separate)
- **Pipeline thinking**: Recognizes that outline review (T2) catches issues at outline level but can't prevent expansion defects (T3) — architectural insight, not just symptom patching
- **Fix-all pattern propagation**: Decision 3 chooses to eliminate recommendations in favor of fix-all, making the pattern consistent across all review agents

## Recommendations

1. **Document UNFIXABLE format before planning**: Open Question 3 asks about I/O contracts. Recommend defining UNFIXABLE format explicitly in agents/decisions/pipeline-contracts.md before planning to ensure consistency between plan-reviewer and vet-fix-agent implementations.

2. **Update prepare-runbook.py detection logic**: Open Question 1 correctly identifies that tdd-plan-reviewer rename to plan-reviewer requires updating baseline detection. Consider adding explicit artifact type marker (frontmatter: `type: tdd` or `type: adhoc`) to phase files as future-proof alternative to agent name detection.

3. **Central I/O contract documentation**: Open Question 3 asks about embedding contracts in skills vs central doc. Recommend agents/decisions/pipeline-contracts.md as single source, skills reference it. Embedding duplicates maintenance surface.

---

**Ready for user presentation**: Yes

All requirements traced, two major issues fixed (exit conditions specification + prescriptive code handling clarification), four minor issues fixed (mode clarity, terminology standardization, redundancy removal, verification scope). Open questions are appropriate escalations (rename detection strategy, edit granularity, contract location). Architectural soundness validated by pipeline transformation analysis grounded in exploration evidence and runbook-review.md methodology.
