# Plugin Migration — Design

## Problem

edify-plugin distributes skills, agents, and hooks to projects via git submodule + symlinks (`just sync-to-parent`). This causes:

- **Ceremony:** Every structural change requires `just sync-to-parent` + restart
- **Fragility:** Symlink breakage in worktrees, missed agents in sync recipe (e.g., `remember-task.md`, `memory-refactor.md`)
- **Adoption friction:** New projects must set up submodule + run sync + configure settings.json hooks
- **Hook indirection:** settings.json → symlink → edify-plugin/hooks (two redirects)

Claude Code plugins solve all of these via auto-discovery of skills/agents and native hook registration.

## Requirements

**Source:** `plans/plugin-migration/outline.md` + design conversation

**Naming note:** The outline uses pre-decision naming (`/ac:init`, `.ac-version`, `plugin/`). This design supersedes those: plugin marketplace name is `edify`, git repo is `edify-plugin` (was `plugin`). All `ac` and `plugin` references in the outline should be read accordingly.

**Functional:**
- FR-1: Skills, agents, hooks load via plugin auto-discovery (no symlinks) — addressed by Components 1-2
- FR-2: `just claude` and `just claude0` launch with `--plugin-dir ./edify-plugin` — addressed by Component 5
- FR-3: `/edify:init` scaffolds CLAUDE.md + fragments for new projects (idempotent) — addressed by Component 4
- FR-4: `/edify:update` syncs fragments when plugin version changes — addressed by Components 3-4
- FR-5: UserPromptSubmit hook detects stale fragments, warns via additionalContext — addressed by Component 7
- FR-6: Portable justfile recipes (claude, wt-*, precommit-base) importable by any project — addressed by Component 5
- FR-7: Existing projects migrate by removing symlinks (no other structural changes) — addressed by Component 6
- FR-8: Plan-specific agents (`*-task.md`) coexist with plugin agents — addressed by Component 1 (auto-discovery vs `.claude/agents/`)
- FR-9: All hooks migrate to plugin; settings.json hooks section emptied — addressed by Component 2

**Non-functional:**
- NFR-1: Dev mode edit→restart cycle no slower than current symlink approach — addressed by `--plugin-dir` live loading
- NFR-2: No token overhead increase from plugin vs symlink loading — validated post-migration

**Out of scope:**
- Fragment content changes (behavioral rules stay as-is)
- Workflow skill redesign
- Marketplace publishing (future)
- Breaking changes to skill interfaces
- New hook logic (existing hooks migrate as-is)

## Architecture

### Dual-Purpose Package

edify-plugin becomes both:
1. **Plugin** — `.claude-plugin/plugin.json` enables auto-discovery of `skills/`, `agents/`, `hooks/`
2. **Submodule** — `fragments/`, `bin/`, `templates/`, `configs/` remain available via submodule path

### Installation Modes

| Mode | Plugin Loading | Fragment Access | Justfile |
|------|---------------|-----------------|----------|
| **Dev** (submodule) | `--plugin-dir ./edify-plugin` | `@edify-plugin/fragments/*.md` direct | `import 'edify-plugin/just/portable.just'` |
| **Consumer** (marketplace) | Plugin install | `/edify:init` copies to `agents/rules/` | Manual or template |

### Directory Layout (edify-plugin)

```
edify-plugin/
├── .claude/                # UNCHANGED: edify-plugin local dev config
├── .claude-plugin/
│   └── plugin.json         # NEW: Plugin manifest (name: "edify")
├── hooks/
│   ├── hooks.json          # NEW: Plugin hook configuration
│   ├── pretooluse-block-tmp.sh
│   ├── submodule-safety.py
│   ├── userpromptsubmit-shortcuts.py
│   └── userpromptsubmit-version-check.py  # NEW: Fragment staleness detector
├── skills/                 # UNCHANGED: 16 skill directories
├── agents/                 # UNCHANGED: 14 agent .md files
├── fragments/              # UNCHANGED: 20 instruction fragments
├── bin/                    # UNCHANGED: 11 utility scripts
├── just/
│   └── portable.just       # NEW: Extracted portable recipes
├── docs/                   # UNCHANGED: workflow and pattern documentation
├── scripts/                # UNCHANGED: create-plan-agent.sh, split-execution-plan.py
├── migrations/             # UNCHANGED: schema migration documentation
├── templates/              # UNCHANGED
├── configs/                # UNCHANGED
├── .version                # NEW: Fragment version marker
├── Makefile                # UNCHANGED: cache management
├── README.md               # UNCHANGED
└── justfile                # MODIFIED: sync-to-parent removed
```

**Deleted:**
- `hooks/pretooluse-symlink-redirect.sh` — purpose eliminated (no more symlinks to edit)

## Components

### 1. Plugin Manifest

**File:** `edify-plugin/.claude-plugin/plugin.json`

```json
{
  "name": "edify",
  "version": "1.0.0",
  "description": "Workflow infrastructure for Claude Code projects"
}
```

**Why minimal:** Auto-discovery handles skills, agents, and hooks from conventional directory locations. No custom path overrides needed — edify-plugin already uses the standard layout (`skills/*/SKILL.md`, `agents/*.md`, `hooks/hooks.json`).

**Coexistence with plan-specific agents:** Plugin agents are discovered from `edify-plugin/agents/`. Plan-specific agents (`*-task.md`) live in `.claude/agents/` as regular files. Both are visible to the Task tool. No namespace collision — plugin agents are internally qualified as `edify:agent-name`.

### 2. Hook Migration

**File:** `edify-plugin/hooks/hooks.json`

Plugin hooks use the wrapper format required by Claude Code:

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/pretooluse-block-tmp.sh"
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py"
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
          "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py"
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
```

**Hook script changes:**

| Script | Change Required | Rationale |
|--------|----------------|-----------|
| `pretooluse-block-tmp.sh` | **None** | No env vars used; checks file paths from stdin only |
| `submodule-safety.py` | **None** | Uses `$CLAUDE_PROJECT_DIR` correctly — it checks the *project's* cwd, not the plugin's location |
| `userpromptsubmit-shortcuts.py` | **None** | No env vars used; stateless stdin→stdout |
| `pretooluse-symlink-redirect.sh` | **Delete** | Purpose eliminated — no symlinks to protect |

**Critical insight:** The explore report incorrectly suggested replacing `$CLAUDE_PROJECT_DIR` with `$CLAUDE_PLUGIN_ROOT` in `submodule-safety.py`. This is wrong. The script needs to know the *project root* (where the user's code lives), not the *plugin root* (where edify is installed). `$CLAUDE_PROJECT_DIR` is the correct variable and remains unchanged.

**hooks.json path resolution:** `$CLAUDE_PLUGIN_ROOT` in `hooks.json` commands resolves to the plugin directory at runtime. In dev mode (`--plugin-dir ./edify-plugin`), it resolves to the edify-plugin directory. In consumer mode (marketplace install), it resolves to the cached plugin directory.

### 3. Fragment Versioning System

**Purpose:** Detect when plugin fragments are newer than project-local copies.

**Files:**
- `edify-plugin/.version` — source version marker (plain text, e.g., `1.0.0`)
- `<project>/.edify-version` — project's installed fragment version

**Version bump protocol:**
- Bump `edify-plugin/.version` whenever fragments change
- Semantic: major = breaking CLAUDE.md structure, minor = new fragment, patch = fragment content fix

**Comparison logic (in version-check hook):**
- Read `$CLAUDE_PROJECT_DIR/.edify-version`
- Read `$CLAUDE_PLUGIN_ROOT/.version`
- If mismatch: inject additionalContext warning
- If `.edify-version` missing: no warning (project may not use managed fragments)

### 4. Migration Command (`/edify:init`)

**Type:** Skill (not command) — needs access to reasoning, file operations, and conditional logic.

**Location:** `edify-plugin/skills/init/SKILL.md`

**Behavior:**

1. **Detect installation mode:**
   - Submodule: `edify-plugin/` exists as directory → dev mode (fragment `@` refs point to `edify-plugin/fragments/`)
   - Plugin only: no `edify-plugin/` → consumer mode (copy fragments to `agents/rules/`)

2. **Scaffold structure:**
   - Create `agents/` directory if missing
   - Create `agents/session.md` from template if missing
   - Create `agents/learnings.md` from template if missing
   - Create `agents/jobs.md` from template if missing

3. **Fragment handling (consumer mode only):**
   - Copy fragments from plugin to `agents/rules/`
   - Rewrite `@edify-plugin/fragments/` references to `@agents/rules/` in CLAUDE.md

4. **CLAUDE.md scaffolding:**
   - If no CLAUDE.md exists: copy `templates/CLAUDE.template.md`, adjust `@` references per mode
   - If CLAUDE.md exists: no modification (idempotent — don't risk destroying user content)

5. **Version marker:**
   - Write `.edify-version` with current `edify-plugin/.version` value

**Idempotency guarantee:** Every operation checks before acting. Re-running `/edify:init` applies only missing pieces.

**`/edify:update` skill:** Separate skill at `edify-plugin/skills/update/SKILL.md`. Behavior: re-copies fragments from plugin source to project target (overwriting existing), then updates `.edify-version` marker. Unlike `/edify:init`, it skips scaffolding (CLAUDE.md, session.md, etc.) and only handles fragment sync. In dev mode, this is a no-op (fragments are read directly from `edify-plugin/fragments/` via `@` references). In consumer mode, it copies updated fragments to `agents/rules/`.

### 5. Justfile Modularization

**New file:** `edify-plugin/just/portable.just`

**Extracted recipes (portable, no Python dependency):**

| Recipe | Purpose | Notes |
|--------|---------|-------|
| `claude` | `claude --plugin-dir ./edify-plugin` | Primary dev workflow |
| `claude0` | `claude --plugin-dir ./edify-plugin --system-prompt ""` | Clean-slate workflow |
| `wt-new name base="HEAD"` | Create worktree | Submodule-aware, `--reference` pattern |
| `wt-ls` | List worktrees | Delegates to `git worktree list` |
| `wt-rm name` | Remove worktree | Force-remove for submodules |
| `wt-merge name` | Merge worktree | Auto-resolves session.md conflicts |
| `precommit-base` | Run edify-plugin validators | validate-tasks, validate-learnings, validate-memory-index, etc. |

**Recipe extraction rules:**
- Portable recipes use only git + bash (no Python tools)
- `precommit-base` calls validators via relative `edify-plugin/bin/` paths (dev mode only; consumer mode path resolution via `$CLAUDE_PLUGIN_ROOT/bin/` is deferred per D-7)
- Bash prolog (`bash_prolog` template variable) stays in root justfile (project-specific helpers)
- `precommit-base` is a *subset* of precommit — it runs edify-plugin validators only. Project justfile adds language-specific checks on top.

**Project justfile consumption:**

```just
import 'edify-plugin/just/portable.just'

# Project-specific recipes below
test *ARGS:
    pytest {{ ARGS }}

precommit: precommit-base
    # Add language-specific checks after base validators
    ruff check
    mypy
```

**justfile `import` support:** Just supports `import` natively (since v1.19.0). Imported files can define their own variables and recipes. However, variables are NOT shared across import boundaries — `portable.just` must define its own `bash_prolog` (or equivalent helper functions) for the `wt-*` and other recipes that currently depend on the root justfile's `bash_prolog`. The portable prolog should be minimal (only `fail`, `visible`, color variables) compared to the root's full prolog (which includes `sync`, `run-checks`, `pytest-quiet`, etc.).

**Root justfile changes:**
- Remove recipes that move to `portable.just` (claude, wt-*, precommit-base subset)
- Add `import 'edify-plugin/just/portable.just'`
- Keep project-specific recipes (test, format, check, lint, release, line-limits)
- Keep `bash_prolog` for project-specific helper functions
- Rebuild `.cache/just-help.txt` after import change (imported recipes appear in `just --list` output, affecting CLAUDE.md `@` reference)

### 6. Symlink Cleanup

**Execution order:** Last component — only after all others verified working.

**Steps:**
1. Remove all symlinks from `.claude/skills/` (16 symlinks)
2. Remove all symlinks from `.claude/agents/` (12 symlinks, preserve `*-task.md` regular files)
3. Remove all symlinks from `.claude/hooks/` (4 symlinks)
4. Remove `pretooluse-symlink-redirect.sh` from `edify-plugin/hooks/` (script deleted)
5. Remove hook entries from `.claude/settings.json` (hooks section becomes `{}`)
6. Remove `sync-to-parent` recipe from `edify-plugin/justfile`
7. Update `.gitignore` if needed (symlink tracking no longer necessary)

**settings.json after cleanup:**

```json
{
  "permissions": { ... },
  "attribution": { ... },
  "plansDirectory": "plans/claude/",
  "sandbox": { ... }
}
```

The `hooks` key is removed entirely. All hook behavior now comes from `edify-plugin/hooks/hooks.json` via plugin auto-discovery.

**Validation before cleanup:**
- `claude --plugin-dir ./edify-plugin` → verify skills load (`/help` lists plugin skills)
- Verify agents appear in Task tool
- Verify hooks fire (test each hook event)
- Only then proceed with symlink removal

### 7. Post-Upgrade Version Check

**File:** `edify-plugin/hooks/userpromptsubmit-version-check.py`

**Behavior:**
- Fires on every UserPromptSubmit (no matcher — same as shortcuts hook)
- Reads `$CLAUDE_PROJECT_DIR/.edify-version` and `$CLAUDE_PLUGIN_ROOT/.version`
- On version mismatch: inject additionalContext `"⚠️ Fragments outdated (project: X, plugin: Y). Run /edify:update."`
- On match or missing `.edify-version`: silent pass-through (exit 0)
- **Once-per-session:** Use a temp file (`$CLAUDE_PROJECT_DIR/tmp/.edify-version-checked`) to fire only on first prompt. Note: Do NOT use system `/tmp/` — the `pretooluse-block-tmp.sh` hook blocks it, and the hook script itself should follow the same convention

**Design rationale:** No PostUpgrade hook exists in Claude Code. UserPromptSubmit is the earliest reliable hook point. Once-per-session gating prevents noise on subsequent prompts.

**Performance:** File existence check + two small file reads. Well under the 5s timeout.

### 8. Script Path Updates

**Audit of `edify-plugin/bin/` references:**

Scripts are referenced from three contexts:
1. **Skills/agents:** `edify-plugin/bin/prepare-runbook.py` — used in skill procedures
2. **settings.json:** `permissions.allow` pattern `Bash(edify-plugin/bin/prepare-runbook.py:*)`
3. **Justfile precommit:** `edify-plugin/bin/validate-*.py` validators

**Dev mode (submodule):** All paths remain `edify-plugin/bin/...` — no change needed. The submodule directory is the plugin directory.

**Consumer mode (marketplace):** Scripts are inside the plugin at `$CLAUDE_PLUGIN_ROOT/bin/...`. Skills and agents would reference `$CLAUDE_PLUGIN_ROOT/bin/` instead of `edify-plugin/bin/`.

**Decision:** For this migration, only dev mode paths matter. Consumer mode path resolution is deferred to marketplace publishing work. Skills can use `edify-plugin/bin/` paths for dev mode; consumer mode will need a path resolution layer (future work, out of scope).

**Minimal changes:**
- `permissions.allow` entry stays as `Bash(edify-plugin/bin/prepare-runbook.py:*)` (dev mode only)
- Validators in precommit stay as `edify-plugin/bin/validate-*.py`
- No script content changes needed

## Key Design Decisions

### D-1: Naming Hierarchy

| Concept | Name | Git repo | Notes |
|---------|------|----------|-------|
| Product | edify | `edify` (was claudeutils) | Latin *aedificare* = "to build" + "to instruct" |
| Plugin | edify (marketplace) | `edify-plugin` (was plugin) | Submodule directory = `edify-plugin/` |
| Python package | edify | `edify` (same repo) | Statusline, session extraction, TDD tooling |

**Why `edify-plugin` not `edify-core`:** The Python package has equal claim to "core" — spending that word on the plugin forecloses the best name for the package. `edify-plugin` is self-documenting and never needs disambiguation.

**Full naming research:** `plans/plugin-migration/reports/naming-research.md`.

### D-2: Hook Scripts Stay Unchanged (Except Deletion)

The `$CLAUDE_PROJECT_DIR` vs `$CLAUDE_PLUGIN_ROOT` distinction is critical:
- `$CLAUDE_PROJECT_DIR` = where the user's project lives (for cwd enforcement, tmp blocking)
- `$CLAUDE_PLUGIN_ROOT` = where the plugin is installed (for locating hook scripts in hooks.json)

Hook *configuration* (hooks.json) uses `$CLAUDE_PLUGIN_ROOT` to locate scripts.
Hook *scripts* use `$CLAUDE_PROJECT_DIR` when they need the project path.
These are orthogonal and both correct.

### D-3: Fragment Distribution via Skill, Not Script

`/edify:init` is a skill (SKILL.md) not a standalone script because:
- Needs conditional logic based on installation mode
- Needs to reason about existing CLAUDE.md content
- Needs idempotency guarantees that are hard to script
- Skills have access to Read/Write/Edit tools with error handling

### D-4: `hooks.json` Over Inline in `plugin.json`

Plugin hooks go in `hooks/hooks.json` (separate file, direct format) rather than inline in `plugin.json` because:
- hooks.json is auto-discovered from `hooks/` directory
- Keeps plugin.json minimal (just name + version)
- Easier to edit hooks independently of manifest

**Format note:** `hooks/hooks.json` uses direct format (`{"PreToolUse": [...]}`) — no wrapper object. The wrapper format (`{"hooks": {...}}`) is only for inline hooks in `plugin.json`.

### D-5: Justfile `import` Over Bash Prolog for Portable Recipes

Portable recipes use Just's native `import` mechanism:
- Clean separation: portable recipes in one file, project recipes in another
- No bash prolog injection needed for shared recipes
- Project-specific helpers stay in root justfile's `bash_prolog`

### D-6: `.edify-version` Over `.ac-version`

Version marker named after plugin marketplace name (`edify`) not old acronym (`ac`):
- Consistent with plugin name on marketplace
- Clear provenance — "this version marker belongs to the edify plugin"
- `.edify-version` in project root (not nested in `agents/`)

### D-7: Future Python Package Dependency

The plugin will depend on the edify Python package for tooling (statusline CLI, session extraction, future TDD infrastructure). Not implemented in this migration — current scripts are stdlib-only.

**Dual venv strategy (future):**
- Submodule mode: parent project's venv has `edify` as dev dependency (direnv activates), plugin scripts `import edify`
- Marketplace mode: plugin creates internal venv, installs edify + deps itself

**Dual memory:**
- Plugin ships edify knowledge via skills, agents, and fragments (how edify works, patterns, conventions)
- Plugin reads project knowledge via `$CLAUDE_PROJECT_DIR` (project-specific decisions, learnings, session state)
- No built-in plugin memory-sharing mechanism exists in Claude Code yet — skills/agents/fragments are the carrier

### D-8: Consumer Mode Deferred

Consumer mode (marketplace install, fragment copying, path resolution) is designed but not implemented in this migration. The focus is dev mode: submodule + `--plugin-dir`. Consumer mode adds complexity (path resolution layer, fragment copying logic) that blocks the core migration without adding immediate value.

`/edify:init` skill is created with consumer mode *design* but only dev mode *implementation*. Consumer mode code paths are stubbed with clear TODO markers.

## Implementation Notes

### Affected Files (Create)

| File | Purpose |
|------|---------|
| `edify-plugin/.claude-plugin/plugin.json` | Plugin manifest |
| `edify-plugin/hooks/hooks.json` | Plugin hook configuration |
| `edify-plugin/hooks/userpromptsubmit-version-check.py` | Fragment version check hook |
| `edify-plugin/.version` | Fragment version marker |
| `edify-plugin/just/portable.just` | Portable justfile recipes |
| `edify-plugin/skills/init/SKILL.md` | `/edify:init` skill |
| `edify-plugin/skills/update/SKILL.md` | `/edify:update` skill |

### Affected Files (Modify)

| File | Change |
|------|--------|
| `.claude/settings.json` | Remove `hooks` section entirely |
| `edify-plugin/justfile` | Remove `sync-to-parent` recipe |
| Root `justfile` | Add `import`, remove migrated recipes |
| `.cache/just-help.txt` | Regenerate (imported recipes change `just --list` output) |
| `.cache/just-help-edify-plugin.txt` | Regenerate (sync-to-parent removed from edify-plugin justfile) |
| `edify-plugin/fragments/claude-config-layout.md` | Remove symlink section referencing `just sync-to-parent` |
| `edify-plugin/fragments/sandbox-exemptions.md` | Remove `just sync-to-parent` subsection |
| `edify-plugin/fragments/project-tooling.md` | Remove `sync-to-parent` references |
| `edify-plugin/fragments/delegation.md` | Update examples referencing `sync-to-parent` |

### Affected Files (Delete)

| File | Reason |
|------|--------|
| `edify-plugin/hooks/pretooluse-symlink-redirect.sh` | Purpose eliminated |
| `.claude/skills/*` (symlinks) | Replaced by plugin auto-discovery |
| `.claude/agents/*` (symlinks only) | Replaced by plugin auto-discovery |
| `.claude/hooks/*` (symlinks) | Replaced by plugin hooks.json |

### Testing Strategy

| Component | Test Method |
|-----------|-------------|
| Plugin manifest | `claude --plugin-dir ./edify-plugin` → skills appear in `/help` |
| Hook migration | Manual hook testing: trigger each hook event, verify behavior matches current |
| Version check | Create `.edify-version` with old version, verify warning on first prompt |
| Init skill | Run on clean directory, verify scaffolding; run on existing project, verify idempotency |
| Justfile import | `just claude` works, `just wt-new test` works from imported recipe |
| Symlink cleanup | Remove symlinks, verify all functionality preserved |
| Coexistence | Create plan-specific agent, verify both plugin and local agents visible |

### Rollback

Each component is independently revertible via git. Symlink cleanup (Component 6) is the point of no return for the old workflow — execute last.

If plugin discovery fails at any point before Component 6: re-run `just sync-to-parent` to restore symlinks (recipe still exists until Component 6).

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/implementation-notes.md` — @ references limitation, hook behavior patterns
- `edify-plugin/fragments/claude-config-layout.md` — hook configuration patterns (already loaded via CLAUDE.md)
- `edify-plugin/fragments/sandbox-exemptions.md` — permission patterns (already loaded via CLAUDE.md)
- `plans/plugin-migration/reports/explore-structure.md` — full edify-plugin directory tree
- `plans/plugin-migration/reports/explore-hooks.md` — hook script analysis
- `plans/plugin-migration/reports/explore-justfiles.md` — justfile structure analysis

**Skills to load:**
- `plugin-dev:plugin-structure` — plugin.json format, auto-discovery rules
- `plugin-dev:hook-development` — hooks.json format, event types, output format

**Additional research allowed:** Planner may query Context7 for Just `import` syntax details.

## Next Steps

1. `/plan-adhoc plans/plugin-migration/design.md` — create execution runbook
2. Load `plugin-dev:plugin-structure` and `plugin-dev:hook-development` before planning
