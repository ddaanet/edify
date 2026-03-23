# Edify Rename

## Requirements

### Functional Requirements

**FR-1: GitHub submodule repo rename**
Rename `ddaanet/agent-core` to `ddaanet/edify-plugin` on GitHub. GitHub auto-redirects the old URL. Acceptance: `git ls-remote git@github.com:ddaanet/edify-plugin.git` succeeds.

**FR-2: Submodule URL update**
Update `.gitmodules` URL from `git@github.com:ddaanet/agent-core.git` to `git@github.com:ddaanet/edify-plugin.git`. Run `git submodule sync` to propagate. Acceptance: `git submodule status` resolves correctly.

**FR-3: Submodule directory rename**
`git mv agent-core plugin` — rename the submodule directory. Acceptance: `ls plugin/.claude-plugin/plugin.json` exists, `ls agent-core/` fails.

**FR-4: Path propagation — config files**
Update all `agent-core` references in: `.gitmodules`, `pyproject.toml`, `justfile`, `CLAUDE.md`, `.claude/settings.json`, `.claude/rules/*.md`. Acceptance: zero `agent-core` matches AND `plugin/` references resolve to existing paths.

**FR-5: Path propagation — source code**
Update all `agent-core` references in `src/` (6 files, 40 occurrences). Mostly worktree/merge code referencing the submodule name. Acceptance: zero `agent-core` matches, `plugin/` refs resolve, `just test` passes.

**FR-6: Path propagation — tests**
Update all `agent-core` references in `tests/` (41 files, 106 occurrences). Fixtures, helpers, test assertions. Acceptance: zero `agent-core` matches, `just test` passes.

**FR-7: Path propagation — agentic prose**
Update `agent-core` references in skills, fragments, agents, decisions, and other agentic prose within `plugin/` (post-rename) and `agents/`. Acceptance: zero `agent-core` matches in `plugin/` and `agents/` (excluding plan artifacts).

**FR-8: Path propagation — active plans**
Update `agent-core` references in plan directories with non-delivered status. Acceptance: active plan files reference `plugin/` paths.

**FR-9a: Python package rename**
Rename Python package directory: `src/claudeutils/` → `src/edify/`, all internal imports updated. Acceptance: `import edify` succeeds. `just test` passes.

**FR-9b: CLI entry point rename**
Rename CLI command from `claudeutils` to `edify`. Update all 133 skill/agent references to `claudeutils` command → `edify`. Update `pyproject.toml` entry points. Acceptance: `edify --help` works, zero `claudeutils` command references in skills/agents.

**FR-9c: PyPI distribution name**
Claim `edify` on PyPI via PEP 541 (current holder: abandoned since Dec 2022, 33 downloads/month). Update `pyproject.toml` `name` field and `sessionstart-health.sh` install target. Non-blocking for other rename work — PyPI claim runs in parallel. Acceptance: `pip install edify` installs this package.

**FR-9d: Update .claude/rules for plugin ownership**
Rules files in `.claude/rules/` reference `.claude/agents/**/*`, `.claude/hooks/**/*`, `.claude/skills/**/*` in their `paths:` frontmatter — these are now plugin-managed artifacts, not user-editable. Update rules to reflect that editing happens in `plugin/` source, not `.claude/` output. Acceptance: no rules reference `.claude/agents/`, `.claude/hooks/`, or `.claude/skills/` as editable paths.

**FR-10: Delete delivered plans**
Remove all plan directories with `delivered` status except `plans/retrospective/`. Before deleting each plan, read its outline or design to write an accurate archive entry in `agents/plan-archive.md`. Git history preserves full content. Acceptance: directories deleted, every deleted plan has archive entry, no active plan removed. Note: verify `remove-fuzzy-recall` planstate discrepancy before deletion.

**FR-11: Marketplace publishing**
Publish the plugin to Claude Code marketplace as `edify`. Depends on all rename work (FR-1 through FR-9) being complete — this is the final step. Acceptance: `claude plugin install edify` succeeds in a fresh project.

**FR-12: GitHub main repo rename**
Rename `ddaanet/claudeutils` to `ddaanet/edify` on GitHub. Acceptance: `git ls-remote git@github.com:ddaanet/edify.git` succeeds.

**FR-13: PEP 541 claim**
File PEP 541 request on `pypi/support` GitHub repo to claim abandoned `edify` package. Runs in parallel with other work. Acceptance: claim approved, package ownership transferred.

### Constraints

**C-1: Session-cli-tool merge-first**
All rename work blocks on session-cli-tool worktree completion and merge. The worktree is actively adding new `claudeutils` references — renaming before merge causes double-rename work and worktree divergence.

**C-2: No broken references at commit boundaries**
Rename propagation must not leave broken references at any commit boundary. The commit strategy (shim, atomic, phased) is a design decision. Python namespace redirections may be needed to decouple file renames from identifier changes.

**C-3: Full-tree grep discovery**
Path propagation must use `grep -r` across full tree, not manual file lists. Prior plugin-migration Phase 0 missed 15+ files with manual inventory (learning: `when step file inventory misses codebase references`).

**C-4: Self-referential submodule content**
Files within `agent-core/` (soon `plugin/`) reference `agent-core/` paths. `grep --exclude-dir` must not exclude the renamed directory's internal references.

**C-5: Local directory rename between sessions**
`mv ~/code/claudeutils ~/code/edify` is a manual step between sessions. Sandbox write-allow paths and `$CLAUDE_PROJECT_DIR` are set at session start — cannot rename under a running session. Worktree container path changes accordingly (`claudeutils-wt/` → `edify-wt/`).

### Out of Scope

- Fragment content changes (path references updated, behavioral rules unchanged)
- New skill logic or workflow redesign
- CLI migration (restructuring `bin/` scripts into proper `edify` subcommands — separate job, future plan material)
- Consumer mode implementation (marketplace installs `edify`, but `$EDIFY_PLUGIN_ROOT` path resolution for consumer projects is deferred)

### Dependencies

- `session-cli-tool` worktree — must complete and merge before rename work begins (C-1)
- GitHub access — admin permissions on `ddaanet/agent-core` and `ddaanet/claudeutils` for repo renames
- PyPI PEP 541 — claim approval for `edify` name (non-blocking for rename, blocking for FR-9c and FR-11)

### Open Questions

- Q-4: `remove-fuzzy-recall` shows as `[delivered]` in planstate but is listed as pending in session.md — verify before deletion

### References

- `plans/plugin-migration/outline.md` — Phase 7 (directory rename) and marketplace setup specs
- `plans/plugin-migration/design.md` — D-1 naming hierarchy, D-8 consumer mode deferral
- `plans/plugin-migration/reports/deliverable-review.md` — deferred items confirmation
- `plans/plugin-migration/reports/phase-0-review.md` — Phase 0 rename review (discovery gaps, ordering)
- `plans/plugin-migration/runbook-outline.md:243-255` — Phase 7 mechanical steps

### Skill Dependencies (for /design)

- Load `plugin-dev:plugin-structure` before design (marketplace publishing in FR-11)
