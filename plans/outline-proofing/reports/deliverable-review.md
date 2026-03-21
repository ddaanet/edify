# Deliverable Review: outline-proofing

**Date:** 2026-03-20
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | src/claudeutils/planstate/inference.py | +21 | -11 |
| Test | tests/test_planstate_inference.py | +14 | -132 |
| Test | tests/test_planstate_inference_lifecycle.py | +138 | -0 |
| Agentic prose | agent-core/skills/design/SKILL.md | +13 | -1 |
| Agentic prose | agent-core/skills/design/references/write-inline-plan.md | +32 | -0 |
| Agentic prose | agent-core/skills/proof/SKILL.md | +6 | -2 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | +26 | -32 |
| Agentic prose | agent-core/skills/runbook/references/tier3-outline-process.md | +1 | -0 |
| Agentic prose | agent-core/skills/runbook/references/tier3-planning-process.md | +9 | -4 |

**Total:** 260 lines added across 9 files. Layer 1 skipped (< 500 lines) — full Layer 2 review.

### Design Conformance

| Design IN-scope item | Status |
|----------------------|--------|
| /design Moderate agentic-prose path: code reading → inline-plan.md → /proof → /inline | Covered |
| /design Moderate non-prose path: code reading → outline.md → /proof → /runbook | Covered |
| /runbook Tier 1 removal, rename to Two-Tier Assessment | Covered |
| /runbook Tier 2: runbook-outline.md → corrector → /proof | Covered |
| /runbook Tier 3: unconditional /proof after Phase 0.86 | Covered |
| /proof integration points table update (5→8, new rows) | Covered |
| inference.py: inline-planned status + outlined→/design routing fix | Covered |

| Design OUT-scope item | Status |
|----------------------|--------|
| outline-corrector criteria | Unchanged ✓ |
| runbook-corrector criteria | Unchanged ✓ |
| validate-runbook.py | Unchanged ✓ |
| /inline SKILL.md | Unchanged ✓ |

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### M1: Prerequisites check missing from Tier 3 path
**File:** agent-core/skills/runbook/SKILL.md:127
**Axis:** Conformance (D3)
**Description:** D3 states: "If /runbook called directly (bypassing /design): STOP. Check plan directory for design-stage artifact (outline.md, inline-plan.md, or design.md). Absent → halt." The prerequisites check is placed inside the Tier 2 section only. The Tier 3 path (`references/tier3-outline-process.md`) contains no equivalent gate. An agent assessing as Tier 3 bypasses the check.
**Practical risk:** Low — Tier 3 criteria require knowing "multiple independent steps (parallelizable), steps need different models" which presuppose reading a design. An agent can't accurately classify Tier 3 without design context. But the design specifies it as a general gate, not Tier-2-only.

### M2: Implicit Read instruction for write-inline-plan.md
**File:** agent-core/skills/design/SKILL.md:145
**Axis:** Actionability (agentic prose)
**Description:** Moderate agentic-prose path step 2 says "Generate `plans/<job>/inline-plan.md` using format from `references/write-inline-plan.md`". This implies reading the reference file but doesn't say so explicitly. The Complex path says "Read `references/write-outline.md`" — explicit instruction. Inconsistency may cause an agent to try to recall the format rather than reading the file.

## Gap Analysis

| Design requirement | Status | Reference |
|-------------------|--------|-----------|
| inline-plan.md artifact + /proof (no corrector) | Covered | design/SKILL.md:143-147, write-inline-plan.md |
| write-inline-plan.md reference file (D1 format) | Covered | design/references/write-inline-plan.md |
| Moderate routing split (agentic-prose / non-prose) | Covered | design/SKILL.md:141-153 |
| Tier 1 elimination + rename | Covered | runbook/SKILL.md:75 |
| Tier 2 prerequisites STOP gate | Partially covered | runbook/SKILL.md:127 (Tier 2 only — see M1) |
| Tier 2 runbook-outline.md → corrector → /proof flow | Covered | runbook/SKILL.md:129-134 |
| /proof removed from Phase 0.75 step 5 | Covered | tier3-planning-process.md:103-106 |
| Phase 0.87 added post-0.86 | Covered | tier3-planning-process.md:182-186 |
| Phase 0.87 in overview list | Covered | tier3-outline-process.md:10 |
| /proof dispatch table: inline-plan.md → none | Covered | proof/SKILL.md:176 |
| Integration points count: 5→8 | Covered | proof/SKILL.md:202 |
| inference.py inline-planned status | Covered | inference.py:76-77, 104 |
| inference.py outlined → /design routing | Covered | inference.py:103 |
| Test coverage: inline-planned | Covered | test_planstate_inference.py:72-80 |
| Test coverage: outlined→/design routing | Covered | test_planstate_inference.py:136 |
| Test file 400-line limit (split) | Covered | test_planstate_inference_lifecycle.py |

## Summary

- Critical: 0
- Major: 0
- Minor: 2

All 7 design IN-scope items delivered. Both minor findings are low-risk conformance gaps: M1 (prerequisites check placement) is practically safe because Tier 3 criteria presuppose design context; M2 (implicit Read instruction) is a clarity issue that well-trained agents handle through inference but explicit wording would eliminate ambiguity.
