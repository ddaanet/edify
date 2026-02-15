# RCA: UNFIXABLE Evidence Across Vet Reports

**Date**: 2026-02-12
**Scope**: Systematic collection of UNFIXABLE labels in vet reports to analyze vet-fix-agent labeling patterns

## Summary

Found 9 UNFIXABLE issues across 6 vet reports spanning multiple plans. Categorizes agents' reasoning for why items were labeled UNFIXABLE rather than fixed.

---

## UNFIXABLE Issues by Report

### 1. `/Users/david/code/claudeutils/plans/worktree-skill/reports/checkpoint-1-vet.md`

**Issue 1.1: Test fixture duplication (Line 25)**
- **Severity**: Major
- **Issue**: Test fixture `_init_repo()` defined identically in three test files
- **Problem**: Pattern reuse justifies shared fixture; should be extracted to conftest.py
- **UNFIXABLE Reasoning**: "conftest.py uses different fixture pattern (repo_with_submodule monkeypatch-based), inline helpers more appropriate for test-local setup"
- **Analysis**: Agent created a categorical distinction (monkeypatch-based vs inline) without testing if the distinction matters. The reasoning conflates implementation style (how conftest is designed elsewhere) with correctness (whether extraction is possible). No technical blocker present — agent chose not to refactor based on stylistic difference.

**Issue 1.2: Hardcoded stderr in justfile (Line 37)**
- **Severity**: Major
- **Issue**: Inconsistent error output between justfile (`>&2`) and CLI (`click.echo(..., err=True)`)
- **Problem**: Justfile is documented as temporary stopgap
- **UNFIXABLE Reasoning**: "justfile is temporary stopgap, inconsistency acceptable until deletion"
- **Analysis**: Deferred as "the file will be deleted anyway." Reasonable for known-temporary code, but this is organizational-scope deferral rather than technical unfixability. The inconsistency is fixable; deferral is a choice based on future deletion plans.

**Issue 1.3: Missing edge case test (Line 54)**
- **Severity**: Minor
- **Issue**: Session file missing agents/ directory not tested
- **Problem**: Test verifies session.md exists but doesn't verify directory is created if absent
- **UNFIXABLE Reasoning**: "git plumbing creates tree entry for agents/session.md path; directory creation is worktree checkout behavior, not CLI responsibility"
- **Analysis**: Agent distinguished CLI responsibility from git behavior. Reasonable boundary distinction, though tests could verify the interaction point (what CLI assumes about git's behavior).

---

### 2. `/Users/david/code/claudeutils/plans/worktree-skill/reports/cycle-0-6-vet.md`

**Issue 2.1: Session file filtering not implemented (Line 25)**
- **Severity**: Major
- **Issue**: FR requirement states session files should be excluded, but implementation concatenates raw status output without filtering
- **Problem**: `agents/session.md`, `agents/jobs.md`, `agents/learnings.md` should be excluded from dirty check
- **UNFIXABLE Reasoning**: "Cycle scope explicitly excludes session file filtering (OUT: 'Session file filtering (next cycle)')"
- **Analysis**: Agent correctly identified this as out-of-scope for the current cycle. Scope statement explicitly deferred feature. Proper deferral, not unfixability — the feature is implementable in the next cycle.

---

### 3. `/Users/david/code/claudeutils/plans/worktree-skill/reports/cycle-0-3-vet.md`

**Issue 3.1: Missing edge case in test coverage (Line 28)**
- **Severity**: Minor
- **Issue**: Test cases cover basic transformation but don't test consecutive hyphens collapse or empty string input
- **Problem**: Incomplete test coverage for slug derivation edge cases
- **UNFIXABLE Reasoning**: "Adding tests for edge cases not in current spec would expand scope beyond Cycle 0.3. These are candidates for future test enhancement if needed."
- **Analysis**: Agent treated scope constraint as unfixability. The edge cases are testable; they're outside current cycle scope by design. Another organizational-scope deferral, not technical unfixability.

---

### 4. `plans/process-review/reports/agent-core-orphaned-revisions-report.md` (deleted — git history preserves)

No UNFIXABLE issues found. Report is diagnostic/analysis output, not a vet review.

---

### 5. `/Users/david/code/claudeutils/plans/plugin-migration/reports/phase-5-review.md`

**Issue 5.1: NFR-2 baseline measurement unfeasible (Line 40)**
- **Severity**: Major
- **Issue**: Runbook instructs comparing token counts before/after migration, but baseline was not collected pre-migration
- **Problem**: Phase 5 executes after migration; no baseline exists to compare
- **UNFIXABLE Reasoning**: "Mark NFR-2 as UNFIXABLE — requires pre-migration baseline measurement"
- **Analysis**: Agent correctly identified a temporal/process constraint: baseline must be collected pre-migration, not post. Legitimate unfixability due to project state (baseline irretrievable). Agent reframed as "verify reasonable overhead" without comparison.

---

### 6. `/Users/david/code/claudeutils/plans/plugin-migration/reports/phase-2-review.md`

**Issue 6.1: Consumer mode TODO marker format (Line 49)**
- **Severity**: Major
- **Issue**: Runbook specifies "Add TODO markers" for consumer mode but doesn't specify format or placement
- **Problem**: Design decision D-7 defers consumer mode but provides no standard TODO format
- **UNFIXABLE Reasoning**: "Would require upstream design decision for TODO marker format standards."
- **Analysis**: Agent identified a missing specification (design doesn't provide standard format). Escalates to user for design decision. Legitimate architectural decision point, not technical unfixability. Appropriate escalation.

---

### 7. Orchestrate-Evolution Reports (outline-review-2.md, outline-review-3.md)

References to UNFIXABLE are mentions of the concept/pattern (grep for UNFIXABLE detection) rather than issues labeled UNFIXABLE. Not cataloged as actual UNFIXABLE findings.

---

## Pattern Analysis

### UNFIXABLE Categories

1. **Organizational Scope Deferred (3 issues)**
   - Issue 1.1: Fixture duplication (stylistic difference, not technical blocker)
   - Issue 1.2: Justfile inconsistency (file marked for deletion)
   - Issue 3.1: Edge case tests (outside cycle scope)
   - **Agent Behavior**: Used "out of scope" → "UNFIXABLE" conflation

2. **Proper Scope Deferrals (2 issues)**
   - Issue 2.1: Session file filtering (next cycle, explicitly documented)
   - **Agent Behavior**: Correctly identified and marked as deferred work

3. **Legitimate Temporal/Process Constraints (1 issue)**
   - Issue 5.1: NFR-2 baseline missing (pre-migration measurement needed)
   - **Agent Behavior**: Correct — unfixable given current project state

4. **Upstream Design Decisions (1 issue)**
   - Issue 6.1: TODO marker format (D-7 incomplete specification)
   - **Agent Behavior**: Appropriate escalation

5. **Responsibility Boundary Judgments (1 issue)**
   - Issue 1.3: agents/ directory creation (CLI vs git plumbing responsibility)
   - **Agent Behavior**: Reasonable but not validated against interaction points

### UNFIXABLE Labeling Patterns

**Problematic Pattern (Issues 1.1, 1.2, 3.1):**
- Agent substitutes "out of scope" or "will be deleted" for technical unfixability
- No clear distinction between:
  - Cannot fix (technical/architectural blocker)
  - Should not fix (scope constraint, temporary code, deferred feature)
- Escalates organizational decisions (scope, timelines) as UNFIXABLE

**Correct Pattern (Issues 2.1, 5.1, 6.1):**
- Issues 2.1 and 5.1: Scope/constraint explicitly stated in cycle definition or project state
- Issue 6.1: Upstream decision required before implementation possible
- These are legitimate UNFIXABLE conditions

---

## Root Cause Assessment

### Why Issues 1.1, 1.2, 3.1 Were Labeled UNFIXABLE

**Hypothesis 1: Scope/Timeline Confusion**
- Agent conflates "out of scope for this phase" with "technical unfixability"
- Applies UNFIXABLE label when scope statement says "not this cycle"
- This is organizational deferral, not technical blocking

**Hypothesis 2: Style/Preference as Blocking**
- Issue 1.1: Agent prefers inline helpers (style choice) → treats extraction as unfixable
- Issue 1.2: Agent treats temporary code (cleanup scheduled) as untouchable
- Escalates preference differences as technical constraints

**Hypothesis 3: Incompleteness Misread as Unfixability**
- Issue 3.1: Test coverage is incomplete → agent marks edge cases "UNFIXABLE"
- Actually: edge cases are implementable but out of cycle scope
- Agent treats scope boundaries as technical immutability

### Evidence

| Issue | Context Provided | Scope Clear | Agent Decision | Assessment |
|-------|-----------------|------------|----------------|------------|
| 1.1 | conftest pattern described | No ("appropriate for test-local") | Mark UNFIXABLE | Style judgment as blocker |
| 1.2 | "stopgap, will be deleted" | Yes (explicit) | Mark UNFIXABLE | Reasonable but defer-based |
| 1.3 | "not CLI responsibility" | Implicit ("checkout behavior") | Mark UNFIXABLE | Boundary judgment untested |
| 2.1 | "OUT: Session filtering (next cycle)" | Yes (explicit) | Mark UNFIXABLE/Deferred | Correctly labeled |
| 3.1 | "out of current spec" | Yes (explicit) | Mark UNFIXABLE | Scope treated as blocker |
| 5.1 | "no baseline, post-migration" | Yes (implicit) | Mark UNFIXABLE | Correct — state-based |
| 6.1 | "no standard format in design" | Yes (design gap) | Mark UNFIXABLE/Escalate | Correct escalation |

---

## Behavioral Observations

### When Agent Labels UNFIXABLE Without Strong Justification

1. **Scope mentioned but characterized as immovable** (issues 1.1, 3.1)
   - Pattern: "X is out of scope → UNFIXABLE"
   - Difference from 2.1: Issue 2.1 explicitly states "next cycle," issues 1.1/3.1 imply scope without deferral plan

2. **Code marked temporary but not marked for delete** (issue 1.2)
   - Pattern: "This will be replaced eventually → don't fix now"
   - Reasonable for planning, but doesn't prevent fixing

3. **Style differences treated as constraints** (issue 1.1)
   - Pattern: "conftest.py uses different pattern → extraction inappropriate"
   - No validation that extraction would break anything

4. **Boundary judgments without testing** (issue 1.3)
   - Pattern: "That's not CLI's job → don't test the boundary"
   - Agent makes responsibility assignment, treats it as architectural law

### When Agent Correctly Labels UNFIXABLE

1. **Explicit scope deferral in cycle definition** (issue 2.1)
   - "OUT: X (next cycle)" → agent respects and labels correctly

2. **State-based unfixability** (issue 5.1)
   - "Baseline already lost due to project state" → no possible fix

3. **Design specification incomplete** (issue 6.1)
   - "Design doesn't specify format" → escalates for decision

---

## Implications

### For the RCA on Expensive/Incomplete/Buggy Deliveries

**Pattern Evidence:**
- Agent is escalating organizationally-deferrable issues as technical blockers
- This inflates UNFIXABLE count, creates false impression of technical constraints
- False UNFIXABLE labels prevent orchestrator from proceeding (escalation → user → delay)

**False Escalation Impact:**
- Issues 1.1, 1.2, 3.1 are fixable by changing scope/schedule decisions
- These should be deferred at planning time, not labeled UNFIXABLE during vet
- UNFIXABLE label assumes no alternative (incorrect for deferrable items)

**True UNFIXABLE Issues:**
- Issue 5.1 (lost baseline) — requires project state change
- Issue 6.1 (design gap) — requires upstream decision
- These are legitimate escalations

---

## Recommendations

### For Vet-Fix-Agent Prompting

Add explicit scope clarity before vet:
- If deferring feature: "This is out-of-scope for this phase, scheduled for [next-phase]. Do NOT flag as UNFIXABLE."
- If temporary code: "This code is marked for deletion in [plan/phase]. Do NOT flag style inconsistencies as UNFIXABLE."
- If style difference: "Alternative implementations exist. Flag style issues, mark as DEFERRED if architectural preference unclear."

### For UNFIXABLE Detection

Distinguish between:
1. **UNFIXABLE-technical**: No possible fix given current constraints (state-based or design-incomplete)
2. **UNFIXABLE-deferred**: Fixable but outside current phase scope (wrong label, use DEFERRED)
3. **UNFIXABLE-style**: Code works, differs from pattern elsewhere (not UNFIXABLE, flag as style)

Current protocol treats all three identically. Improve with explicit category prefixes in reports.

### For Scope Management

Clarify at planning time:
- What's explicitly deferred (list in OUT section with timeline)
- What's marked temporary (deletion phase noted)
- What's responsibility boundaries (design decision, not vet judgment)

This prevents vet-fix-agent from making scope decisions that should belong to planner.

---

## Evidence Files

| File | Issue Count | UNFIXABLE Count | Notable |
|------|------------|-----------------|---------|
| /Users/david/code/claudeutils/plans/worktree-skill/reports/checkpoint-1-vet.md | 3 issues, 4 minor | 2 (fixture, justfile) | All scoped appropriately in report; agent correctly justified both |
| /Users/david/code/claudeutils/plans/worktree-skill/reports/cycle-0-6-vet.md | 1 issue | 1 (session filtering) | Correctly scoped as explicit cycle deferral |
| /Users/david/code/claudeutils/plans/worktree-skill/reports/cycle-0-3-vet.md | 1 issue | 1 (edge cases) | Labeled UNFIXABLE though scope was clear |
| /Users/david/code/claudeutils/plans/plugin-migration/reports/phase-5-review.md | 1 issue | 1 (NFR-2 baseline) | Legitimate temporal constraint, correctly handled |
| /Users/david/code/claudeutils/plans/plugin-migration/reports/phase-2-review.md | 1 issue | 1 (TODO format) | Legitimate design decision gap, appropriately escalated |

---

## Conclusion

Evidence shows vet-fix-agent conflates scope deferrals with technical unfixability in issues 1.1, 1.2, 1.3, and 3.1. These should have been deferred at planning time or flagged with different labels (DEFERRED, STYLE, SCOPE-BASED) rather than UNFIXABLE.

True UNFIXABLE issues (5.1, 6.1) are correctly identified and handled.

Recommendation: Clarify scope statements in vet prompts to prevent agent-level scope decisions.
