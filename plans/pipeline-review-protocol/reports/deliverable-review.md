# Deliverable Review: pipeline-review-protocol

**Date:** 2026-03-09
**Methodology:** agents/decisions/deliverable-review.md
**Conformance baseline:** plans/pipeline-review-protocol/outline.md (no design.md — inline execution, outline is authoritative)

## Inventory

| Type | File | Lines changed |
|------|------|--------------|
| Agentic prose | agent-core/skills/proof/SKILL.md | +141 (new) |
| Agentic prose | agent-core/skills/design/SKILL.md | +21/-1 |
| Agentic prose | agent-core/skills/design/references/write-design.md | +6 |
| Agentic prose | agent-core/skills/design/references/write-outline.md | +6/-2 |
| Agentic prose | agent-core/skills/requirements/SKILL.md | +4/-6 |
| Agentic prose | agent-core/skills/runbook/references/tier3-outline-process.md | +2/-1 |
| Agentic prose | agent-core/skills/runbook/references/tier3-planning-process.md | +20/-5 |
| Agentic prose | agent-core/skills/review-plan/SKILL.md | +1 |
| Agentic prose | agent-core/skills/review-plan/references/review-examples.md | +4/-5 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | +1/-1 |
| Agentic prose | agent-core/skills/design/references/discussion-protocol.md | -20 (deleted) |
| Configuration | .claude/skills/proof | +1 (symlink) |

**Total:** 12 files, ~207 net lines. All agentic prose except one config symlink.

**Design conformance:** All 5 outline scope IN items addressed.

## Critical Findings

None.

## Major Findings

1. **`proof <artifact>.md` planstate not implemented**
   - Outline Approach section: "**Planstate:** `proof <artifact>.md` — plan enters this state when awaiting user validation (e.g., `proof outline.md`, `proof runbook-phase-2.md`)."
   - Outline Scope IN: "`proof <artifact>.md` planstate"
   - /proof SKILL.md contains no planstate management — no lifecycle.md entry on loop entry or exit
   - No hosting skill integration point writes planstate either
   - **Impact:** If a session ends during /proof review, plan status doesn't reflect "awaiting user validation." Cross-session state visibility gap. The `claudeutils _worktree ls` output won't show the plan is in proof state.
   - **Mitigation assessment:** /proof runs inline within a single session — the loop starts and completes atomically from the hosting skill's perspective. Planstate may be unnecessary for a transient in-session state. But the outline explicitly scopes it IN.

2. **Phase 3.25 passes glob pattern to single-artifact /proof skill**
   - `tier3-planning-process.md:444`: `Invoke /proof plans/<job>/runbook-phase-*.md`
   - /proof SKILL.md Entry section: "Read the artifact under review" — singular
   - /proof's loop mechanics (reword, accumulate, sync) are designed around one artifact's decisions
   - **Impact:** Agent executing Phase 3.25 faces ambiguous invocation — does it expand the glob and invoke /proof per-file, or pass the glob and expect /proof to handle multiple files? Neither path is specified.
   - **Outline reference:** C2 table row 5: "Post-expansion (after Phase 1/3 corrector) | runbook-phase-*.md" — the wildcard is present in the outline too, so this ambiguity originates in the design, not the implementation.

## Minor Findings

### Duplication

3. **Author-Corrector Coupling dependency table duplicated across /proof and /design**
   - Identical table at proof/SKILL.md:108-113 and design/SKILL.md:166-171
   - Outline C3: "Author-corrector coupling is a /design responsibility" — but /proof also contains the full check and table for "when /proof's hosting skill is /design"
   - Two invocation paths: /design runs coupling check during design creation, /proof runs it during validation loop. Both are reasonable.
   - Maintenance risk: table changes require two-file update. No single source of truth.

### Naming/Consistency

4. **Corrector Dispatch subagent_type inconsistency for runbook-phase-*.md**
   - proof/SKILL.md:81: `runbook-phase-*.md | runbook-corrector (/review-plan) | corrector`
   - All other dispatch table rows use the specific corrector agent name as subagent_type: `outline-corrector`, `design-corrector`, `runbook-outline-corrector`
   - The `runbook-phase-*.md` row uses generic `corrector` — different pattern from siblings
   - Functionally correct (corrector agent loads review-plan skill), but inconsistent naming

### Supplementary Changes

5. **review-plan and review-examples.md changes are in-scope extensions**
   - review-plan/SKILL.md:229 adds ImportError/AssertionError vacuity check — appropriate companion to Bootstrap pattern
   - review-examples.md updates ImportError example to Bootstrap + behavioral assertion pattern
   - Not in outline scope explicitly, but correctly coupled to author-corrector relationship (Bootstrap changes in /runbook tdd-cycle-planning.md require review-plan/corrector update)

6. **handoff/SKILL.md, runbook/SKILL.md changes are supplementary**
   - handoff/SKILL.md: note-override for command derivation — not in outline scope, appears to be a companion fix
   - runbook/SKILL.md: tdd-cycle-planning.md reference in Tier 2 planning — not in outline scope, companion to Bootstrap
   - Both are appropriate companion changes but unspecified in outline

## Gap Analysis

| Outline Scope IN | Status | Reference |
|-----------------|--------|-----------|
| `/proof` skill (replacing discussion-protocol.md) | Covered | proof/SKILL.md (+141 lines), discussion-protocol.md deleted |
| `proof <artifact>.md` planstate | **Missing** | No planstate integration in skill or hosting skills |
| Integration in /requirements (Step 5) | Covered | requirements/SKILL.md:154 |
| Integration in /design (Phase B) | Covered | write-outline.md:159 |
| Integration in /design (Post-design) | Covered | write-design.md:60 (C.4.5) |
| Integration in /runbook (Post-outline) | Covered | tier3-planning-process.md:105 |
| Integration in /runbook (Post-expansion) | Covered | tier3-planning-process.md:444 |
| Author-corrector coupling in /design | Covered | design/SKILL.md:155-173 |
| Automatic corrector dispatch after "apply" | Covered | proof/SKILL.md:72-95 |

| Outline Scope OUT | Status |
|------------------|--------|
| New corrector agents | Respected — no new agents |
| Changes to validate-runbook.py | Partially violated — +12 lines (vacuity check for ImportError) |
| Changes to prepare-runbook.py | Respected |
| Hook-based enforcement | Respected |
| Changes to /inline or /orchestrate | Respected |
| Continuation infrastructure | Respected |

**Note on validate-runbook.py:** The +12 line change adds ImportError-as-RED vacuity detection (Section 11.1 companion). This is an author-corrector coupling obligation — when tdd-cycle-planning.md changed the Bootstrap pattern, review-plan and validate-runbook.py needed corresponding updates. Justified despite being out of scope.

## Summary

- **Critical:** 0
- **Major:** 2 (planstate gap, glob/single-artifact ambiguity)
- **Minor:** 4 (table duplication, subagent_type naming, 2 unspecified companion changes)

The corrector review (reports/review.md) caught and fixed 3 issues before this review. The 2 Major findings are architectural gaps: planstate was in-scope but not delivered, and multi-file /proof invocation is underspecified. Both originate partly in the outline (planstate specified without lifecycle mechanism, glob pattern used without multi-artifact protocol).
