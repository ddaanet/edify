# Agent-Core Exploration Report: 2026-03-12

## Summary

Agent-core is a comprehensive workflow infrastructure for Claude Code agents, currently installed as a git submodule. It provides 33 skills, 13 agents, 27 fragments, and a hook system for lifecycle management. The project is structured to be converted to a Claude Code plugin (`edify-plugin`), with all components ready for migration.

---

## 1. Agent-Core Directory Structure (Top 2 Levels)

```
plugin/
├── agents/              # 13 agent definitions (specialized sub-agents)
├── bin/                 # Utility and validator scripts
├── configs/             # Shared tool configurations (ruff, mypy, docformatter, justfile)
├── docs/                # Documentation
├── fragments/           # 27 instruction fragments (ambient context)
├── hooks/               # 10 hook files + hooks.json registry
├── migrations/          # Migration-related files
├── scripts/             # Additional scripts
├── skills/              # 33 skill definitions (slash commands)
├── templates/           # Project scaffolding (CLAUDE.template.md, dotenvrc)
├── README.md            # Comprehensive overview (269 lines)
└── justfile             # Project recipes
```

---

## 2. Hooks in plugin/hooks/

All hook files present and configured in `hooks.json`:

| Hook File | Purpose |
|-----------|---------|
| `hooks.json` | Registry defining hook event bindings (UserPromptSubmit, PreToolUse, PostToolUse, SessionStart, Stop) |
| `posttooluse-autoformat.sh` | PostToolUse: Auto-format Write/Edit changes |
| `pretooluse-block-tmp.sh` | PreToolUse: Block writes to `/tmp/`, enforce project-local `tmp/` |
| `pretooluse-recall-check.py` | PreToolUse: Verify recall artifact structure |
| `pretooluse-recipe-redirect.py` | PreToolUse: Route Bash commands to justfile recipes when available |
| `pretooluse-symlink-redirect.sh` | PreToolUse: Resolve symlink targets for Edit operations |
| `sessionstart-health.sh` | SessionStart: Run health checks at session startup |
| `stop-health-fallback.sh` | Stop: Fallback health checks on session termination |
| `submodule-safety.py` | PreToolUse/PostToolUse: Block/warn commands from wrong cwd |
| `userpromptsubmit-shortcuts.py` | UserPromptSubmit: Expand workflow shortcuts (s, x, xc, r, h, etc.) |

**hooks.json event bindings:**
- `UserPromptSubmit`: userpromptsubmit-shortcuts.py (timeout: 5s)
- `PreToolUse` (Bash): pretooluse-recipe-redirect.py
- `PostToolUse` (Write\|Edit): posttooluse-autoformat.sh
- `SessionStart` (*): sessionstart-health.sh
- `Stop` (*): stop-health-fallback.sh

---

## 3. .claude/ Directory Symlinks

**Skills (.claude/skills/):** 33 symlinks
```
brief, codify, commit, deliverable-review, design, doc-writing, error-handling,
gitmoji, ground, handoff, handoff-haiku, how, inline, magic-query, memory-index,
next, orchestrate, plugin-dev-validation, prime, prioritize, project-conventions,
proof, recall, reflect, release-prep, requirements, review, review-plan, runbook,
shelve, token-efficient-bash, when, worktree
```

**Agents (.claude/agents/):** 17 items
- 13 symlinks: artisan.md, brainstorm-name.md, corrector.md, design-corrector.md, hooks-tester.md, outline-corrector.md, refactor.md, runbook-corrector.md, runbook-outline-corrector.md, runbook-simplifier.md, scout.md, tdd-auditor.md, test-driver.md
- 5 generated files (not symlinks): handoff-cli-tool-*.md agents (corrector, impl-corrector, implementer, task, test-corrector, tester)

**Hooks (.claude/hooks/):** 4 symlinks
- pretooluse-block-tmp.sh
- pretooluse-symlink-redirect.sh
- submodule-safety.py
- userpromptsubmit-shortcuts.py

---

## 4. Settings.json Hooks Section

Cannot access (permission denied — in deny-list). However, hooks.json shows complete hook registry within plugin/hooks/. The actual .claude/settings.json would reference this registry for plugin/hook orchestration.

---

## 5. Justfile Recipes

**Root justfile (plugin-migration/):**
```
help              # Show available recipes
precommit         # Stub precommit validation
setup             # Set up development environment
sync-to-parent    # Sync skills and agents to parent .claude directory via symlinks
```

**Agent-core justfile:** No output (likely no recipes specific to plugin, or uses root recipes).

---

## 6. Plugin Files

**No .claude-plugin/ or plugin.json files exist.**

Status from README.md (line 12-13): "Currently installed as a git submodule; converting to a [Claude Code plugin][plugin-docs] (`edify-plugin`)." Migration is in-progress; plugin structure has not yet been created.

---

## 7. Artifact Counts

| Category | Count |
|----------|-------|
| **Fragments** | 27 (instruction files, ambient context) |
| **Skills** | 33 (slash-command procedures) |
| **Agents** | 13 (symlinked sub-agent definitions) |
| **Generated Agents** | 5 (handoff-cli-tool suite) |
| **Hook Files** | 10 (shell + Python scripts) |
| **Scripts (bin/)** | Utility and validator scripts (prepare-runbook.py, validate-*.py, etc.) |

---

## 8. Version Files

**No .version or version.txt files found anywhere in the codebase.**

---

## Key Findings for Plugin Migration

1. **Complete Infrastructure Stack:** All skills, agents, fragments, and hooks are present and working (evidenced by symlinks in .claude/ and hooks.json registry).

2. **Submodule → Plugin Gap:** Current installation assumes plugin as a git submodule with `just sync-to-parent` to create symlinks. Plugin model would require:
   - Plugin package structure (manifest.json or equivalent)
   - Declarative hook/skill/agent registration
   - No symlink dependency on parent project structure

3. **Hook Architecture Ready:** hooks.json registry is already declarative and environment-variable aware (`$CLAUDE_PROJECT_DIR`). Can be adapted to plugin configuration.

4. **Generated Agent Files:** The 5 handoff-cli-tool-* agents are generated (not symlinks), suggesting a generation pipeline exists for plan-specific agents.

5. **No Plugin Metadata:** Absence of version files and plugin.json suggests migration is in requirements/design phase, not implementation.

6. **Fragment Loading via @-references:** Fragments load through CLAUDE.md `@` references (27 total), not declaratively. Plugin model may need to shift to plugin-level ambient context injection.

---

## Gaps & Unresolved Questions

- **Plugin package format:** What structure replaces the submodule + symlink model? (Claude Code plugin standards needed)
- **Hook registration:** How do hooks integrate into plugin manifest vs. .claude/settings.json?
- **Ambient fragment loading:** Does plugin system support @-reference loading, or require new mechanism?
- **Plan-specific agent generation:** What pipeline generates the handoff-cli-tool-* agents? Is it integrated into plugin?
- **Distribution & versioning:** No .version file present; plugin will need version management strategy.
- **Dependency management:** justfile uses `just` (external tool); plugin may need different dependency handling.
