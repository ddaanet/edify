# Step 5.3

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Step 5.3: Update sync-to-parent Recipe

**Objective:** Add `python3 agent-core/bin/sync-hooks-config.py` call to `sync-to-parent` recipe in `agent-core/justfile`.

**Script Evaluation:** Small — single line addition to justfile recipe.

**Execution Model:** Sonnet (justfile edit requires careful placement and context)

**Prerequisite:**
- Read `agent-core/justfile` sync-to-parent recipe — identify end of recipe body for append location
- Step 5.2 complete: sync-hooks-config.py exists

**Implementation:**

Insert before `echo "Sync complete!"` at the end of the `sync-to-parent` recipe body (after the hooks section, before the closing echo):

```just
    echo "Syncing hook configuration..."
    python3 agent-core/bin/sync-hooks-config.py
```

Notes:
- Justfile recipes run from project root (not script directory)
- `agent-core/bin/sync-hooks-config.py` path is relative to project root — correct
- Recipe uses `#!/usr/bin/env bash` shebang with `set -euo pipefail` — script failure aborts sync
- sync-hooks-config.py writes settings.json → requires dangerouslyDisableSandbox when running `just sync-to-parent`
- The hooks section (symlink sync for hook scripts and hooks.json) already exists in sync-to-parent — insert the sync-hooks-config.py call AFTER the existing hooks section

**Expected Outcome:** `sync-to-parent` recipe ends with hook config sync call. Running `just sync-to-parent` deploys both symlinks and hook configuration.

**Error Conditions:**
- sync-hooks-config.py fails → recipe exits non-zero (set -euo pipefail); settings.json unchanged if write failed
  - Step 5.2 implementation must write atomically (write to temp file, rename to settings.json) to prevent partial write on interrupt — verify this is implemented in sync-hooks-config.py before running

**Validation:**
```bash
# Verify recipe contains new line
grep -n "sync-hooks-config" agent-core/justfile
# Expected: line number with "python3 agent-core/bin/sync-hooks-config.py"
```

---
