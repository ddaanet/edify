# Step 2.1 Vet Review: runbook-review.md Restructuring

**Reviewed file:** `agents/decisions/runbook-review.md`
**Also changed:** `agents/memory-index.md`, `agent-core/skills/memory-index/SKILL.md`
**Step:** 2.1 (FR-1: Restructure runbook-review.md as type-agnostic)
**Reviewer:** Self-review (sub-agent context, cannot delegate to vet-fix-agent)

## Verification Criteria

### 1. All 5 axes have type-agnostic definitions with TDD/General subsections

| Axis | Type-neutral definition | TDD subsection | General subsection |
|------|------------------------|----------------|-------------------|
| Vacuous Items | Line 11: "Items where RED tests don't constrain... or steps produce no functional outcome" | Lines 13-17 | Lines 19-22 |
| Ordering | Line 35: "Items that reference structures not yet created" | Lines 37-40 | Lines 42-44 |
| Item Density | Line 52: "Unnecessary items that dilute expansion quality" | Lines 54-58 | Lines 60-63 |
| Checkpoints | Line 71: "Distance between quality gates" | Lines 73-76 | Lines 78-81 |
| File Growth | Line 92: "Growth projection prevents refactor escalations" | Lines 94-97 | Lines 99-102 |

All 5 axes present with type-neutral definitions and both subsections. FIXED (pre-existing + heading renames).

### 2. Behavioral vacuity detection is concrete

Lines 24-27 add:
- TDD: pairwise cycle verification (N+1 RED fails given N GREEN)
- General: achievability test (N+1 not achievable by extending N)
- Heuristic: cycles/steps > LOC/20

All three criteria are concrete and actionable. FIXED.

### 3. Process section uses conditional terminology

Lines 110-115:
- Step 1: "Identify phase types (TDD or general)"
- Step 2: "For each item (cycle or step)"
- Step 3: "evaluate item (cycle or step) density"
- Step 4: "count items (cycles or steps) between quality gates"

Consistent conditional terminology throughout. FIXED.

### 4. Heading renames (type-agnostic)

- "When Detecting Vacuous Tdd Cycles" -> "When Detecting Vacuous Items"
- "When Evaluating Cycle Density" -> "When Evaluating Item Density"
- "haiku context window" -> "context window" (removed model-specific reference in density definition)

### 5. Memory index consistency

Both `agents/memory-index.md` and `agent-core/skills/memory-index/SKILL.md` updated:
- `/when detecting vacuous tdd cycles` -> `/when detecting vacuous items`
- `/when evaluating cycle density` -> `/when evaluating item density`

Entries match renamed headings. FIXED.

## Issues Found

None. All acceptance criteria met.

## Summary

- 0 UNFIXABLE
- 0 DEFERRED
- 5 items verified as correctly implemented
