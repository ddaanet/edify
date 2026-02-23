# Step 1.3

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.3: Delete plan-specific agent detritus

**Objective**: Delete 8 standalone agent files from .claude/agents/ left over from past plan executions.
**Script Evaluation**: Direct
**Execution Model**: Haiku

**Implementation**:
Delete 8 files in .claude/agents/:
- error-handling-task.md
- pushback-task.md
- runbook-quality-gates-task.md
- when-recall-task.md
- workflow-rca-fixes-task.md
- worktree-merge-data-loss-task.md
- worktree-merge-resilience-task.md
- workwoods-task.md

Do NOT delete: hb-p*.md, quality-infrastructure-task.md, runbook-generation-fixes-task.md (active plans).

**Expected Outcome**: 8 files deleted. Active plan agents untouched.
**Error Conditions**: File not found -> warn and continue (may already be deleted)
**Validation**: `ls .claude/agents/*-task.md` shows only active plan agents

---
