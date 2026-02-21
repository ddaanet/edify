# Step 1.3

**Plan**: `plans/quality-infrastructure/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.3: Delete plan-specific detritus

**Objective**: Remove 8 standalone plan-specific agent files from .claude/agents/.

**Execution Model**: Haiku

**Implementation**:

Git rm these 8 files from .claude/agents/:
- error-handling-task.md
- pushback-task.md
- runbook-quality-gates-task.md
- when-recall-task.md
- workflow-rca-fixes-task.md
- worktree-merge-data-loss-task.md
- worktree-merge-resilience-task.md
- workwoods-task.md

**CRITICAL**: Verify each file is a standalone file (not a symlink) before deleting. Symlinks point to agent-core/ and must NOT be deleted — they're managed by `just sync-to-parent`. Check with `ls -la .claude/agents/` first.

**Expected Outcome**: 8 standalone files removed. All symlinks remain intact.

**Error Conditions**:
- File not found → Warn, continue (may already be deleted)
- File is a symlink → STOP, do NOT delete — symlinks managed separately

**Validation**: `ls -la .claude/agents/` shows only symlinks (→ agent-core/) plus hook-batch-task.md. No other standalone *-task.md files.

---
