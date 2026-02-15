# Step 3.2

**Plan**: `plans/pushback/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.2: Sync symlinks to parent

**Objective**: Update symlinks in `.claude/` via `just sync-to-parent`

**Implementation**:

Run `just sync-to-parent` in `agent-core/` directory. This syncs:
- `.claude/hooks/userpromptsubmit-shortcuts.py` → `agent-core/hooks/userpromptsubmit-shortcuts.py`
- `.claude/agents/` symlinks
- `.claude/skills/` symlinks

**Command**:
```bash
cd agent-core && just sync-to-parent
```

Requires `dangerouslyDisableSandbox: true` (writes to `.claude/` outside project sandbox allowlist)

**Expected Outcome**: Symlinks updated, hook changes now visible in `.claude/hooks/`

**Error Conditions**:
- Recipe fails with permission error → STOP, verify dangerouslyDisableSandbox
- Symlinks not created/updated → STOP, check recipe output for errors

**Validation**: `ls -la .claude/hooks/userpromptsubmit-shortcuts.py` shows symlink to agent-core

---
