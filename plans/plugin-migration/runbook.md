---
name: plugin-migration
model: haiku
---

# Plugin Migration Runbook

**Context:** Migrate plugin from symlink-based distribution to Claude Code plugin architecture (dev mode only).

**Source:** `plans/plugin-migration/design.md`

**Status:** Ready for execution

**Created:** 2026-02-07

---

## Weak Orchestrator Metadata

**Total Steps:** 16

**Execution Model:**
- Steps 1.1-1.2, 2.1-2.2, 3.1-3.3, 4.1-4.2, 5.1-5.2, 6.1-6.2: Haiku (file operations, inline execution)
- Steps 2.3-2.4: Sonnet (skill design requires reasoning)
- Step 5.3: Sonnet (validation and analysis)

**Step Dependencies:**
- Phase 1 → Phase 2, 3, 4 (plugin manifest required)
- Phases 2, 3, 4 → Phase 5 (all components ready for cleanup)
- Phase 5 → Phase 6 (cleanup complete before cache regeneration)

**Error Escalation:**
- Haiku → Sonnet: Validation failures, unexpected file structures
- Sonnet → User: Design deviations, unfixable issues

**Report Locations:** `plans/plugin-migration/reports/`

**Success Criteria:** Plugin loads without errors, all skills/agents/hooks functional, performance parity with symlink approach, no token overhead increase

**Prerequisites:**
- Plugin manifest created (Phase 1)
- Skills loaded: `plugin-dev:plugin-structure` and `plugin-dev:hook-development`

---

## Common Context

**Requirements:**
- FR-1: Plugin auto-discovery (no symlinks) — Phases 1-2
- FR-2: `just claude` with `--plugin-dir` — Phase 4
- FR-3: `/edify:init` scaffolding — Phase 2
- FR-4: `/edify:update` fragment sync — Phase 2
- FR-5: Version check via hook — Phase 3
- FR-6: Portable justfile recipes — Phase 4
- FR-7: Symlink cleanup — Phase 5
- FR-8: Plan-specific agent coexistence — Phase 5
- FR-9: Hooks migrate to plugin — Phase 3
- NFR-1: Dev mode performance parity — Phase 5 validation
- NFR-2: Token overhead parity — Phase 5 validation

**Key Constraints:**
- Dev mode only (D-7): Consumer mode deferred to future work
- Plugin name = `edify` (D-1)
- Hook scripts unchanged except deletion (D-2)
- Skills/agents already in correct structure for auto-discovery

**Project Paths:**
- Plugin manifest: `plugin/.claude-plugin/plugin.json`
- Version marker: `plugin/.version`
- Hook config: `plugin/hooks/hooks.json`
- Skills: `plugin/skills/*/SKILL.md` (16 existing + 2 new)
- Agents: `plugin/agents/*.md` (14 files)
- Portable recipes: `plugin/just/portable.just`

**Conventions:**
- Use `$CLAUDE_PLUGIN_ROOT` in hook commands for portability
- Use project `tmp/` directory (not system `/tmp/`)
- Verify with `jq` for JSON validation
- Test hooks require restart (hooks load at session start only)

---

### Phase 1: Plugin Manifest

## Step 1.1: Create plugin manifest

Create minimal plugin manifest at `plugin/.claude-plugin/plugin.json`:

```bash
mkdir -p plugin/.claude-plugin
cat > plugin/.claude-plugin/plugin.json << 'EOF'
{
  "name": "edify",
  "version": "1.0.0",
  "description": "Workflow infrastructure for Claude Code projects"
}
EOF
```

**Validation:** File exists, JSON valid via `jq .`, contains name/version/description

---

## Step 1.2: Create fragment version marker

Create version marker at `plugin/.version`:

```bash
printf '1.0.0' > plugin/.version
```

**Validation:** File exists, content exactly `1.0.0` (5 bytes, no trailing newline)

---

### Phase 2: Skills and Agents

## Step 2.1: Verify agent structure

Verify `plugin/agents/` contains 14 agent `.md` files:

```bash
agent_count=$(find plugin/agents -maxdepth 1 -name "*.md" -type f | wc -l)
echo "Agent count: $agent_count"
[ "$agent_count" -eq 14 ] || echo "ERROR: Expected 14 agents"
```

---

## Step 2.2: Verify skill structure

Verify `plugin/skills/` contains 16 skill subdirectories with `SKILL.md`:

```bash
skill_count=$(find plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
skill_md_count=$(find plugin/skills -name "SKILL.md" | wc -l)
echo "Skill directory count: $skill_count"
echo "SKILL.md count: $skill_md_count"
[ "$skill_count" -eq 16 ] && [ "$skill_md_count" -eq 16 ] || echo "ERROR: Expected 16 skills"
```

---

## Step 2.3: Create /edify:init skill

Create `/edify:init` skill at `plugin/skills/init/SKILL.md` for dev mode scaffolding.

**Note:** Skill content should provide procedural guidance for Claude on how to scaffold project structure (detect mode, create directories, copy templates, write version marker). See existing skills like `/token-efficient-bash` for procedural format patterns.

---

## Step 2.4: Create /edify:update skill

Create `/edify:update` skill at `plugin/skills/update/SKILL.md` for fragment sync.

**Note:** Skill content should provide procedural guidance for version marker updates (dev mode: no-op, just update `.edify-version`; consumer mode: TODO markers).

---

### Phase 3: Hook Migration

## Step 3.1: Create hooks.json

Create `plugin/hooks/hooks.json` with plugin hook configuration:

```bash
cat > plugin/hooks/hooks.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/pretooluse-block-tmp.sh",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-shortcuts.py",
            "timeout": 5
          },
          {
            "type": "command",
            "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-version-check.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
EOF
```

**Validation:** File exists, JSON valid, contains `hooks` field at root level

---

## Step 3.2: Delete obsolete hook script

Delete `plugin/hooks/pretooluse-symlink-redirect.sh`:

```bash
rm plugin/hooks/pretooluse-symlink-redirect.sh
```

**Validation:** File no longer exists

---

## Step 3.3: Create version check hook

Create `plugin/hooks/userpromptsubmit-version-check.py` with once-per-session version mismatch detection.

**Implementation:** Python script that checks `.edify-version` vs `.version`, uses temp file `tmp/.edify-version-checked` for once-per-session gating, injects warning via `additionalContext` if versions differ.

---

### Phase 4: Justfile Modularization

## Step 4.1: Create portable.just

Extract portable recipes to `plugin/just/portable.just` with minimal bash prolog (fail, visible, color variables). Include: claude, claude0, wt-new, wt-ls, wt-rm, wt-merge, precommit-base.

---

## Step 4.2: Update root justfile

Add `import 'plugin/just/portable.just'` at top, remove migrated recipes, keep project-specific recipes (test, format, check, lint, release, line-limits).

---

### Phase 5: Cleanup and Validation

## Step 5.1: Remove symlinks

Remove all symlinks from `.claude/skills/` (16), `.claude/agents/` (12, preserve `*-task.md` regular files), `.claude/hooks/` (4).

---

## Step 5.2: Cleanup configuration and documentation

- Remove `hooks` section from `.claude/settings.json`
- Remove `sync-to-parent` recipe from `plugin/justfile`
- Update fragments: claude-config-layout.md, sandbox-exemptions.md, project-tooling.md, delegation.md (remove sync-to-parent references)

---

## Step 5.3: Validate all functionality

**Plugin discovery:** `claude --plugin-dir ./plugin` → verify skills in `/help`, agents in Task tool

**Hook testing:** Restart session, trigger each event type (PreToolUse, PostToolUse, UserPromptSubmit), verify behavior matches baseline

**Agent coexistence:** Create test `test-task.md` agent, verify both plugin and local agents visible

**NFR validation:**
- NFR-1: Compare edit→restart cycle time with baseline (should match)
- NFR-2: Measure context size before/after with identical session (diff ≤ 5%)

---

### Phase 6: Cache Regeneration

## Step 6.1: Regenerate root just help cache

Run `just cache` to rebuild `.cache/just-help.txt` after import changes.

---

## Step 6.2: Regenerate plugin just help cache

Run `gmake -C plugin all` to rebuild `.cache/just-help-plugin.txt` after sync-to-parent removal.

---

## Design Decisions

- **D-1:** Plugin name = `edify`
- **D-2:** Hook scripts unchanged (except deletion)
- **D-3:** Fragment distribution via skill
- **D-4:** `hooks.json` separate file
- **D-5:** Justfile `import` for portability
- **D-6:** `.edify-version` marker
- **D-7:** Consumer mode deferred (dev mode only)

---

## Dependencies

**Before This Runbook:**
- plugin submodule exists at current location
- Skills loaded: `plugin-dev:plugin-structure`, `plugin-dev:hook-development`
- Baseline measurements captured (for NFR validation)

**After This Runbook:**
- Plugin operational in dev mode (`--plugin-dir ./plugin`)
- Symlinks removed (point of no return for old workflow)
- All functionality validated against requirements

---

## Rollback

Each phase is independently revertible via git. Phase 5 (symlink cleanup) is the point of no return — execute last. If plugin discovery fails before Phase 5, can restore symlinks with `just sync-to-parent` (recipe still exists until Phase 5.2).

---

## Notes

- **Dev mode only:** Implements submodule + `--plugin-dir` workflow. Consumer mode (marketplace) designed but deferred per D-7.
- **Idempotency:** All file creation steps check existence first. Runbook can be re-run safely.
- **Testing strategy:** Manual testing per component. Hook testing requires restart (hooks load at session start only).
- **Performance:** Phase 5.3 validation includes NFR performance and token overhead checks against baseline.
