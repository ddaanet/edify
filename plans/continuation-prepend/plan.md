# Continuation Prepend — Tier 2 Plan

**Design source:** `plans/continuation-prepend/problem.md`
**Classification:** Moderate — agentic-prose + production (test)
**Model:** Opus (architectural artifacts)

## Component 1: Protocol & Skill Updates (prose)

Update the consumption protocol to add step 3 (prepend) — skills may optionally prepend entries to the continuation before consuming.

### Files

1. **`agent-core/fragments/continuation-passing.md`** §Consumption Protocol (lines 32-45)
   - Add step 3: "If skill needs a subroutine: prepend entries to continuation"
   - Clarify: existing entries remain in original order (append-only invariant)
   - Clarify: prepend only — never remove, reorder, or modify existing entries

2. **`agent-core/skills/inline/SKILL.md`** §Continuation (lines 164-174)
   - Add prepend step between step 2 and step 3
   - Renumber existing step 3 → step 4

3. **`agent-core/skills/orchestrate/references/continuation.md`** §Consumption (lines 7-17)
   - Add optional prepend step to IF continuation present flow
   - Add prepend example (orchestrate needs /commit checkpoint before continuing chain)

4. **`agent-core/skills/handoff/SKILL.md`** §Continuation (lines 151-155)
   - Add prepend mention to the compact protocol description

### NOT in scope

- `agent-core/skills/design/SKILL.md` — No `cooperative: true` frontmatter, no §Continuation section. Uses continuation implicitly in routing args. Separate tech debt.
- `agent-core/skills/runbook/SKILL.md` — Same as design.
- `agent-core/skills/commit/SKILL.md` — Terminal skill. No continuation section. Would never prepend.

## Component 2: Integration Test

Add test for prepend behavior in `tests/test_continuation_integration.py`.

- Test: skill prepends subroutine entry, consumes it, remainder preserves original chain
- Test: prepend preserves append-only invariant (original entries unchanged)
- Test: multiple prepended entries consumed in order

## Constraint

**Append-only for existing entries.** The user's original chain plus default exits form an immutable suffix. Skills may only add work *before* it.
