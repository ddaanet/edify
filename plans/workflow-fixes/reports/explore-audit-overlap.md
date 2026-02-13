# Workflow Skills Audit: Scope and Overlaps with Target Artifacts

**Date:** 2026-02-12
**Source:** `/Users/david/code/claudeutils-wt/worktree/plans/workflow-skills-audit/`
**Plan Status:** Designed (audit.md completed, vet review complete, 12 findings addressed)

---

## Summary

The workflow-skills-audit plan is a comprehensive analysis of planning and design skills in the agent-core framework. It covers two major components: (1) alignment between plan-adhoc and plan-tdd skills, and (2) audit of the design skill. The audit produced 12 prioritized action items, of which 7 have been implemented and vetted. Significant overlaps exist with plan-adhoc, plan-tdd, design skill, and the downstream review agents (tdd-plan-reviewer, vet-fix-agent, runbook-outline-review-agent).

---

## What the Workflow-Skills-Audit Plan Covers

### Scope (From audit.md)

The audit examines:

1. **Part 1: Alignment of plan-adhoc with plan-tdd**
   - Structural comparison (frontmatter, tier assessment, discovery patterns, outline/expansion/review flow)
   - Gaps in plan-adhoc that exist in plan-tdd (consolidation gates, complexity checks, checkpoints section)
   - Conflict: plan-adhoc manual assembly vs plan-tdd deference to prepare-runbook.py
   - 7 specific changes recommended for plan-adhoc

2. **Part 2: Design Skill Audit**
   - Complexity triage correctness
   - Checkpoint commit placement before design-vet-agent
   - Phase C numbering gap (missing C.2)
   - design-vet-agent fix-all pattern compliance
   - Session state check enforcement
   - Delegation pattern quality assessment

### Status (From jobs.md)

- **Current Status:** `designed`
- **Metadata:** "plan-adhoc alignment + design skill audit, 12 items"

### Completed Work (From vet review report)

The audit recommendations have been partially implemented:

- **7 changes to plan-adhoc SKILL.md have been applied and vetted:**
  1. Fix assembly contradiction (Point 2) — manual concatenation removed, deferred to prepare-runbook.py
  2. Add consolidation gate after outline (Point 0.85)
  3. Add complexity check before expansion (Point 0.9)
  4. Add consolidation gate after assembly (Point 2.5)
  5. Add checkpoints section
  6. Reword design skill C.4 (design-vet-agent fix-all pattern)
  7. Align plan-adhoc frontmatter (name, model, requires, outputs)

- **Vet review status:** "Ready" with all critical/major issues fixed (5 fixes applied, 3 items verified correct)

---

## Artifacts Mentioned in Audit and Their Relationship

| Artifact | Role in Audit | Scope of Overlap |
|----------|---------------|------------------|
| **plan-adhoc** | Primary subject (Part 1) | Complete skill rewrite; consolidation gates, complexity check, checkpoints added; assembly contradiction fixed |
| **plan-tdd** | Source of patterns for porting | Patterns audited for applicability to plan-adhoc; 7 changes ported from plan-tdd to plan-adhoc |
| **design skill** | Primary subject (Part 2) | Checkpoint commit placement (C.2), fix-all pattern wording (C.4), phase numbering |
| **tdd-plan-reviewer** | Referenced in audit | Plan-tdd uses tdd-plan-reviewer for per-phase review; plan-adhoc uses vet-agent (intentional difference documented) |
| **vet-fix-agent** | Referenced in audit | design skill C.3-C.4 invokes design-vet-agent (related agent); audit clarifies fix-all pattern application |
| **runbook-outline-review-agent** | Referenced in audit | Both plan-tdd and plan-adhoc use this agent for outline review at checkpoint (aligned) |
| **vet skill** | Indirectly referenced | Plan-adhoc Tier 1/2/3 assessment mentions delegating to "vet agent"; unclear if vet-fix-agent or separate vet skill |
| **plugin-dev:skill-development** | Tangentially mentioned | Design skill A.0 mentions loading plugin-dev skills as dependency; not subject of audit |
| **plugin-dev:agent-development** | Tangentially mentioned | Same as above |

---

## Detailed Overlaps with Target Artifacts

### 1. plan-adhoc ↔ plan-tdd Alignment

**Overlap Magnitude:** Very High (complete alignment study)

**What the audit covers:**
- Structural comparison table showing 27 aspects
- Identified 3 HIGH-priority gaps (consolidation gate outline, complexity check, assembly contradiction)
- Identified 2 MEDIUM-priority gaps (consolidation gate runbook, checkpoints section)
- Identified 3 LOW-priority gaps (frontmatter, reference files, complexity context passing)
- Identified intentional divergences (TDD-specific features should NOT be ported)

**Status:**
- 7 out of 12 total findings from audit have been implemented in plan-adhoc
- Implementation was vetted by vet-fix-agent; all fixes applied
- Remaining items (design skill audit findings) not yet implemented

**Key conflicts resolved:**
- **Assembly contradiction (HIGH):** plan-adhoc manual concatenation contradicted learnings.md decision "Manual runbook assembly bypasses automation." Fix: removed manual assembly, defer to prepare-runbook.py.
- **Missing consolidation gates (HIGH):** plan-adhoc lacked Phase 1.6 outline-level and Phase 4.5 runbook-level consolidation patterns. Both ported from plan-tdd.

**Outstanding items from audit:**
- design skill checkpoint commit (C.2) not yet implemented
- design skill C.4 wording clarification not yet implemented

---

### 2. design skill Audit Findings

**Overlap Magnitude:** High (7 of 12 audit items apply to design skill)

**What the audit covers:**
- Finding 1 (HIGH): Missing checkpoint commit before design-vet-agent (C.2 gap)
- Finding 2 (OK): Complexity triage correctly implemented
- Finding 3 (LOW): Session state check not enforced (prose gate skipping risk)
- Finding 4-5 (OK): A.2 delegation pattern and outline-review-agent validated
- Finding 6 (LOW): Phase C numbering gap (C.2 can fill it)
- Finding 7 (OK): design-vet-agent fix-all pattern recognized, needs C.4 rewording

**Status:**
- Audit completed and documented
- 1 issue confirmed as "ready" (vet review of plan-adhoc changes implies design implications checked)
- 5 design skill findings remain unadressed (numbered 1, 3, 6, 7 above + C.4 wording)

**Critical finding:**
- **Finding 1 (HIGH):** Design documents are created at C.1 but not committed before vet review at C.3. This conflates the designer's original output with vet-applied fixes in git history. Recommendation: Add C.2 checkpoint commit with tool call (not prose gate).

---

### 3. tdd-plan-reviewer Agent

**Overlap Magnitude:** Low (referenced but not modified)

**What the audit covers:**
- Audit table row 22: "phase-by-phase expansion: plan-tdd uses tdd-plan-reviewer (fix-all)"
- Audit marks this as "Aligned (different reviewer)" since plan-adhoc uses vet-agent instead
- This is documented as intentional divergence: TDD-specific anti-pattern detection vs general-purpose vet

**Status:**
- tdd-plan-reviewer is not a target artifact for modification
- Audit validates its use in plan-tdd; no overlap with audit fixes

---

### 4. vet-fix-agent

**Overlap Magnitude:** Medium (referenced in design skill context, agent definition referenced)

**What the audit covers:**
- Audit Part 2, Finding 7: design-vet-agent fix-all pattern clarification needed in design skill C.4
- Current C.4 wording implies caller re-fixes; should reflect that design-vet-agent applies all fixes
- Audit recommends rewording C.4 to distinguish between: "check for ESCALATION" vs "verify satisfaction with applied fixes"

**Status:**
- vet-fix-agent definition reviewed; fix-all pattern confirmed
- design skill C.4 wording not yet updated per audit recommendation
- Audit discovered design-vet-agent and vet-fix-agent are different agents (design docs vs implementation); audit only addresses design-vet-agent

---

### 5. runbook-outline-review-agent

**Overlap Magnitude:** Low (validation only, no changes)

**What the audit covers:**
- Audit table row 19: "Outline review agent: runbook-outline-review-agent (fix-all)" aligned in both plan-tdd and plan-adhoc
- Audit Finding 5 (OK): outline-review-agent confirmed to exist at `/Users/david/code/claudeutils/agent-core/agents/outline-review-agent.md`
- Note: separate runbook-outline-review-agent.md also exists (for planning skills)

**Status:**
- Agent is validated as present and correctly integrated in both skills
- No changes needed
- Audit confirms it's called at checkpoint (A.6 in design, Point 0.75 in both planning skills)

---

### 6. vet skill

**Overlap Magnitude:** Low (indirectly referenced)

**What the audit covers:**
- plan-adhoc Tier 1 sequence mentions "Delegate to vet agent for review"
- Unclear reference: is this vet-fix-agent or a separate "vet skill"?
- Audit does not clarify this distinction

**Status:**
- No audit findings specific to vet skill
- Could be clarification opportunity if vet skill is indeed a separate artifact

---

### 7. plugin-dev:skill-development and plugin-dev:agent-development

**Overlap Magnitude:** Very Low (tangential reference only)

**What the audit covers:**
- design skill A.0 (Requirements Checkpoint) mentions loading plugin-dev skills as dependency
- Audit Part 2, Finding 3: Recommends making session state check concrete (prose gate issue)
- Audit does not evaluate plugin-dev skills themselves

**Status:**
- Not primary subjects of audit
- Referenced in design skill context only
- No changes recommended to plugin-dev skills

---

## Cross-Cutting Observations

### Pattern: Consolidation Gates (Newly Ported)

The audit identified that plan-tdd has two consolidation gates:
1. **Phase 1.6** (after outline) — merges trivial phases with adjacent complexity before expensive expansion
2. **Phase 4.5** (after assembly) — catches trivial steps that weren't visible at outline level

Both were ported to plan-adhoc as Points 0.85 and 2.5. This is a cross-artifact pattern that should be validated in:
- **design skill:** Does outline phase need consolidation gate? (Design generates outline at A.5, but design documents typically are monolithic, not phase-grouped. Not applicable.)
- **orchestrate skill:** Does orchestration handle merged steps correctly? (Should verify orchestrator_plan respects consolidated step boundaries.)

### Pattern: Checkpoint Commits

Both plan-tdd and plan-adhoc emphasize checkpoints at phase boundaries. Design skill currently missing explicit checkpoint commit before vet review (C.2 gap). Audit recommends:
- design skill: Add C.2 checkpoint commit (preserve pre-vet output)
- design skill: Fix prose gate skipping risk by including tool call, not prose-only gate

### Pattern: Fix-All Agents

Audit clarifies that design-vet-agent applies ALL fixes (critical, major, minor), not just critical/major. The downstream caller's role is:
- Check for ESCALATION (UNFIXABLE issues)
- Verify satisfaction with applied fixes (optional re-review)
- NOT re-apply fixes (agent already did it)

This pattern is documented in learnings.md ("Review Agent Fix-All Pattern") and should be applied consistently across all fix-all agents:
- design-vet-agent (design documents)
- vet-fix-agent (implementation code)
- tdd-plan-reviewer (TDD runbook cycles)

### Gap: skill dependency scan in plan-adhoc

Design skill A.0 includes "Skill dependency scan" to load plugin-dev skills early. Audit recommends:
- plan-adhoc should consider similar pattern if it creates agents/skills/hooks
- Currently plan-adhoc does not include this; LOW priority per audit

---

## Pending Implementation (From audit.md Prioritized Items)

### HIGH Priority (3 items — 1 done, 2 pending)

| Item | Target Artifact | Status | Location |
|------|-----------------|--------|----------|
| Fix assembly contradiction | plan-adhoc | ✓ DONE | Point 2 |
| Add consolidation gate (outline) | plan-adhoc | ✓ DONE | Point 0.85 |
| Add complexity check | plan-adhoc | ✓ DONE | Point 0.9 |
| **Add checkpoint commit before vet** | **design skill** | **PENDING** | **C.2 (insert between C.1 and C.3)** |

### MEDIUM Priority (2 items — 1 done, 1 pending)

| Item | Target Artifact | Status | Location |
|------|-----------------|--------|----------|
| Add consolidation gate (assembly) | plan-adhoc | ✓ DONE | Point 2.5 |
| Add checkpoints section | plan-adhoc | ✓ DONE | New section |
| **Reword design skill C.4** | **design skill** | **PENDING** | **C.4 (clarify fix-all pattern)** |

### LOW Priority (5 items — 1 done, 4 pending)

| Item | Target Artifact | Status |
|------|-----------------|--------|
| Align plan-adhoc frontmatter | plan-adhoc | ✓ DONE |
| Add reference files | plan-adhoc | PENDING (recommended deferral) |
| Pass complexity context | design → plan-adhoc | PENDING |
| Make session state check concrete | design skill | PENDING |
| Design skill C.6 numbering | design skill | PENDING (low impact) |

---

## Overlaps Summary Table

| Artifact | Audit Coverage | Changes Made | Changes Pending | Validation Status |
|----------|-----------------|---------------|------------------|-------------------|
| plan-adhoc | Complete (Part 1) | 7/7 changes implemented | None | Vetted, Ready |
| plan-tdd | Source patterns (no changes) | N/A | N/A | Patterns validated |
| design skill | Partial (Part 2) | 0/4 changes | Checkpoint (C.2), C.4 wording, session check, phase numbering | Findings documented |
| tdd-plan-reviewer | Referenced (validation only) | None | None | Validated present/correct |
| vet-fix-agent | Referenced (pattern clarity) | None | C.4 wording depends on this pattern | Pattern documented |
| runbook-outline-review-agent | Referenced (validation) | None | None | Confirmed present/aligned |
| vet skill | Indirect reference | None | Clarification needed | No changes recommended |
| plugin-dev:* | Indirect reference | None | Dependency scan for plan-adhoc (LOW) | Not primary subject |

---

## Recommendations for Workflow-Fixes Plan

1. **Immediate (Blocking):**
   - Implement design skill C.2 checkpoint commit (prevents conflating designer output with vet fixes in git history)
   - Reword design skill C.4 to clarify fix-all pattern (needed for correct downstream agent usage)

2. **High Priority (Quality):**
   - Verify orchestrate skill handles merged steps correctly (consolidation gates in plan-adhoc)
   - Validate prepare-runbook.py works with consolidated runbook structure

3. **Medium Priority (Clarity):**
   - Make design skill session state check concrete (add tool call to prevent prose gate skipping)
   - Clarify plan-adhoc "vet agent" reference (vet-fix-agent vs vet skill?)

4. **Low Priority (Enhancement):**
   - Add plan-adhoc reference files (error-handling.md, examples.md)
   - Consider plan-adhoc skill dependency scan pattern (parallel to design skill A.0)
   - Pass complexity context from design to plan-adhoc (avoid redundant re-assessment)

---

## File Locations (Absolute Paths)

- Audit report: `/Users/david/code/claudeutils-wt/worktree/plans/workflow-skills-audit/audit.md`
- Vet review: `/Users/david/code/claudeutils-wt/worktree/plans/workflow-skills-audit/reports/plan-adhoc-vet-review.md`
- plan-adhoc skill: `/Users/david/code/claudeutils-wt/worktree/agent-core/skills/plan-adhoc/SKILL.md`
- plan-tdd skill: `/Users/david/code/claudeutils-wt/worktree/agent-core/skills/plan-tdd/SKILL.md`
- design skill: `/Users/david/code/claudeutils-wt/worktree/agent-core/skills/design/SKILL.md`
- tdd-plan-reviewer: `/Users/david/code/claudeutils-wt/worktree/agent-core/agents/tdd-plan-reviewer.md`
- vet-fix-agent: `/Users/david/code/claudeutils-wt/worktree/agent-core/agents/vet-fix-agent.md`
- runbook-outline-review-agent: `/Users/david/code/claudeutils-wt/worktree/agent-core/agents/runbook-outline-review-agent.md`
