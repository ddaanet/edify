# Step 1.2

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.2: Vet fragment

**Objective**: Review fragment for deslop compliance, research grounding application, and fragment structural conventions.

**Implementation**:

Delegate to `vet-fix-agent` with execution context:

**Scope:**
- IN: Fragment content (Motivation, Design Discussion Evaluation, Agreement Momentum, Model Selection), prose style, research grounding application
- OUT: Hook implementation, CLAUDE.md wiring (future phases)

**Changed files**: `agent-core/fragments/pushback.md`

**Requirements**:
- Deslop compliance: direct statements, no hedging, no preamble, active voice
- Research grounding: evaluator framing (not DA), counterfactual structure, confidence calibration, motivation before rules
- Fragment conventions: clear section structure, imperative rules, appropriate heading level (##)

Fix all issues. Write report to: `plans/pushback/reports/vet-step-1.2.md`

**Expected Outcome**: Vet report shows all issues fixed or no issues found. Fragment revised if needed.

**Error Conditions**:
- UNFIXABLE issues in vet report → STOP, escalate to user with report path
- Fragment still uses hedging after fixes → STOP, investigate why fixes didn't apply

**Validation**: Grep for UNFIXABLE in vet report (should be empty), precommit passes, fragment ready for Phase 2.

---


**Test file**: `tests/test_userpromptsubmit_shortcuts.py` (new — in project `tests/` directory, not `agent-core/`)

**Import mechanism**: Hook filename `userpromptsubmit-shortcuts.py` contains hyphen — requires `importlib.util.spec_from_file_location` to import for testing.

**Common TDD stop conditions** (auto-applied to all cycles):
- RED fails to fail → STOP, diagnose test
- GREEN passes without implementation → STOP, test too weak
- Test requires mocking not yet available → STOP, add prerequisite cycle
- Implementation needs architectural decision → STOP, escalate to opus

---
