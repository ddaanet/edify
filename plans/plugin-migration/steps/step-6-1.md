# Step 6.1

**Plan**: `plans/plugin-migration/runbook-phase-6.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Execute after plugin verified working. Irreversible within session.

---

---

## Step 6.1: Remove symlinks and clean settings.json

**Objective**: Remove all symlinks from `.claude/`, remove hook entries from `settings.json`, remove deny rules that guarded symlink targets, and remove `sync-to-parent` recipe.

**Prerequisites**:
- Phases 1, 2, 5 complete (plugin fully verified, version coordination in place)
- Post-phase state verification:
  - `plugin/hooks/hooks.json` contains all 9 surviving hooks (setup integrated into `sessionstart-health.sh`, no new hook added)
  - `plugin/.claude-plugin/plugin.json` exists
  - `sessionstart-health.sh` updated with setup responsibilities (Step 2.3)

**Implementation**:
1. **Remove skill symlinks** from `.claude/skills/`:
   - `find .claude/skills/ -type l -delete` (removes all 33 symlinks)
   - Verify: `find .claude/skills/ -type l | wc -l` returns 0
2. **Remove agent symlinks and obsolete agent files** from `.claude/agents/`:
   - `find .claude/agents/ -type l -delete` (removes 13 symlinks)
   - `rm -f .claude/agents/handoff-cli-tool-*.md` (plan-specific agents — plan absorbed, no longer needed)
   - Verify: `find .claude/agents/ -type l | wc -l` returns 0
3. **Remove hook symlinks** from `.claude/hooks/`:
   - `find .claude/hooks/ -type l -delete` (removes 4 symlinks)
4. **Remove ALL hook entries** from `.claude/settings.json`:
   - Delete the entire `"hooks": { ... }` section
   - Settings.json retains: permissions, sandbox, plansDirectory, attribution, enabledPlugins
5. **Remove deny rules** from `.claude/settings.json` that guarded symlink targets:
   - Remove `Write(.claude/skills/*)`
   - Remove `Write(.claude/agents/*)`
   - Remove `Write(.claude/hooks/*)`
   - Remove `Bash(ln:*)`
6. **Remove `sync-to-parent` recipe** from `plugin/justfile`
7. **Delete `pretooluse-symlink-redirect.sh`** from `plugin/hooks/`:
   - `rm plugin/hooks/pretooluse-symlink-redirect.sh`
   - Verify entry removed from `plugin/hooks/hooks.json` (done in Step 2.1)
8. **Update `.gitignore`**: run `grep -n 'symlink\|\.claude/skills\|\.claude/agents\|\.claude/hooks' .gitignore` — remove any lines that tracked symlinks as generated artifacts

**Expected Outcome**:
- No symlinks in `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`
- No obsolete agent files in `.claude/agents/`
- `settings.json` has no `hooks` section
- `settings.json` deny list has no symlink-guard rules
- `sync-to-parent` recipe removed
- `pretooluse-symlink-redirect.sh` deleted

**Error Conditions**:
- If `find -type l` finds non-plugin symlinks → investigate before deleting
- If `handoff-cli-tool-*.md` files cannot be deleted (permission error, unexpected file type) → investigate before proceeding
- If settings.json parse fails after editing → fix JSON syntax

**Validation**:
- `find .claude/skills/ -type l | wc -l` returns 0
- `find .claude/agents/ -type l | wc -l` returns 0
- `find .claude/hooks/ -type l | wc -l` returns 0
- `ls .claude/agents/handoff-cli-tool-*.md 2>/dev/null | wc -l` returns 0
- `python3 -c "import json; d=json.load(open('.claude/settings.json')); assert 'hooks' not in d; print('OK')"`
- `test ! -f plugin/hooks/pretooluse-symlink-redirect.sh && echo OK` returns OK
- **Automated plugin check** (from project root, symlinks now removed):
  ```bash
  claude -p "list your available slash commands" --plugin-dir ./plugin 2>&1 | grep -c "design\|commit\|orchestrate" && \
  claude -p "list your available agents" --plugin-dir ./plugin 2>&1 | grep -c "agent"
  ```
  Skills and agents must be discoverable via `--plugin-dir` alone (no symlinks remain)

---
