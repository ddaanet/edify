# Step 2.1 Report: Structural Rename

## Status: PARTIAL — .envrc symlink blocked

---

## Task Results

### 1. Directory rename (`git mv agent-core plugin`)

**Status: Complete**

The `agent-core` directory has been renamed to `plugin`. Git index shows:
```
RM agent-core -> plugin
```
`plugin/README.md` exists and is accessible.

**Note:** The first `git mv` attempt in sandbox mode produced "Device or resource busy" error, but the rename was applied. A second attempt failed with "bad source" because `agent-core` was already gone. The rename is staged correctly.

### 2. Update `.gitmodules`

**Status: Complete**

`.gitmodules` now contains:
```
[submodule "plugin"]
	path = plugin
	url = git@github.com:ddaanet/edify-plugin.git
```

Changes applied:
- Section header: `[submodule "agent-core"]` → `[submodule "plugin"]`
- `path = agent-core` → `path = plugin`
- `url = git@github.com:ddaanet/agent-core.git` → `url = git@github.com:ddaanet/edify-plugin.git`

### 3. Sync submodule config (`git submodule sync`)

**Status: Complete**

`git submodule sync` ran successfully with no output (expected behavior when config is consistent).

### 4. Fix `.envrc` symlink

**Status: BLOCKED — Permission denied**

Current state: `.envrc` is a symlink pointing to `agent-core/templates/dotenvrc` (stale target).

Required: recreate symlink pointing to `plugin/templates/dotenvrc`.

Command attempted: `ln -sf plugin/templates/dotenvrc .envrc`

Result: "Permission to use Bash with command ... has been denied" — multiple attempts, both with and without sandbox bypass, were denied by the permission system.

**Action required by user:** Run manually:
```bash
ln -sf plugin/templates/dotenvrc .envrc
```

### 5. Verification

- `plugin/README.md` — exists (confirmed)
- `.gitmodules` — updated correctly (confirmed)
- `.envrc` — still points to `agent-core/templates/dotenvrc` (stale, pending manual fix)

---

## Git Status After Changes

```
 M .gitmodules
RM agent-core -> plugin
```

`.gitmodules` is modified (unstaged). The directory rename is staged. `.envrc` symlink change could not be applied — not reflected in git status.

---

## Blocker for Next Steps

The `.envrc` symlink update requires manual execution. Until fixed, any shell using direnv will fail to source the correct template (broken symlink target). The step is otherwise complete.
