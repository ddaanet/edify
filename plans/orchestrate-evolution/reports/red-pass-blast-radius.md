# RED Pass Blast Radius: Diagnostic & Protocol

**Date:** 2026-02-12
**Source:** when-recall Phase 0 orchestration, cycles 0.1–0.8

## Incident

Cycle 0.3 agent reported unexpected RED pass — test passed when failure expected. Investigation (prompted by user) revealed the issue extended beyond one cycle.

## Diagnostic: Phase 0 Blast Radius Assessment

Tested all remaining Phase 0 cycles' RED assertions against current implementation state after cycles 0.1 (subsequence matching) and 0.2 (boundary bonuses) completed.

| Cycle | Feature | RED Passes? | Classification | Root Cause |
|-------|---------|-------------|----------------|------------|
| 0.3 | Consecutive bonus | YES | Over-implementation | Step 0.1 assertion (`exact > sparse`) impossible with base scoring; agent added consecutive bonus to satisfy test |
| 0.4 | Gap penalties | NO | Correct | Feature absent, 48.0 == 48.0 |
| 0.5 | Word-overlap tiebreaker | YES | **Test flaw** | Boundary bonuses create score difference (212 vs 202); feature absent but test satisfied by unrelated behavior |
| 0.6 | Min score threshold | NO | Correct | `score_match("x", long_string)` returns 32.0, not 0.0 |
| 0.7 | rank_matches | YES | Over-implementation | Agent created function in cycle 0.1 because design.md lists it in module spec |
| 0.8 | Prefix disambiguation | YES | By design | Cycle spec says "No new code required IF existing scoring already disambiguates" |

### Critical Finding: Cycle 0.5 Test Flaw

The word-overlap tiebreaker will never be implemented. The test asserts `score_match("auth fail", "when auth fails") > score_match("auth fail", "auth failover config")` expecting this requires word-overlap logic. But boundary bonuses already create a 10-point difference (212 vs 202). The test passes, GREEN never runs, feature silently skipped.

**Fix needed at execution time:** Rewrite RED assertions with inputs that produce genuinely tied fzf scores, so only the tiebreaker can break the tie.

### Root Cause Analysis

Three distinct failure categories:

1. **Step contradiction** (0.3): RED assertions require behavior the GREEN phase explicitly excludes ("no bonuses yet" but `exact > sparse` impossible without bonuses). Agent forced to over-implement. Design context told it what to add but any solution would pull a future feature forward.

2. **Design context leakage** (0.7): Agent proactively created `rank_matches` (listed in design.md module spec) during cycle 0.1 despite step file not mentioning it. The scope decision (step + design + outline) is intentional — design context helps agents make correct implementation choices. This is acceptable: feature is correctly implemented.

3. **Assertion isolation failure** (0.5): Test doesn't isolate the target feature. Assertions pass due to side effects of other features (boundary bonuses). This is a deliverable defect — feature designed but never implemented.

### Design Context Scope Assessment

The question: does including design.md in agent context cause harmful over-implementation?

**Evidence:** Design context caused 1/6 remaining cycles to have features pre-implemented (0.7). The consecutive bonus over-implementation (0.3) was caused by a step file contradiction, not design context — the agent would have needed to add something regardless.

**Verdict:** Design context is net positive. Without it, cycle 0.1's over-implementation would have been ad-hoc (wrong constants, wrong algorithm) instead of design-aligned. The rank_matches pre-creation (0.7) is harmless — function is correct and tests add coverage.

## Proposed Protocol: RED Pass Blast Radius

### Trigger

TDD cycle reports unexpected RED pass (test passes when failure expected, no `[REGRESSION]` marker).

### Procedure

1. **Don't handle in isolation.** An unexpected pass indicates implementation state diverged from runbook assumptions.

2. **Blast radius assessment.** Write each remaining cycle's RED assertions as executable code, run against current state, classify each:
   - **Over-implementation:** Feature present, test correctly validates it. Commit test, skip GREEN/REFACTOR.
   - **Test flaw:** Test passes but feature is ABSENT. **Critical** — feature silently skipped. Rewrite assertions to isolate feature.
   - **Correct:** Feature absent, test fails. Execute normally.

3. **Fix test flaws before continuing.** Test flaws are deliverable defects. Rewrite RED assertions to require the specific feature (construct inputs that isolate behavior).

4. **Resume execution.** Over-implementations: commit test, skip GREEN/REFACTOR. Correct: execute normally. Test flaws: execute with rewritten assertions.

### Rationale

A single unexpected pass often indicates systemic runbook issues (step contradictions, design context effects, assertion isolation failures) affecting multiple cycles. Point-fixing one cycle misses adjacent defects. The assessment costs minutes; a silent feature skip costs a missing deliverable.

### Integration Points

- **Orchestrate skill:** On RED_PASS escalation, run blast radius before deciding how to handle
- **Plan-reviewer:** Could potentially catch assertion isolation failures during review (detect assertions satisfiable by prior-cycle features)
- **Runbook expansion:** Planner should verify RED assertions are unsatisfiable without the GREEN implementation
