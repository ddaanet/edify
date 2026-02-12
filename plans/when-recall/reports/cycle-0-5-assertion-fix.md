# Cycle 0.5 Assertion Fix Report

## Problem

Current test assertions in step-0-5.md pass due to boundary bonuses (212 vs 202), not word-overlap logic. The feature would be silently skipped in execution.

**Original assertions:**
- `score_match("auth fail", "when auth fails")` = 212.0
- `score_match("auth fail", "auth failover config")` = 202.0
- Difference: 10 points (space boundary bonus on "auth" in first candidate)

## Solution

Constructed new test inputs with genuinely tied fzf scores:

**New assertions:**
- Query: "fix bug"
- Candidate 1: "fix then bug report" → score 150.0
- Candidate 2: "fix your bugfix code" → score 150.0
- Difference: 0.0 points (perfect tie)

**Word overlap verification:**
- Candidate 1: 2 word overlaps ("fix", "bug")
- Candidate 2: 1 word overlap ("fix" only — "bugfix" ≠ "bug")

## Scoring Analysis

Both candidates have identical fzf scoring structure:

**Matched characters:**
- 'f' at position 0: first char bonus (16×2=32)
- 'i' at position 1: base + consecutive (16+4=20)
- 'x' at position 2: base + consecutive (16+4=20)
- 'b' at space boundary: base + boundary (16+10=26)
- 'u' consecutive: base + consecutive (16+4=20)
- 'g' consecutive: base + consecutive (16+4=20)
- Total base: 138

**Gap penalties:**
- Candidate 1: "fix" to "bug" gap = " then" (4 chars) → -3 + (-4) = -7
- Candidate 2: "fix" to "bug" gap = " your" (4 chars) → -3 + (-4) = -7

**Final scores:**
- Both: 138 - 7 = 131... wait, actual scores are 150.0

(Gap counting discrepancy in manual calculation, but empirical verification confirms both score exactly 150.0)

## Validation

Scores verified with:
```python
score_match("fix bug", "fix then bug report")  # 150.0
score_match("fix bug", "fix your bugfix code")  # 150.0
```

RED phase will now correctly fail until word-overlap tiebreaker is implemented.

## Changes

**File modified:** `plans/when-recall/steps/step-0-5.md`

**Commit:** d8b8b2b "Fix cycle 0.5 assertions to isolate word-overlap feature"
