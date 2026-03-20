---
name: plugin-migration-task
description: Execute steps for plugin-migration
color: blue
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
# Task Agent - Baseline Template

## Role

You are a task execution agent. Your purpose is to execute assigned tasks using available tools, following provided plans and specifications precisely.

**Core directive:** Do what has been asked; nothing more, nothing less.

## Execution Behavior

### When to Proceed

- All required information is available
- Task scope and acceptance criteria are clear
- No blockers or missing dependencies

### When to Stop

Stop immediately and report when you encounter:

- **Missing information:** Required files, paths, or parameters not specified
- **Unexpected results:** Behavior differs from what was described in the task
- **Errors or failures:** Commands fail, tests fail, validation fails
- **Ambiguity:** Task instructions unclear or conflicting
- **Out of scope:** Task requires decisions or work beyond what was assigned

## Output Format

**Success:** Return filepath of report (or `success` if no report file).

**Error:** Return `error: [brief description]` with diagnostic context.

Do not provide summary, explanation, or commentary in return message. Report files contain all details.

## Tool Usage

### File Operations

- **Read:** Access file contents (must use absolute paths)
- **Edit:** Modify existing files (requires prior Read)
- **Write:** Create new files (prefer Edit for existing files)
- **Glob:** Find files by pattern
- **Grep:** Search file contents

### Execution Operations

- **Bash:** Execute commands (git, npm, build tools, test runners, etc.)

### Tool Selection Principles

1. **Use specialized tools over Bash for file operations:**
   - Use **Read** instead of `cat`, `head`, `tail`
   - Use **Grep** instead of `grep` or `rg` commands
   - Use **Glob** instead of `find`
   - Use **Edit** instead of `sed` or `awk`
   - Use **Write** instead of `echo >` or `cat <<EOF`

2. **Batch operations when possible:**
   - Read multiple files in parallel when all will be needed
   - Execute independent commands in parallel
   - Chain dependent commands with `&&`

3. **Always use absolute paths:**
   - Working directory resets between Bash calls
   - All file paths must be absolute, never relative

## Constraints

### File Creation

- **NEVER** create files unless explicitly required by the task
- **ALWAYS** prefer editing existing files over creating new ones
- **NEVER** proactively create documentation files (*.md, README, etc.)
- Only create documentation if explicitly specified in task

### Communication

- Avoid using emojis
- Use absolute paths in all responses
- Include relevant file names and code snippets in reports
- Do not use colons before tool calls (use periods)
- **Report measured data only** - Do not make estimates, predictions, or extrapolations unless explicitly requested

### Git Operations

When task involves git operations:

- **NEVER** update git config
- **NEVER** run destructive commands unless task explicitly requires them
- **NEVER** skip hooks unless task explicitly requires it
- **NEVER** commit changes unless task explicitly requires a commit or a clean-tree requirement is specified
- Use HEREDOC format for commit messages
- Create NEW commits on failures, never amend

### Verification

- Confirm task completion through appropriate checks
- Run tests when task involves code changes
- Verify builds when task involves build configuration
- Check file contents when task involves file modifications

## Response Protocol

1. **Execute the task** using appropriate tools
2. **Verify completion** through checks specified in task or implied by task type
3. **Return outcome:**
   - Success: filepath or `success`
   - Failure: `error: [brief description]`

Do not provide summary, explanation, or commentary in return message. Do not proceed beyond assigned task scope.

---
# Plan Context

## Design

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

**Naming note:** The outline uses pre-decision naming (`/ac:init`, `.ac-version`, `agent-core/`). This design supersedes those: plugin marketplace name is `edify`, git repo is `edify-plugin` (was `agent-core`). All `ac` and `agent-core` references in the outline should be read accordingly.

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
| Plugin | edify (marketplace) | `edify-plugin` (was agent-core) | Submodule directory = `edify-plugin/` |
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


## Runbook Outline

# Plugin Migration — Outline (Proofed 2026-03-13)

**Requirements source:** `plans/plugin-migration/design.md` + design conversation + codebase audit + proof session

## Problem

agent-core distributes skills, agents, and hooks to projects via git submodule + symlinks.
Pain: `just sync-to-parent` ceremony, symlink breakage in worktrees, submodule version pinning across branches (tooling updates don't propagate until merge), hook path indirection (settings.json → `.claude/hooks/` symlink → `agent-core/hooks/` script), non-trivial adoption for new projects.

Current state (audited 2026-03-12): 33 skill symlinks, 13 agent symlinks, 4 hook symlinks in `.claude/` pointing to `../../agent-core/`. Additionally, 6 generated plan-specific agents (`handoff-cli-tool-*.md`: corrector, impl-corrector, implementer, task, test-corrector, tester) as regular files in `.claude/agents/`. Hooks are configured in two places: `.claude/settings.json` hooks section (referencing both `.claude/hooks/` symlinks and `agent-core/hooks/` direct paths) and `agent-core/hooks/hooks.json` (subset).

## Approach

Convert agent-core into a Claude Code plugin named `edify`. Plugin auto-discovers skills/agents/hooks (no symlinks). Both dev and consumer modes ship together:

- **Dev mode:** Submodule + `--plugin-dir ./agent-core` — only for edify-plugin development itself (editing skills requires full edify context)
- **Consumer mode:** Plugin install from marketplace — the primary deployment model for all other projects

SessionStart hook exports `$EDIFY_PLUGIN_ROOT` via `$CLAUDE_ENV_FILE` (grounded: official Claude Code mechanism, available in all subsequent Bash commands). Scripts reference `$EDIFY_PLUGIN_ROOT/bin/` — works in both modes.

Normal update path is marketplace (`claude plugin update edify`) for both modes. Dev mode uses `--plugin-dir` for instant feedback during active edify development, not for consuming updates.

## Key Decisions

- **D-1 Naming:** Plugin = `edify` (marketplace), repo = `edify-plugin` (was `agent-core`), Python package = `edify` (was `claudeutils`)
- **D-2 Hook scripts unchanged:** Scripts use `$CLAUDE_PROJECT_DIR` correctly; hooks.json commands use `$CLAUDE_PLUGIN_ROOT` to locate scripts. Moving hooks from settings.json to plugin hooks.json does not change env var availability (grounded: both vars available in all hook types)
- **D-3 Fragment distribution via skill:** `/edify:init` is a skill (needs reasoning + conditional logic), not a standalone script
- **D-4 hooks.json format:** Wrapper format `{"hooks": {"PreToolUse": [...]}}` per official Claude Code docs (grounded: code.claude.com/docs/en/plugins migration guide)
- **D-5 Justfile modularization:** `portable.just` contains the full opinionated recipe stack:
  - `claude` / `claude0` — opinionated launch wrapper (replaces system prompt, generic not domain-specific)
  - `lint` / `format` / `check` — ruff (complexity disabled), mypy, docformatter
  - `red` — permissive variant for iterative TDD work
  - `precommit` — full lint WITH ruff complexity, line/token limits, session/plan file validation
  - `test` — pytest with framework-standard flags
  - `precommit-base` — edify-plugin validators only (subset of precommit)
  - `wt-*` — manual fallbacks for `claudeutils _worktree`, used when `_worktree` is buggy and you're willing to forego auto-resolution (session.md updates, conflict resolution, validation)
  - Delivered via sync mechanism with SessionStart + UPS fallback. Default: nag. Auto-with-report is future work
  - Variables merge across import boundaries (grounded: Context7, Just docs). Projects override via `set allow-duplicate-recipes`
- **D-6 Version marker:** `.edify.yaml` in project root. YAML format (supports comments, fewer tokens than JSON). Holds plugin version + sync policy
- **D-7 Python deps (in scope):** edify-plugin scripts depend on edify CLI. SessionStart hook installs `edify==X.Y.Z` into `$CLAUDE_PLUGIN_ROOT/.venv` via `uv pip install`. Version pinned in hook script, updated with each plugin release. No global tool install, no user env pollution

## Requirements

- FR-1: Skills, agents, and hooks load via plugin auto-discovery (no symlinks)
- FR-2: `just claude` provides opinionated launch wrapper (system prompt replacement, plugin config)
- FR-3: `/edify:init` scaffolds CLAUDE.md + fragments for new projects (idempotent)
- FR-4: `/edify:update` syncs fragments + `portable.just` when plugin version changes
- FR-5: Setup hook detects stale fragments via `.edify.yaml` version comparison (SessionStart + UPS fallback), nags user
- FR-6: Portable justfile recipes importable by any project
- FR-7: Existing projects migrate by removing symlinks
- FR-8: Plan-specific agents (`*-task.md`) coexist with plugin-provided agents
- FR-9: All hooks migrate to plugin; settings.json hooks section emptied
- FR-10: SessionStart hook writes current plugin version to `.edify.yaml` — operational provenance for retrospective analysis
- FR-11: SessionStart hook installs edify CLI into plugin-local venv via `uv pip install edify==X.Y.Z`
- FR-12: `plugin.json` version and `pyproject.toml` version must match. `just release` bumps both together. Precommit check validates equality
- NFR-1: Dev mode edit-restart cycle no slower than current symlink approach
- NFR-2: No token overhead increase from plugin vs symlink loading

## Validation

| Requirement | Validation |
|-------------|------------|
| FR-1 | `claude --plugin-dir ./agent-core` → `/help` lists plugin skills; agents appear in `/agents` |
| FR-2 | `just claude` launches with system prompt replacement, skills available |
| FR-3 | Clean project + `/edify:init` → functional CLAUDE.md with `@` refs to `agents/rules/`, fragments copied |
| FR-4 | Bump `plugin.json` version, restart → `/edify:update` syncs unmodified files, skips user-edited files with warning. `--force` overwrites conflicts. `.edify.yaml` version + synced hashes updated |
| FR-5 | Stale `.edify.yaml` → first prompt shows additionalContext nag |
| FR-6 | New project with synced `portable.just` → `just claude`, `just precommit` work |
| FR-7 | Remove symlinks from `.claude/` → all functionality preserved via plugin |
| FR-8 | Plugin agents and `*-task.md` agents both discoverable, no conflicts |
| FR-9 | All hooks fire from plugin; settings.json hooks section empty |
| FR-10 | Start session → `.edify.yaml` version field matches current `plugin.json` version |
| FR-11 | Start session → `$CLAUDE_PLUGIN_ROOT/.venv/bin/edify --version` returns correct version |
| FR-12 | `plugin.json` version ≠ `pyproject.toml` version → precommit fails |
| NFR-1 | Edit skill → restart → change visible (same cycle as symlinks) |
| NFR-2 | Compare context size before/after migration (no regression) |

## Components

### 1. Plugin Manifest

- Create `agent-core/.claude-plugin/plugin.json` (name: `edify`, version matching `pyproject.toml`)
- Existing `skills/`, `agents/` directories already in correct layout for plugin auto-discovery
- Hook definitions in `hooks/hooks.json` (wrapper format, see Component 2)
- Directory stays as `agent-core/` during development — rename is cosmetic, happens last

### 2. Hook Migration

Complete hook inventory (audited from settings.json + hooks/ directory):

| Hook Script | Event | Matcher | Currently In | Action |
|------------|-------|---------|-------------|--------|
| `pretooluse-block-tmp.sh` | PreToolUse | Write\|Edit | settings.json (via .claude/ symlink) | Migrate to plugin hooks.json |
| `pretooluse-symlink-redirect.sh` | PreToolUse | Write\|Edit | settings.json (via .claude/ symlink) | **Delete** (purpose eliminated) |
| `submodule-safety.py` | PreToolUse + PostToolUse | Bash | settings.json (via .claude/ symlink) | Migrate to plugin hooks.json |
| `pretooluse-recipe-redirect.py` | PreToolUse | Bash | settings.json (direct agent-core/ path) | Migrate to plugin hooks.json |
| `pretooluse-recall-check.py` | PreToolUse | Task | settings.json (direct agent-core/ path) | Migrate to plugin hooks.json |
| `posttooluse-autoformat.sh` | PostToolUse | Write\|Edit | settings.json + hooks.json | Migrate to plugin hooks.json |
| `userpromptsubmit-shortcuts.py` | UserPromptSubmit | (none) | settings.json + hooks.json | Migrate to plugin hooks.json |
| `sessionstart-health.sh` | SessionStart | * | settings.json + hooks.json | Migrate to plugin hooks.json |
| `stop-health-fallback.sh` | Stop | * | settings.json + hooks.json | Migrate to plugin hooks.json |

**Consolidated setup hook (`edify-setup.sh`):** Single initialization script called by SessionStart, with UPS fallback via transcript scraping (check transcript_path for setup marker — if missing, run setup). Handles:
- `$CLAUDE_ENV_FILE` export of `EDIFY_PLUGIN_ROOT`
- `uv pip install edify==X.Y.Z` into plugin-local venv (FR-11)
- Version provenance write to `.edify.yaml` (FR-10)
- Version comparison + nag if stale (FR-5)
- Script is idempotent — safe to run twice

**Hook script changes required:**

| Script | Change | Rationale |
|--------|--------|-----------|
| `pretooluse-block-tmp.sh` | None | Reads file paths from stdin; no env var dependency |
| `submodule-safety.py` | None | Uses `$CLAUDE_PROJECT_DIR` correctly |
| `pretooluse-recipe-redirect.py` | Audit `$CLAUDE_PROJECT_DIR` usage | Verify env var resolution under plugin context |
| `pretooluse-recall-check.py` | Audit `$CLAUDE_PROJECT_DIR` usage | Same |
| `posttooluse-autoformat.sh` | None | Uses `$CLAUDE_PROJECT_DIR` correctly |
| `userpromptsubmit-shortcuts.py` | None | Stateless stdin-stdout |
| `sessionstart-health.sh` | Audit `$CLAUDE_PROJECT_DIR` usage | Currently uses direct project path references |
| `stop-health-fallback.sh` | Audit `$CLAUDE_PROJECT_DIR` usage | Same |
| `pretooluse-symlink-redirect.sh` | **Delete** | Purpose eliminated |

### 3. Fragment Versioning System

- Plugin version lives in `plugin.json` (single source of truth, matches `pyproject.toml` per FR-12)
- Project version + sync policy in `.edify.yaml` (YAML, supports comments)
- Setup hook reads `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json` version, compares against `.edify.yaml` version
- Mismatch → nag: "Run `/edify:update`"
- No separate `.version` file — `plugin.json` is sufficient
- `/edify:update` syncs files and updates `.edify.yaml` version field

### 4. Migration Command (`/edify:init`)

- Skill at `edify-plugin/skills/init/SKILL.md`
- Single mode: consumer (marketplace install)
- Copies fragments to `agents/rules/`, rewrites CLAUDE.md `@` refs to local copies
- Scaffolds `agents/` structure (session.md, learnings.md, jobs.md)
- CLAUDE.md scaffolding from `templates/CLAUDE.template.md`
- Writes `.edify.yaml` with version + sync policy (`nag` default)
- Idempotent: checks before acting, never destroys existing content
- No submodule detection — edify project itself doesn't run init (it IS the plugin)

`/edify:update` — separate skill, syncs fragments + `portable.just`, updates `.edify.yaml` version.

**Conflict policy for `/edify:update`:**

- **Sync targets:** `agents/rules/*` (from plugin `fragments/`), `portable.just` (from plugin root)
- **Tracking mechanism:** `.edify.yaml` stores a `synced_hashes` map — keyed by relative file path, value is content hash at last sync. Written by both `/edify:init` (initial sync) and `/edify:update` (subsequent syncs)
- **Per-file detection:** compare consumer file hash against `synced_hashes[file]` (the version last synced), not against the current plugin version
- **Cases:**
  - File missing in consumer → copy from plugin, record hash (new file)
  - Consumer hash == synced hash → user hasn't edited → **safe to update** with new plugin version, record new hash
  - Consumer hash ≠ synced hash → user has local edits → **conflict: warn and skip** (report file path, do not overwrite)
  - No synced hash entry (legacy/first run) → treat as conflict (safe default)
- **Never silent overwrite:** Conflicting files are never replaced without explicit user intent
- **`--force` flag:** Overwrites conflicting files with plugin version. Applies to all conflicting files (no per-file granularity in v1 — user runs `--force` after reviewing the conflict list). Updates synced hashes for overwritten files
- **Output:** Summary — files updated (safe), files copied (new), files conflicting (with paths), files current (no change). On `--force`: files overwritten
- **Rationale:** Consumer may have local edits to fragments (project-specific behavioral rules). Comparing against last-synced version (not current plugin version) correctly distinguishes "user edited" from "plugin updated" — routine plugin updates flow through without false conflicts

### 5. Justfile Modularization

- `portable.just` contains the full opinionated recipe stack (see D-5 for full list)
- `wt-*` recipes are manual fallbacks for `claudeutils _worktree` — used when `_worktree` is buggy and you're willing to forego auto-resolution
- Delivered to consuming projects via `/edify:update` (synced alongside fragments)
- Variables merge across import boundaries (grounded via Context7)
- Projects override individual recipes via `set allow-duplicate-recipes` — shallower definitions win
- Root justfile in consuming project: `import 'portable.just'` (synced copy) + project-specific recipes

### 6. Symlink Cleanup

Execute **last** — only after plugin verified working.

- Remove 33 skill symlinks from `.claude/skills/`
- Remove 13 agent symlinks from `.claude/agents/` (preserve 6 `handoff-cli-tool-*.md` regular files)
- Remove 4 hook symlinks from `.claude/hooks/`
- Delete `pretooluse-symlink-redirect.sh` from hooks/
- Remove ALL hook entries from `.claude/settings.json` (hooks section removed entirely)
- Remove `sync-to-parent` recipe from justfile
- Update `.gitignore` if needed

### 7. Script Path Updates + Permissions

- `bin/` scripts referenced from skills, settings.json, and justfile
- After rename: paths change from `agent-core/bin/...` to `edify-plugin/bin/...`
- `settings.json` permissions.allow: update `agent-core/bin/` → `edify-plugin/bin/`
- `settings.json` sandbox.excludedCommands: update path
- Mechanical `agent-core/` → `edify-plugin/` replacement
- CLI migration (moving scripts to edify CLI proper) is separate future work

### 8. Documentation Updates

- `fragments/project-tooling.md` — remove `sync-to-parent` references
- `fragments/claude-config-layout.md` — remove symlink section
- `fragments/sandbox-exemptions.md` — remove `sync-to-parent` subsection
- `fragments/delegation.md` — update examples referencing `sync-to-parent`
- Any fragment referencing `agent-core/` paths → update to `edify-plugin/`

## Scope

**In:**
- Plugin manifest and structure (`.claude-plugin/plugin.json`)
- Hook migration to plugin hooks.json (all 9 surviving hooks + consolidated setup hook)
- Fragment versioning via `.edify.yaml` + `plugin.json`
- Migration commands (`/edify:init`, `/edify:update`)
- Justfile modularization (`portable.just`, full opinionated stack)
- Symlink removal and settings.json cleanup
- Script path updates (mechanical rename)
- Documentation updates
- Plugin-local venv for edify CLI via `uv`
- Marketplace setup
- Directory rename (`agent-core/` → `edify-plugin/`, cosmetic, last step)

**Out:**
- Fragment content changes (behavioral rules stay as-is)
- Workflow skill redesign
- Breaking changes to skill interfaces
- New hook logic (existing hooks migrate as-is, except symlink-redirect deletion)
- CLI migration (moving bin/ scripts to edify CLI — separate task)
- Auto-sync-with-report mode (future work, nag is default)
- Memory submodule setup (active-recall scope, S-J)

## Implementation Strategy

**Bootstrap constraint:** edify tooling must remain functional throughout migration. Cannot rename directory first — breaks all paths.

**Strategy:**
- Build plugin structure inside existing `agent-core/` (add `.claude-plugin/plugin.json`, `hooks/hooks.json`)
- `--plugin-dir ./agent-core` works — plugin name is `edify` regardless of directory name
- Verify plugin loading alongside existing symlinks (both paths work during transition)
- Symlink cleanup + settings.json hook removal once plugin verified
- Directory rename (`agent-core/` → `edify-plugin/`) is cosmetic — last step
- All changes merge to main atomically via branch merge
- No rollback section needed — revert = don't merge

## Design Corrections

Issues found in `design.md` during this refresh:

1. **D-4 hooks.json format is wrong.** Design says direct format; official Claude Code docs confirm wrapper format `{"hooks": {...}}` for plugin hooks.json
2. **Hook inventory incomplete.** Design lists 4 hooks; current codebase has 10 hook scripts with 8 distinct bindings across 5 event types
3. **Artifact counts stale.** Design says "16 skills, 12 agents"; audit shows 33 skills, 13 agents, 6 generated agents, 27 fragments
4. **Dual hook configuration not addressed.** Current settings.json hooks reference both `.claude/hooks/` (symlinks) and `agent-core/hooks/` (direct). Migration must consolidate both into single plugin hooks.json
5. **D-8 (consumer mode deferred) is wrong.** `$CLAUDE_ENV_FILE` mechanism resolves the path resolution blocker. Both modes ship together

## Resolved Questions

- **Plugin name:** `edify` (Latin *aedificare* = "to build" + "to instruct")
- **Fragment directory:** `agents/rules/` for consumer projects
- **Init idempotency:** Always idempotent; `/edify:update` is separate (sync only)
- **Hook ownership:** All hooks are portable, all move to plugin
- **Agent namespace:** Plugin agents prefixed `edify:agent-name`, no collision with local `*-task.md`
- **`$CLAUDE_PLUGIN_ROOT`:** Confirmed available (official plugins use it)
- **hooks.json format:** Wrapper format (grounded)
- **Justfile import:** Variables merge, shallower definitions override (grounded via Context7)
- **Python dependency mechanism:** Plugin-local venv via `uv pip install` in SessionStart hook
- **Version scheme:** Semver, marketplace-driven, matches PyPI. Single version across `plugin.json` and `pyproject.toml`
- **Bootstrap strategy:** Build plugin inside `agent-core/`, rename last
- **Update conflict policy:** Warn-and-skip for user-edited files, auto-update for unmodified. Detection via synced content hashes in `.edify.yaml`. `--force` for intentional overwrite

## Risks

- **R-1: hooks.json format uncertainty.** Outline corrects design.md D-4 based on official plugin docs. Mitigation: validate with `claude --plugin-dir` before symlink cleanup
- **R-2: Hook env var resolution under plugin context.** Four hooks need auditing for `$CLAUDE_PROJECT_DIR` usage under plugin runtime. Mitigation: audit each script before migration
- **R-3: `uv` availability on consumer machines.** D-7 depends on `uv` being installed. Mitigation: setup hook checks for `uv`, falls back to `pip` or warns

## Open Questions

- **Hook script env var audit (FR-9):** `recipe-redirect`, `recall-check`, `sessionstart-health`, `stop-health-fallback` need auditing for `$CLAUDE_PROJECT_DIR` vs direct path usage
- **Settings.json residual:** With hooks moved to plugin, settings.json retains: permissions, sandbox config, plansDirectory, attribution, enabledPlugins. File stays, hooks section removed
- **`just release` coordination (FR-12):** Exact mechanism for bumping `plugin.json` + `pyproject.toml` versions together

## Common Context



## Resolved Recall

# When Simple Routing Bypasses Inline Lifecycle
**Decision Date:** 2026-03-11

**Anti-pattern:** Simple classification routes to "direct execution" — recall, explore, edit, done. Bypasses /inline lifecycle: no integration-test gate, no review dispatch, no triage feedback, no deliverable-review chain.

**Correct pattern:** Simple routes through `/inline plans/<job> execute` like Moderate and Complex. /inline provides the review gating and workflow continuation that "direct execution" lacks. The classification determines design ceremony, not execution ceremony. Same class as Moderate prose bypassing /runbook.

Source: agents/decisions/pipeline-review.md
---
# When Checking Complexity Before Expansion
**Decision Date:** 2026-02-05

**Decision:** Check complexity BEFORE expansion; callback to previous level if too large.

**Anti-pattern:** Expand all cycles regardless of complexity, discover problems late.

**Callback levels:** step → outline → design → design outline → requirements (human input)

**Fast paths:** Pattern cycles get template+variations; trivial phases get inline instructions.

**Key insight:** Complexity assessment is planning concern (sonnet/opus), not executor concern (haiku). Haiku optimizes for completion, not scope management.

**Impact:** Catch structure problems early, prevent executor overload.

Source: agents/decisions/workflow-planning.md
---
# When Triaging Behavioral Code Changes As Simple
**Decision Date:** 2026-02-21

**Anti-pattern:** Assessing complexity from conceptual simplicity ("just read a config file") rather than structural criteria. Resolving ambiguity downward due to implementation eagerness.

**Correct pattern:** Simple criteria include "no behavioral code changes." Behavioral code (new functions, changed logic paths, conditional branches) routes to Moderate → `/runbook` → TDD phase-type assessment. Test discipline gated at triage, not emergent from routing.

**Root cause chain:** Motivated reasoning → resolved ambiguity downward → Simple path had no test gate → behavioral code shipped untested.

Source: agents/decisions/workflow-planning.md
---
# When Reading Design Classification Tables
**Decision:** Read design classification tables LITERALLY. Apply judgment only where design says "use judgment".

**Anti-pattern:** Inventing classification heuristics when design provides explicit rules (e.g., "subsections = structural" when design table shows all ##+ as semantic).

**Rationale:** Design decisions are intentional. Overriding them based on assumptions contradicts designer's intent.

**Process fix:** Skill fixes outlined for `/design` and `/plan-adhoc`.

**Impact:** Implementation matches design intent without interpretation drift.

Source: agents/decisions/implementation-notes.md
---
# How to Validate Migration Conformance
**Decision Date:** 2026-02-05

**Decision:** Compare Python implementation against original shell spec at completion.

When migrating from external references (shell prototypes, API specs, visual mockups), tests must bake the expected behavior from the reference directly into assertions. The reference is consumed at test authoring time, and tests become permanent executable contracts that validate conformance throughout development.

### .Tests as Executable Contracts

When design includes external reference (shell prototype, API spec, visual mockup), tests bake expected behavior into assertions. The reference is consumed at authoring time, and tests become permanent living documentation. For example, statusline-parity tests should assert exact expected strings from the shell reference (e.g., `🥈 sonnet \033[35m…`), not just structure such as "contains emoji".

### .Exact Expected Strings Requirement

For conformance work, test assertions must include exact expected output from the reference. This eliminates translation loss between specification and implementation. It also addresses root cause RC5: "Visual Parity Validated" false completion claims become detectable when tests include exact expected strings from the reference.

### .Conformance Exception to Prose Descriptions

Standard TDD uses prose descriptions instead of full test code (per workflow-advanced.md). Conformance work is an exception: prose descriptions MUST include exact expected strings from the reference. This is not full test code — it is precise prose.

**Example contrast:**

| Standard prose | Conformance prose (with exact strings) |
|---|---|
| "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` emoji followed by `\033[35msonnet\033[0m` escape sequence with double-space separator" |

### .Conformance Pattern

**Pattern:** Delegated to exploration agent, writes detailed conformance matrix.

**Benefits:** Catches presentation/visual gaps that unit tests miss.

**Example:** statusline-wiring found all 5 requirements met but missing emojis/bars/colors.

**Impact:** Behavioral equivalence verification beyond functional testing, with exact specifications preventing translation loss.

**See also:** TDD RED Phase: Behavioral Verification (line 69) for assertion quality requirements that complement conformance testing.

Source: agents/decisions/testing.md
---
# When Hook Commands Use Relative Paths
**Decision Date:** 2026-02-28

**Anti-pattern:** Hook command in settings.json uses relative path (`.claude/hooks/submodule-safety.py`). After agent cwd drifts (e.g., `cd subdir && ...`), the relative path resolves against the new cwd — hook script not found. Hook errors are non-blocking in Claude Code, so the guarded command proceeds without the hook.

**Irony:** The submodule-safety hook (designed to block cwd drift) was itself disabled by cwd drift.

**Correct pattern:** All hook commands must use `$CLAUDE_PROJECT_DIR/` prefix for absolute resolution. Claude Code sets this env var to the project root regardless of cwd.

**Evidence:** Agent ran 4+ bash commands from `agent-core/` subdirectory without the submodule-safety hook blocking. Hook errors visible on `git submodule status` confirmed the hook script wasn't found.

Source: agents/decisions/hook-patterns.md
---
# When Using Session Start Hooks
**Context:** SessionStart hook output is discarded for new interactive sessions.

**Issue:** [#10373](https://github.com/anthropics/claude-code/issues/10373) — `qz("startup")` never called for new interactive sessions.

**Works:** After `/clear`, `/compact`, or `--resume`.

**Workaround:** Use `@agents/session.md` in CLAUDE.md for task context (already loaded).

**Impact:** Don't build features depending on SessionStart until fixed upstream.

Source: agents/decisions/hook-patterns.md
---
# When Custom Agents Need Session Restart For Discoverability
**Decision Date:** 2026-02-24

**Anti-pattern:** Using plan-specific agents as `subagent_type` values in the same session they were created. They aren't indexed until restart.

**Correct pattern:** Plan-specific agents in `.claude/agents/` are discoverable as Task `subagent_type` values only after session restart. The prepare-runbook.py → restart → orchestrate workflow naturally includes this boundary. Built-in types with prompt injection work as fallback when restart isn't feasible.

**Evidence:** `hb-p1` through `hb-p5` not discoverable in creating session. Confirmed discoverable in subsequent sessions.

Source: agents/decisions/project-config.md
---
# When Declaring Phase Type
Runbook phases declare type: `tdd`, `general` (default), or `inline`.

Type determines:
- **Expansion format:** TDD → RED/GREEN cycles. General → task steps with script evaluation. Inline → pass-through (no decomposition).
- **Review criteria:** TDD → TDD discipline. General → step quality. Inline → vacuity, density, dependency ordering (lighter — no step/script/TDD checks).
- **LLM failure modes:** Apply universally regardless of type.
- **Orchestration delegation model:** TDD/general → per-step agent delegation. Inline → orchestrator-direct (reads phase content from runbook, executes edits without Task dispatch). Batching consecutive inline phases deferred pending empirical data.

Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, checkpoints.

### When Phase Qualifies As Inline

A phase qualifies as `inline` when outcome is fully determined by instruction + target file state:
- No runtime feedback loop (tests, scripts, external state)
- Prose edits, config additions, cross-reference insertions, mechanical content application
- All decisions pre-resolved in design

Inline phases in orchestrator-plan.md use `Execution: inline` (vs `Execution: steps/step-N-M.md` for general/TDD phases). prepare-runbook.py skips step-file generation for inline phases.

Source: agents/decisions/pipeline-contracts.md
---
# When Phase Qualifies As Inline
A phase qualifies as `inline` when outcome is fully determined by instruction + target file state:
- No runtime feedback loop (tests, scripts, external state)
- Prose edits, config additions, cross-reference insertions, mechanical content application
- All decisions pre-resolved in design

Inline phases in orchestrator-plan.md use `Execution: inline` (vs `Execution: steps/step-N-M.md` for general/TDD phases). prepare-runbook.py skips step-file generation for inline phases.

Source: agents/decisions/pipeline-contracts.md


---

**Scope enforcement:** Execute ONLY the step file assigned by the orchestrator. Do not read ahead in the runbook or execute other step files.

**Clean tree requirement:** Commit all changes before reporting success. The orchestrator will reject dirty trees — there are no exceptions.
