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
| FR-4 | Bump `plugin.json` version, restart → `/edify:update` syncs files, `.edify.yaml` version matches |
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

## Risks

- **R-1: hooks.json format uncertainty.** Outline corrects design.md D-4 based on official plugin docs. Mitigation: validate with `claude --plugin-dir` before symlink cleanup
- **R-2: Hook env var resolution under plugin context.** Four hooks need auditing for `$CLAUDE_PROJECT_DIR` usage under plugin runtime. Mitigation: audit each script before migration
- **R-3: `uv` availability on consumer machines.** D-7 depends on `uv` being installed. Mitigation: setup hook checks for `uv`, falls back to `pip` or warns

## Open Questions

- **Hook script env var audit (FR-9):** `recipe-redirect`, `recall-check`, `sessionstart-health`, `stop-health-fallback` need auditing for `$CLAUDE_PROJECT_DIR` vs direct path usage
- **Settings.json residual:** With hooks moved to plugin, settings.json retains: permissions, sandbox config, plansDirectory, attribution, enabledPlugins. File stays, hooks section removed
- **`just release` coordination (FR-12):** Exact mechanism for bumping `plugin.json` + `pyproject.toml` versions together
