# Plugin Migration — Runbook Outline

**Design source:** `plans/plugin-migration/outline.md` (proofed, authoritative — supersedes design.md)
**Recall artifact:** `plans/plugin-migration/recall-artifact.md`

## Requirements Mapping

| Step | Files | Requirements |
|------|-------|-------------|
| 1.1 | `plugin.json` (create) | FR-1 |
| 1.2 | `hooks/hooks.json` (rewrite) | FR-1, FR-9 |
| 1.3 | — (validation checkpoint) | FR-1, FR-8, NFR-1 |
| 5.1 | `.edify.yaml` (create) | FR-5, FR-10 |
| 5.2 | precommit script/justfile | FR-12 |
| 2.1 | 4 hook scripts (audit) | FR-9 |
| 2.2 | hook scripts (fix), `symlink-redirect` (delete) | FR-9 |
| 2.3 | `edify-setup.sh` (create) | FR-5, FR-10, FR-11 |
| 2.4 | `hooks/hooks.json` (edit) | FR-9 |
| 3.1 | `skills/init/SKILL.md`, `CLAUDE.template.md` (create) | FR-3 |
| 3.2 | `skills/update/SKILL.md` (create) | FR-4 |
| 4.1 | `portable.just` (create) | FR-2, FR-6 |
| 4.2 | `justfile` (edit) | FR-2, FR-6 |
| 6.1 | `.claude/` symlinks (delete), `settings.json` (edit) | FR-7, FR-9 |
| 6.2 | fragments (edit) | FR-7 |
| 6.3 | — (validation checkpoint) | FR-1, FR-7, FR-9 |
| 7 | directory rename + all `plugin/` path refs | — |
| NFR-1 | validated at Step 1.3 | NFR-1 |
| NFR-2 | architectural (same content, different mechanism) | NFR-2 |

## Key Decisions Reference

- D-1 (naming): outline.md §Key Decisions
- D-2 (hook scripts unchanged): outline.md §Component 2, hook script changes table
- D-3 (fragment distribution via skill): outline.md §Component 4
- D-4 (hooks.json wrapper format): outline.md §Key Decisions, Design Corrections §1
- D-5 (justfile modularization): outline.md §Key Decisions, §Component 5
- D-6 (version marker .edify.yaml): outline.md §Key Decisions
- D-7 (python deps in scope): outline.md §Key Decisions

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Phase-specific guidance:**
- Phase 2 hook migration: outline Component 2 has complete hook inventory table and script-change table — use literally, do not re-audit
- Phase 2 edify-setup.sh: consolidated setup hook is new code with env var export, venv install, version comparison — needs careful specification. Recall entry "when using session start hooks" documents SessionStart output discard (#10373) — UPS fallback design must account for this
- Phase 3 skills are agentic prose artifacts — opus model, prose review cycles
- Phase 4: `portable.just` needs its own minimal bash prolog (only `fail`, `visible`, color variables) — see outline §Component 5 for details on import boundary constraints
- Phase 6 symlink cleanup: mechanical but must preserve handoff-cli-tool-*.md regular files

**Checkpoint guidance:**
- Phase 1 ends with checkpoint (Step 1.3) — gates all downstream phases. Requires tmux verification mechanism (design needed)
- Phase 2 ends with checkpoint (Step 2.4) — verify setup hook fires and env vars propagate (same tmux mechanism)
- Phase 6 ends with checkpoint (Step 6.3) — final validation gate before Phase 7 rename

**Hook inventory note:**
- Step 1.2 lists all 9 surviving hooks explicitly — expansion should use outline.md Component 2 table for matchers and event types, not re-audit
- `posttooluse-autoformat.sh` is included in hook count but marked "None" for script changes — no audit needed, just migration to hooks.json

**Phase ordering:**
- Phase 5 runs immediately after Phase 1 (creates `.edify.yaml` before Phase 2's setup hook)
- Phase 7 (inline) is the directory rename — orchestrator executes directly, no step files needed

**Consolidation candidates:**
- Phase 5 has only 2 steps (Low-Medium complexity) but creates `.edify.yaml` needed by Phase 2 — must stay separate due to dependency ordering
- Step 6.2 (fragment updates) is low-complexity mechanical work — could inline into Step 6.1, but keeping separate preserves clear separation between destructive deletion and content updates

**Unresolved design dependencies (flagged, not fixable by reviewer):**
- Phase 4 depends on D-5 redesign (thematic module boundaries). Expansion must either resolve D-5 first or execute with single `portable.just` as designed
- Step 1.3 tmux verification mechanism needs design before execution. Applies to Steps 2.4, 6.1, 6.3 verification as well

**Bootstrap constraint:**
- plugin/ must remain functional throughout migration
- Plugin verified alongside existing symlinks before symlink removal (Phase 6)
- Recall entry "when hook commands use relative paths" applies: all hooks.json commands must use `$CLAUDE_PLUGIN_ROOT` prefix for absolute resolution

---

### Phase 1: Plugin manifest and structure (type: general)

Create the plugin structure inside existing `plugin/` directory.

- Step 1.1: Create `.claude-plugin/plugin.json`
  - Name: `edify`, version matching `pyproject.toml` current version
  - Target: `plugin/.claude-plugin/plugin.json`
  - Verify: `cat plugin/.claude-plugin/plugin.json` shows valid JSON with name and version
  - Files: `plugin/.claude-plugin/plugin.json` (create), `pyproject.toml` (read for version)

- Step 1.2: Create plugin `hooks/hooks.json` in wrapper format
  - Migrate all hook definitions from `.claude/settings.json` hooks section into `plugin/hooks/hooks.json`
  - Wrapper format: `{"hooks": {"PreToolUse": [...], ...}}` per D-4
  - All commands use `$CLAUDE_PLUGIN_ROOT/hooks/` prefix (not `$CLAUDE_PROJECT_DIR`)
  - Omit `pretooluse-symlink-redirect.sh` (deleted in Phase 2)
  - Include all 9 surviving hooks: `pretooluse-block-tmp.sh`, `submodule-safety.py` (PreToolUse+PostToolUse), `pretooluse-recipe-redirect.py`, `pretooluse-recall-check.py`, `posttooluse-autoformat.sh`, `userpromptsubmit-shortcuts.py`, `sessionstart-health.sh`, `stop-health-fallback.sh` (see outline.md Component 2 for full inventory)
  - Verify: JSON validates, all 9 surviving hooks present with correct matchers
  - Files: `plugin/hooks/hooks.json` (rewrite from current subset), `.claude/settings.json` (read for current bindings)

- Step 1.3: Validate plugin loading
  - Verify FR-1 (auto-discovery), NFR-1 (dev mode cycle)
  - Verify FR-8: plan-specific agents (`.claude/agents/handoff-cli-tool-*.md`) coexist with plugin agents — both discoverable, no conflicts
  - **Requires design:** programmatic Claude CLI verification via tmux (send keys, capture output, check results). Find existing tooling for tmux-based CLI interaction before building custom
  - Validation checkpoint — STOP and report results before proceeding

### Phase 5: Version coordination and precommit (type: general)

Wire version consistency and release coordination. Runs early — creates `.edify.yaml` before Phase 2's setup hook needs it.

- Step 5.1: Create `.edify.yaml` schema and initial file
  - YAML format with: `version`, `sync_policy` (default: nag)
  - Initial version from current `pyproject.toml`
  - Target: `.edify.yaml` in project root (for this project as dogfood)
  - Files: `.edify.yaml` (create)

- Step 5.2: Add version consistency precommit check (FR-12)
  - Check: `plugin.json` version == `pyproject.toml` version
  - Add to `just precommit` or as standalone check script
  - Wire into `just release` to bump both together
  - Files: precommit script or justfile recipe (create/edit), `justfile` (edit for release)

### Phase 2: Hook migration and setup hook (type: general)

Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage. Phase 5 must complete first (`.edify.yaml` exists for setup hook to read/update).

- Step 2.1: Audit hook scripts for env var usage
  - Scripts needing audit (from outline Component 2 table): `pretooluse-recipe-redirect.py`, `pretooluse-recall-check.py`, `sessionstart-health.sh`, `stop-health-fallback.sh`
  - Check each for `$CLAUDE_PROJECT_DIR` usage — must resolve correctly under plugin context
  - Check for hardcoded `plugin/` paths that need `$CLAUDE_PLUGIN_ROOT` substitution
  - Record findings per script: no-change-needed or specific edits required
  - Files: 4 scripts in `plugin/hooks/`

- Step 2.2: Apply hook script fixes from audit
  - Apply any env var fixes identified in Step 2.1
  - Delete `pretooluse-symlink-redirect.sh` (purpose eliminated by plugin migration)
  - Verify remaining scripts have no relative path references (recall: hook commands must use absolute paths)
  - Files: affected scripts from audit + `plugin/hooks/pretooluse-symlink-redirect.sh` (delete)
  - Depends on: Step 2.1

- Step 2.3: Create consolidated `edify-setup.sh`
  - New file: `plugin/hooks/edify-setup.sh`
  - Handles (per outline Component 2):
    - Export `EDIFY_PLUGIN_ROOT` via `$CLAUDE_ENV_FILE` (grounded: official mechanism)
    - `uv pip install edify==X.Y.Z` into `$CLAUDE_PLUGIN_ROOT/.venv` (FR-11) — with `uv` availability check, pip fallback (R-3). Note: package is currently `edify` on PyPI; rename to `edify` is separate work
    - Write current plugin version to `.edify.yaml` (FR-10)
    - Compare `.edify.yaml` version against plugin version, nag if stale (FR-5)
  - UPS fallback: transcript scraping for setup marker (if SessionStart discarded — recall: #10373)
  - Script must be idempotent
  - Verify: script runs without error, `.edify.yaml` updated, env var available in subsequent commands
  - Files: `plugin/hooks/edify-setup.sh` (create)

- Step 2.4: Wire setup hook into hooks.json
  - Post-phase state: `plugin/hooks/hooks.json` (rewritten in Step 1.2) contains all 9 surviving hooks in wrapper format
  - Add SessionStart entry for `edify-setup.sh` in `plugin/hooks/hooks.json`
  - Ensure it runs before `sessionstart-health.sh` (setup provides env vars health check may need)
  - Verify: restart session → setup hook fires → env vars available (same tmux verification mechanism as Step 1.3)
  - Validation checkpoint — STOP and report Phase 2 results before proceeding
  - Files: `plugin/hooks/hooks.json` (edit)
  - Depends on: Steps 2.2, 2.3

### Phase 3: Migration skills (type: general, model: opus)

Create `/edify:init` and `/edify:update` skills — agentic prose artifacts requiring opus.

- Step 3.1: Create `/edify:init` skill
  - New skill at `plugin/skills/init/SKILL.md`
  - **Conversational, not predetermined recipe.** No real consumer use case yet — over-specifying behavior bakes in unvalidated assumptions
  - Skill loads reference material (outline Component 4, fragment inventory, template) and discusses setup with user
  - Reference points: fragment list, `agents/` structure, CLAUDE.md template, `.edify.yaml` format
  - Idempotent: check before acting, never destroy existing content
  - Need to create template: `plugin/templates/CLAUDE.template.md`
  - Files: `plugin/skills/init/SKILL.md` (create), `plugin/templates/CLAUDE.template.md` (create)

- Step 3.2: Create `/edify:update` skill
  - New skill at `plugin/skills/update/SKILL.md`
  - Behavior: sync fragments + `portable.just`, update `.edify.yaml` version
  - Separate from init — update is sync-only, not scaffolding
  - Files: `plugin/skills/update/SKILL.md` (create)

### Phase 4: Justfile modularization (type: general)

Extract portable recipes and update root justfile.

**Depends on D-5 redesign:** Current D-5 specifies a single `portable.just`. Thematic modules (e.g., `lint.just`, `test.just`, `claude.just`, `worktree.just`) are the better design — consumers import only what they need, no `allow-duplicate-recipes` override mechanism. Module boundaries need design work before this phase executes.

- Step 4.1: Create portable justfile module(s)
  - Extract portable recipe stack from current `justfile` (per D-5 list):
    - `claude` / `claude0` — opinionated launch wrapper (system prompt replacement, plugin config) (FR-2)
    - `lint` / `format` / `check` — ruff, mypy, docformatter
    - `red` — permissive TDD variant
    - `precommit` — full lint with complexity
    - `precommit-base` — edify-plugin validators only
    - `test` — pytest with framework flags
    - `wt-*` — manual worktree fallbacks (per D-5: included in portable stack)
  - Do NOT include `release` (project-specific)
  - Each module needs its own minimal bash prolog (`fail`, `visible`, color variables) — cannot rely on root justfile's `bash_prolog`
  - Target: `plugin/` (module structure TBD by D-5 redesign)
  - Files: justfile module(s) (create)

- Step 4.2: Update root justfile to import portable modules
  - Import module(s) from `plugin/`
  - Remove recipes that moved to portable modules
  - Keep project-specific recipes (release, line-limits, project-specific helpers)
  - Keep `bash_prolog` for project-specific helper functions
  - Verify: `just claude` launches with system prompt, skills available (FR-2)
  - Verify: `just --list` shows both imported and project-specific recipes
  - Regenerate `.cache/just-help.txt` and `.cache/just-help-edify-plugin.txt` (imported recipes change `just --list` output)
  - Files: `justfile` (edit), `.cache/just-help*.txt` (regenerate)
  - Depends on: Step 4.1

### Phase 6: Symlink cleanup, settings migration, and doc updates (type: general)

Execute after plugin verified working. Irreversible within session.

- Step 6.1: Remove symlinks and clean settings.json
  - Post-phase state: `plugin/hooks/hooks.json` contains all 9 surviving hooks (Phase 1+2), `plugin/.claude-plugin/plugin.json` exists (Phase 1), `plugin/hooks/edify-setup.sh` wired into hooks.json (Phase 2)
  - Remove 33 skill symlinks from `.claude/skills/`
  - Remove 13 agent symlinks from `.claude/agents/` (PRESERVE 6 `handoff-cli-tool-*.md` regular files)
  - Remove 4 hook symlinks from `.claude/hooks/`
  - Remove ALL hook entries from `.claude/settings.json` hooks section
  - Remove `sync-to-parent` recipe from `plugin/justfile`
  - Remove deny rules from `settings.json`: `Write(.claude/skills/*)`, `Write(.claude/agents/*)`, `Write(.claude/hooks/*)`, `Bash(ln:*)` — no longer needed
  - Update `.gitignore` if needed
  - Verify plugin still discovers all skills/agents/hooks (same tmux verification mechanism as Step 1.3)
  - Files: `.claude/skills/*` (delete symlinks), `.claude/agents/*` (delete symlinks only), `.claude/hooks/*` (delete symlinks), `.claude/settings.json` (edit), `justfile` (edit)
  - Depends on: Phases 1, 2, 5 (plugin fully verified, version coordination in place)

- Step 6.2: Update fragments and documentation
  - `fragments/project-tooling.md`: remove `sync-to-parent` references
  - `fragments/claude-config-layout.md`: remove symlink section
  - `fragments/sandbox-exemptions.md`: remove `sync-to-parent` subsection
  - `fragments/delegation.md`: update examples referencing `sync-to-parent`
  - Files: 4 fragments in `plugin/fragments/` (edit)
  - Depends on: Step 6.1

- Step 6.3: Validate migration completeness
  - FR-1: plugin auto-discovery works without symlinks
  - FR-7: all functionality preserved
  - FR-9: all hooks fire from plugin, settings.json hooks empty
  - NFR-2: validated architecturally — same content loaded, different mechanism. No empirical measurement needed
  - Run `just precommit` — full validation gate
  - Validation checkpoint — STOP and report results before Phase 7
  - Depends on: Steps 6.1, 6.2

### Phase 7: Directory rename (type: inline)

Rename `plugin/` → `edify-plugin/` and update all references. All decisions pre-resolved, mechanical replacement.
Depends on: Phase 6 (symlinks removed, migration validated)

- `mv plugin/ edify-plugin/`
- `settings.json` `permissions.allow`: update all `plugin/bin/` → `edify-plugin/bin/`
- `settings.json` `sandbox.excludedCommands`: update `plugin/bin/prepare-runbook.py` → `edify-plugin/bin/prepare-runbook.py`
- `justfile`: update import paths from `plugin/` → `edify-plugin/`
- CLAUDE.md `@`-references: update `plugin/` → `edify-plugin/`
- Any fragment, skill, or agent referencing `plugin/` paths
- `--plugin-dir ./plugin` → `--plugin-dir ./edify-plugin` in justfile `claude` recipe
- Verify: `just precommit` passes, `just claude` launches correctly

---

## Phase Dependencies

```
Phase 1 (manifest) → Phase 5 (versioning) → Phase 2 (hooks) → Phase 6 (cleanup) → Phase 7 (rename)
Phase 3 (skills) — independent after Phase 1
Phase 4 (justfile) — independent after Phase 1, depends on D-5 redesign
Phase 6 (cleanup) — depends on Phases 1, 2, 5 (plugin verified, version coordination in place). Phases 3, 4 are not strict dependencies (existing skills already discoverable) but should complete first for clean validation
```

Parallelizable after Phase 5: Phases 2, 3, 4 are independent.
Phase 5 runs immediately after Phase 1 (creates `.edify.yaml` before Phase 2's setup hook needs it).

## Complexity Per Phase

| Phase | Items | Complexity | Model |
|-------|-------|------------|-------|
| 1: Plugin manifest | 3 | Medium (new structure + validation design) | Sonnet |
| 5: Version coordination | 2 | Low-Medium (wiring) | Sonnet |
| 2: Hook migration | 4 | High (audit + new setup hook) | Sonnet (2.3 may need opus for setup script design) |
| 3: Migration skills | 2 | High (agentic prose) | Opus |
| 4: Justfile modularization | 2 | Medium (depends on D-5 redesign) | Sonnet |
| 6: Symlink cleanup + docs | 3 | Medium (careful deletion + fragment updates + validation) | Sonnet |
| 7: Directory rename | inline | Low (mechanical replacement) | Sonnet |
