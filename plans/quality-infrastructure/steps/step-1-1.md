# Step 1.1

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.1: Batch rename agent definition files

**Objective**: Rename 11 agent files via git mv to new names per substitution table.
**Script Evaluation**: Direct
**Execution Model**: Haiku

**Implementation**:
Git mv 11 files in agent-core/agents/:
- vet-fix-agent.md to corrector.md
- design-vet-agent.md to design-corrector.md
- outline-review-agent.md to outline-corrector.md
- runbook-outline-review-agent.md to runbook-outline-corrector.md
- plan-reviewer.md to runbook-corrector.md
- review-tdd-process.md to tdd-auditor.md
- quiet-task.md to artisan.md
- quiet-explore.md to scout.md
- tdd-task.md to test-driver.md
- runbook-simplification-agent.md to runbook-simplifier.md
- test-hooks.md to hooks-tester.md

Requires `dangerouslyDisableSandbox: true` (git mv writes .git tracking).
Commit all renames atomically.

**Expected Outcome**: All 11 files at new paths. Old paths removed. Single commit.
**Error Conditions**: git mv fails -> STOP, report file state
**Validation**: `ls agent-core/agents/corrector.md artisan.md scout.md test-driver.md` succeeds; `git status` clean after commit

---
