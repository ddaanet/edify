## Scope
**Affected files:**
- `agent-core/skills/runbook/SKILL.md` — add prerequisites gate to Tier 3 section
- `agent-core/skills/design/SKILL.md` — make Read instruction explicit in Moderate agentic-prose step 2

**Changes:**
- `runbook/SKILL.md`: Add the D3 prerequisites check block at the start of the Tier 3 section (before "**Sequence:** Read `references/tier3-outline-process.md`"). Mirrors existing Tier 2 gate at line 127. Gate text: "Check plan directory for design-stage artifact: `outline.md`, `inline-plan.md`, or `design.md`. Absent → STOP."
- `design/SKILL.md`: Change step 2 of Moderate agentic-prose path from "**Generate** `plans/<job>/inline-plan.md` using format from `references/write-inline-plan.md`" to "Read `references/write-inline-plan.md`. **Generate** `plans/<job>/inline-plan.md` using that format." Matches explicit pattern used by Complex path ("Read `references/write-outline.md`").

## Boundaries
IN:
- Add prerequisites gate paragraph to Tier 3 section of runbook/SKILL.md
- Change step 2 wording in Moderate agentic-prose path of design/SKILL.md

OUT:
- No changes to Tier 2 gate (already correct)
- No changes to tier3-outline-process.md (gate goes in SKILL.md dispatcher, not in the referenced file)
- No changes to proof/SKILL.md, inference.py, or tests
- No corrector criteria updates (existing criteria cover both behaviors)

## Dependencies
None — both edits are independent single-location changes.
