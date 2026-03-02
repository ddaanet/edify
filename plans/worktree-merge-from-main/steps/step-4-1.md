# Step 4.1

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: opus
**Phase**: 4

---

## Step 4.1: Add Mode D to SKILL.md and update enumeration sites

Add Mode D (Sync from main) to `agent-core/skills/worktree/SKILL.md` following Mode C structure.

**Mode D content:**
- Invocation: `wt sync` or `wt from-main`, maps to `claudeutils _worktree merge --from-main`
- Sandbox bypass required (same as Mode C)
- Exit code handling parallels Mode C (0=success, 3=conflicts, 1=precommit failure, 2=fatal)
- Key differences from Mode C: session.md keeps ours (worktree focus preserved), learnings.md uses main as base with branch delta appended, delete/modify conflicts auto-resolved (main's structural changes accepted)

**Enumeration sites:** Grep SKILL.md for "merge", "Mode C", "slug" references. Update:
- Principles section: "Merge is idempotent" applies to both directions
- Mode list (if any): add Mode D entry
- Any Mode C references that should mention bidirectional awareness

**Checkpoint:** `just precommit` — skill file validates, all tests pass.
