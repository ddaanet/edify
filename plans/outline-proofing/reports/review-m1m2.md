# Review: M1/M2 Fix Verification

**Scope:** agent-core/skills/runbook/SKILL.md (M1), agent-core/skills/design/SKILL.md (M2)
**Date:** 2026-03-21
**Source findings:** plans/outline-proofing/reports/deliverable-review.md (minor findings M1, M2)

## M1: D3 gate in Tier 3 section

**Requirement:** Prerequisites check ("check plan directory for design-stage artifact: outline.md, inline-plan.md, or design.md; absent → STOP") must appear in Tier 3 section of runbook/SKILL.md, not just Tier 2.

**Evidence (runbook/SKILL.md:180):**

> **Prerequisites check (D+B anchor):** Check plan directory for design-stage artifact: `outline.md`, `inline-plan.md`, or `design.md`. Absent → STOP. `/runbook` without prior `/design` gating is an error — scope was not user-validated.

Gate present. Wording identical to Tier 2 gate at line 127. Placement: immediately after Tier 3 criteria block, before `**Sequence:**` — correct.

**Status: PASS**

---

## M2: Explicit Read instruction in Moderate agentic-prose step 2

**Requirement:** Step 2 of Moderate agentic-prose path must include explicit "Read `references/write-inline-plan.md`" instruction before generating the artifact, matching the explicit form used by the Complex path.

**Evidence (design/SKILL.md:145):**

> Read `references/write-inline-plan.md`. **Generate** `plans/<job>/inline-plan.md` using that format.

Explicit Read instruction present. Matches Complex path pattern at line 154 (`Read \`references/write-outline.md\``).

**Status: PASS**

---

## Verdict

Both minor findings from deliverable-review.md are resolved. No further changes required. No UNFIXABLE issues.
