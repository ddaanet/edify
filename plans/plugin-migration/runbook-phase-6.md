### Phase 6: Symlink cleanup, settings migration, and doc updates (type: general, model: sonnet)

Execute after plugin verified working. Irreversible within session.

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

## Step 6.2: Update fragments and documentation

**Objective**: Remove `sync-to-parent` references and symlink documentation from fragments.

**Prerequisites**:
- Step 6.1 complete (symlinks removed, sync-to-parent deleted)
- Read each fragment before editing:
  - `plugin/fragments/project-tooling.md`
  - `plugin/fragments/claude-config-layout.md`
  - `plugin/fragments/sandbox-exemptions.md`
  - `plugin/fragments/delegation.md` (outline specified as target — verify for any `sync-to-parent` references; currently none found, but confirm before skipping)

**Implementation**:
1. `project-tooling.md`: remove `sync-to-parent` references (recipe no longer exists), remove anti-pattern example using `ln -sf` to create symlinks
2. `claude-config-layout.md`: remove the "Symlinks in .claude/:" subsection (lines referencing `.claude/agents/`, `.claude/skills/`, `.claude/hooks/` symlinks and `just sync-to-parent`)
3. `sandbox-exemptions.md`: remove `sync-to-parent` subsection entirely (recipe deleted)
4. `delegation.md`: check for `sync-to-parent` references; skip if none found (currently clean)

**Expected Outcome**:
- No references to `sync-to-parent` in any fragment
- No symlink documentation in `claude-config-layout.md`
- All fragments valid markdown

**Error Conditions**:
- If fragment has other references to symlinks beyond the targeted sections → investigate scope
- If removing a section leaves orphan cross-references → fix or note

**Validation**:
- `grep -r 'sync-to-parent' plugin/fragments/` returns no matches
- `grep 'sync-to-parent\|Symlinks in .claude' plugin/fragments/claude-config-layout.md` returns no matches

---

## Step 6.3: Validate migration completeness (checkpoint)

**Objective**: Final validation gate before Phase 7 rename. Verify all functional requirements met post-symlink-removal.

**Prerequisites**:
- Steps 6.1, 6.2 complete

**Implementation**:
1. **FR-1**: Plugin auto-discovery works without symlinks (automated via `-p` headless mode):
   ```bash
   claude -p "list your available slash commands" --plugin-dir ./plugin 2>&1 | tee tmp/migration-verify-skills.txt
   claude -p "list your available agents" --plugin-dir ./plugin 2>&1 | tee tmp/migration-verify-agents.txt
   ```
   - Skills and agents must appear in output (no symlinks, `--plugin-dir` only)
2. **FR-7**: All functionality preserved
   - `grep -r '@plugin/' CLAUDE.md agents/ .claude/rules/ | grep -v Binary` — each path must exist: `ls <path>` for each returned reference
   - `grep -rh '^@' plugin/fragments/ plugin/skills/ | sort -u` — verify each referenced fragment path exists on disk
3. **FR-9**: All hooks fire from plugin, settings.json hooks section empty
   - Verify hooks.json contains all hooks
   - Verify settings.json has no hooks section
4. **NFR-2**: Validated architecturally — same content loaded via plugin auto-discovery instead of symlinks. No empirical measurement needed.
5. **Run `just precommit`** — full validation gate
   - Must pass completely (lint, format, type check, tests, version consistency)

**Expected Outcome**:
- All FRs verified
- `just precommit` passes
- System fully functional without symlinks

**Error Conditions**:
- If `just precommit` fails → fix issues before proceeding to Phase 7
- If any FR check fails → diagnose and fix or escalate

**Validation**:
- Validation checkpoint — STOP and report results before Phase 7
- All checks must pass before proceeding to directory rename
