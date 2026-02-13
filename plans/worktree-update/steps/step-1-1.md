# Step 1.1

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.1: Fix wt-merge THEIRS clean tree check and agent-core setup recipe

**Objective**: Fix two justfile issues — add clean tree check for worktree side before merge (C2), and add setup recipe to agent-core (C3).

**Findings**: C2 (`justfile:209-222` missing THEIRS clean tree check) and C3 (`agent-core/justfile` missing `setup` recipe required by design D5).

**Implementation**:

1. **Read current wt-merge recipe** at `justfile:209-222`:
   - Identify where OURS clean tree check happens
   - Note the check pattern and error message format

2. **Add THEIRS clean tree check**:
   - After OURS check (around line 211-212)
   - Before fetch and merge operations
   - Check worktree directory for uncommitted changes
   - Pattern: `git -C "$WT_PATH" diff --quiet --exit-code && git -C "$WT_PATH" diff --cached --quiet --exit-code`
   - Error message: "Worktree has uncommitted changes. Commit or stash before merging."

3. **Verify placement**:
   - THEIRS check must run BEFORE `git fetch` (line 213)
   - Both clean checks (OURS and THEIRS) must complete before merge operations

4. **Add agent-core setup recipe** in `agent-core/justfile`:
   - Read existing recipes to understand structure
   - Add after existing recipes
   - agent-core is documentation/skills only — check if pyproject.toml or package.json exists
   - If no package dependencies: stub recipe pointing to `just sync-to-parent`
   - If dependencies exist: implement actual setup steps

**Expected Outcome**: wt-merge recipe checks both sides for uncommitted changes. `just setup` runs successfully in agent-core directory.

**Error Conditions**:
- If git commands fail → check WT_PATH is correctly computed
- If recipe syntax error → verify bash quoting and variable expansion
- If justfile syntax error in agent-core → verify recipe formatting (tabs vs spaces)

**Validation**:
```bash
grep -A 3 "THEIRS" justfile
cd agent-core && just setup && echo $?
```

---
