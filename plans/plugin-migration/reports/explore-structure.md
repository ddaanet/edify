# Agent Core Structure Exploration

## Summary

Agent-core is a shared submodule providing unified workflow infrastructure for Claude Code projects. It contains 16 skills, 14 baseline agents, 4 hook scripts, 11 utility scripts, and comprehensive workflow documentation. All skills and agents are synced to parent projects via symlinks in `.claude/` directories. Currently no plugin.json exists—all hooks are configured in `.claude/settings.json` (legacy hook configuration).

---

## Directory Tree Overview

```
plugin/
├── .git/                          # Submodule git repository
├── .claude/                       # Agent-core local configuration
│   ├── CLAUDE.local.md.example    # Development-only context (not synced to parent)
│   └── settings.json              # Local hook configuration for development
├── agents/                        # Baseline agent templates (14 files)
├── bin/                           # Utility scripts (11 executable files)
├── configs/                       # Configuration templates for projects
├── docs/                          # Workflow and pattern documentation
├── fragments/                     # Reusable instruction fragments (19 markdown files)
├── hooks/                         # Hook implementation scripts (4 files)
├── migrations/                    # Schema migration documentation
├── skills/                        # Workflow skills (16 directories)
├── templates/                     # Templates for project setup
├── scripts/                       # Ad-hoc scripts (create-plan-agent.sh, split-execution-plan.py)
├── Makefile                       # Build/development targets
├── justfile                       # Recipe: sync-to-parent + precommit stub
└── README.md                      # Project documentation
```

---

## Skills Directory

All 16 skills in `/Users/david/code/edify-plugin-migration/plugin/skills/`:

| Skill | Type | Location | Purpose |
|-------|------|----------|---------|
| commit | Workflow | `commit/SKILL.md` | Handle multi-line commit messages with gitmoji selection |
| design | Workflow | `design/SKILL.md` | Design session entry point (detects TDD vs general) |
| gitmoji | Helper | `gitmoji/SKILL.md` | Gitmoji index lookup and selection |
| handoff | Workflow | `handoff/SKILL.md` | Update session.md context and prepare for handoff |
| handoff-haiku | Workflow | `handoff-haiku/SKILL.md` | Haiku-specific handoff (no learnings judgment) |
| next | Workflow | `next/SKILL.md` | Show next pending task or current status |
| opus-design-question | Query | `opus-design-question/SKILL.md` | Delegate design decisions to Opus |
| orchestrate | Workflow | `orchestrate/SKILL.md` | Execute runbook steps with checkpoint gates |
| plan-adhoc | Planning | `plan-adhoc/SKILL.md` | General runbook planning (infrastructure, refactoring) |
| plan-tdd | Planning | `plan-tdd/SKILL.md` | TDD runbook planning (test-first methodology) |
| reflect | Analysis | `reflect/SKILL.md` | Root cause analysis and reflection |
| remember | Documentation | `remember/SKILL.md` | Consolidate learnings into permanent documentation |
| review-tdd-plan | Review | `review-tdd-plan/SKILL.md` | Review TDD runbook for RED/GREEN violations |
| shelve | Workflow | `shelve/SKILL.md` | Pause work, store session state, resume later |
| token-efficient-bash | Pattern | `token-efficient-bash/SKILL.md` | Bash scripting pattern with strict mode and error handling |
| vet | Review | `vet/SKILL.md` | Code review and vetting skill |

**Skill structure:** Each skill is a directory with:
- `SKILL.md` — Main skill definition (frontmatter + description)
- `references/` — Reference files for skill context
- `examples/` — Example outputs
- `scripts/` — Helper scripts (e.g., gitmoji index update)
- `templates/` — Templates used by the skill

**Total skills in symlinks:** 17 (includes `review-tdd-plan` which isn't listed as primary, but is symlinked)

---

## Agents Directory

All 14 agents in `/Users/david/code/edify-plugin-migration/plugin/agents/`:

| Agent | File Size | Purpose |
|-------|-----------|---------|
| design-vet-agent.md | 12.6 KB | Review design documents for completeness and correctness (Opus) |
| memory-refactor.md | 4.8 KB | Refactor memory index and learnings structure |
| outline-review-agent.md | 10.1 KB | Review plan outlines for requirements coverage |
| quiet-explore.md | 3.8 KB | Exploration agent for file discovery and reporting |
| quiet-task.md | 4.4 KB | Base task execution agent (quiet output pattern) |
| refactor.md | 7.0 KB | Code refactoring agent |
| remember-task.md | 7.2 KB | Documentation consolidation task agent |
| review-tdd-process.md | 12.1 KB | Review TDD execution for RED/GREEN compliance |
| runbook-outline-review-agent.md | 14.8 KB | Review runbook outlines holistically |
| tdd-plan-reviewer.md | 6.3 KB | Review TDD planning for prescriptive code violations |
| tdd-task.md | 9.7 KB | TDD cycle execution agent (test → implement → refactor) |
| test-hooks.md | 12.5 KB | Agent for testing Claude Code hooks |
| vet-agent.md | 9.8 KB | General code review and vetting |
| vet-fix-agent.md | 11.3 KB | Automated fix agent (applies all fixes found) |

**Agent types:**
- **Baseline templates** — `quiet-task.md`, `tdd-task.md` (copied to `.claude/agents/[plan-name]-task.md` by prepare-runbook.py)
- **Specialized reviewers** — design-vet-agent, tdd-plan-reviewer, vet-fix-agent, outline-review-agent (invoked by skills)
- **Process agents** — review-tdd-process, test-hooks, memory-refactor (experimental/utilities)

---

## Hooks Directory

Four hook scripts in `/Users/david/code/edify-plugin-migration/plugin/hooks/`:

### Hook Scripts

| Hook | Event | Language | Purpose |
|------|-------|----------|---------|
| pretooluse-block-tmp.sh | PreToolUse | Bash | Block writes to system `/tmp/`, enforce project-local `tmp/` |
| pretooluse-symlink-redirect.sh | PreToolUse | Bash | Block writes to symlinked files, suggest write to plugin source |
| submodule-safety.py | PreToolUse / PostToolUse | Python | Enforce project root cwd, block cross-submodule commands |
| userpromptsubmit-shortcuts.py | UserPromptSubmit | Python | Expand workflow shortcuts (s, x, xc, r, h, hc, ci, ?) |

### Hook Details

**pretooluse-block-tmp.sh:**
- Reads JSON input from stdin
- Extracts tool_name and file_path
- Blocks Write/Edit tools targeting `/tmp/` or `/private/tmp/`
- Outputs error to stderr, exits with code 2 to block operation

**pretooluse-symlink-redirect.sh:**
- Checks if target file is a symlink to plugin
- If so, blocks Write/Edit and suggests writing to plugin source instead
- Uses readlink to resolve symlink target
- Handles relative symlinks by converting to absolute

**submodule-safety.py:**
- Dual-mode: PreToolUse blocks commands, PostToolUse warns about cwd drift
- PreToolUse: Blocks all commands unless cwd == project root (except exact `cd` restores)
- PostToolUse: Injects additionalContext warning when cwd != project root
- Uses CLAUDE_PROJECT_DIR env var for project root detection

**userpromptsubmit-shortcuts.py:**
- Tier 1 (exact match): s, x, xc, r, h, hc, ci, ?
- Tier 2 (colon prefix): d: (discussion), p: (pending)
- Expands shortcuts to full workflow descriptions
- Silent pass-through if no match (exit 0)

### Hook Integration

Hooks are currently configured in `.claude/settings.json` (not in plugin.json):
- **PreToolUse** matchers: Write|Edit, Bash
- **PostToolUse** matchers: Bash
- **UserPromptSubmit** → global (no matcher)

Symlinks in `.claude/hooks/` point to plugin source:
```
pretooluse-block-tmp.sh → ../../plugin/hooks/pretooluse-block-tmp.sh
pretooluse-symlink-redirect.sh → ../../plugin/hooks/pretooluse-symlink-redirect.sh
submodule-safety.py → ../../plugin/hooks/submodule-safety.py
userpromptsubmit-shortcuts.py → ../../plugin/hooks/userpromptsubmit-shortcuts.py
```

---

## Bin Directory

Eleven utility scripts in `/Users/david/code/edify-plugin-migration/plugin/bin/`:

| Script | Language | Purpose |
|--------|----------|---------|
| add-learning.py | Python | Add single learning entry to learnings.md |
| assemble-runbook.py | Python | Assemble phase files into consolidated runbook.md |
| batch-edit.py | Python | Batch file editor with marker format (<<<...>>>) |
| learning-ages.py | Python | Analyze learning ages and consolidation readiness |
| prepare-runbook.py | Python (33.7 KB) | Main: generate step artifacts from runbook.md |
| task-context.sh | Bash | Recover session.md from git history using task name as key |
| validate-decision-files.py | Python | Validate agent decision file headers against memory index |
| validate-jobs.py | Python | Validate jobs.md plan status entries |
| validate-learnings.py | Python | Validate learnings.md format and word count |
| validate-memory-index.py | Python | Validate memory index entries against referenced files |
| validate-tasks.py | Python | Validate session.md pending task metadata |

**Key scripts:**
- **prepare-runbook.py** — Central runbook processing: metadata extraction, cycle numbering, step file generation, agent YAML creation
- **validate-*.py** — Pre-commit validators for consistency enforcement
- **batch-edit.py** — Token-efficient multi-file editing (marker format: <<<FILE:key>>><new content>===)

---

## Fragments Directory

Nineteen instruction fragments in `/Users/david/code/edify-plugin-migration/plugin/fragments/`:

| Fragment | Purpose |
|----------|---------|
| bash-strict-mode.md | Bash scripting pattern with set -euo pipefail |
| claude-config-layout.md | Hook and agent configuration patterns |
| code-removal.md | Delete obsolete code, don't archive |
| commit-delegation.md | Commit workflow delegation patterns |
| commit-skill-usage.md | Always use /commit skill for multi-line messages |
| communication.md | Stop on errors, wait for instruction, explicit boundaries |
| delegation.md | Delegate everything, script-first evaluation |
| design-decisions.md | Use /opus-design-question for architectural choices |
| error-classification.md | Error taxonomy for planning work |
| error-handling.md | Never suppress errors, report explicitly |
| execute-rule.md | Session modes (STATUS/EXECUTE/RESUME/WORKTREE) |
| no-estimates.md | Report measured data only, no predictions |
| prerequisite-validation.md | Validation patterns for plan execution |
| project-tooling.md | Use project recipes before ad-hoc commands |
| sandbox-exemptions.md | Permission allow + dangerouslyDisableSandbox patterns |
| tmp-directory.md | Use project-local tmp/, never system /tmp/ |
| token-economy.md | No file content repetition, use references |
| tool-batching.md | Batch reads/writes, parallel edits, sequential same-file |
| vet-requirement.md | Vet all production artifacts (code, plans, tests) |
| workflows-terminology.md | Terminology: Job, Design, Phase, Runbook, Step |

---

## Templates Directory

Three files in `/Users/david/code/edify-plugin-migration/plugin/templates/`:

| File | Purpose |
|------|---------|
| CLAUDE.template.md | Template CLAUDE.md for new projects using plugin |
| dotenvrc | Environment variable configuration example |
| README.md | Templates directory documentation |

---

## Documentation (docs) Directory

Six workflow and pattern guides in `/Users/david/code/edify-plugin-migration/plugin/docs/`:

| Document | Lines | Purpose |
|----------|-------|---------|
| @file-pattern.md | — | File pattern matching conventions |
| general-workflow.md | — | General implementation workflow (6 stages) |
| pattern-plan-specific-agent.md | — | Plan-specific agent generation pattern |
| pattern-weak-orchestrator.md | — | Weak orchestrator execution pattern |
| shortcuts.md | — | Workflow shortcuts reference (s, x, r, h, ci) |
| tdd-workflow.md | — | TDD methodology workflow (RED/GREEN/REFACTOR) |

---

## Configs Directory

Configuration templates in `/Users/david/code/edify-plugin-migration/plugin/configs/`:

| Config | Purpose |
|--------|---------|
| claude-env.sh | Environment variable configuration |
| docformatter-base.toml | Docstring formatting rules |
| justfile-base.just | Base justfile recipes for projects |
| mypy-base.toml | Type checking configuration |
| ruff-base.toml | Linting configuration |
| README.md | Configuration template guidance |

---

## Current Symlinks in .claude/

**Skills (.claude/skills/):** 17 symlinks
- commit → ../../plugin/skills/commit
- design → ../../plugin/skills/design
- gitmoji → ../../plugin/skills/gitmoji
- handoff → ../../plugin/skills/handoff
- handoff-haiku → ../../plugin/skills/handoff-haiku
- next → ../../plugin/skills/next
- opus-design-question → ../../plugin/skills/opus-design-question
- orchestrate → ../../plugin/skills/orchestrate
- plan-adhoc → ../../plugin/skills/plan-adhoc
- plan-tdd → ../../plugin/skills/plan-tdd
- reflect → ../../plugin/skills/reflect
- remember → ../../plugin/skills/remember
- review-tdd-plan → ../../plugin/skills/review-tdd-plan
- shelve → ../../plugin/skills/shelve
- token-efficient-bash → ../../plugin/skills/token-efficient-bash
- vet → ../../plugin/skills/vet

**Agents (.claude/agents/):** Mix of symlinks and task files
- Symlinks: design-vet-agent.md, outline-review-agent.md, quiet-explore.md, quiet-task.md, refactor.md, review-tdd-process.md, runbook-outline-review-agent.md, tdd-plan-reviewer.md, tdd-task.md, test-hooks.md, vet-agent.md, vet-fix-agent.md
- Task files (generated by prepare-runbook.py): `*-task.md` files from prior plans (claude-tools-recovery-task.md, claude-tools-rewrite-task.md, consolidation-task.md, etc.)

**Hooks (.claude/hooks/):** 4 symlinks
- pretooluse-block-tmp.sh → ../../plugin/hooks/pretooluse-block-tmp.sh
- pretooluse-symlink-redirect.sh → ../../plugin/hooks/pretooluse-symlink-redirect.sh
- submodule-safety.py → ../../plugin/hooks/submodule-safety.py
- userpromptsubmit-shortcuts.py → ../../plugin/hooks/userpromptsubmit-shortcuts.py

---

## Hook Configuration

Current hook configuration in `.claude/settings.json`:

**PreToolUse hooks:**
```json
[
  {
    "matcher": "Write|Edit",
    "hooks": [
      "bash $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse-block-tmp.sh",
      "bash $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse-symlink-redirect.sh"
    ]
  },
  {
    "matcher": "Bash",
    "hooks": [
      "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"
    ]
  }
]
```

**PostToolUse hooks:**
```json
[
  {
    "matcher": "Bash",
    "hooks": [
      "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"
    ]
  }
]
```

**UserPromptSubmit hooks:**
```json
[
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/plugin/hooks/userpromptsubmit-shortcuts.py",
        "timeout": 5
      }
    ]
  }
]
```

---

## Justfile

Single justfile at `/Users/david/code/edify-plugin-migration/plugin/justfile`:

| Recipe | Purpose |
|--------|---------|
| help | List available recipes |
| sync-to-parent | Create symlinks in parent project's .claude/ directory |
| precommit | Stub validation (plugin has no validation requirements) |

**Key recipe:** `sync-to-parent` creates relative symlinks for:
- All skills in `plugin/skills/*/` → `.claude/skills/`
- All agent files in `plugin/agents/*.md` → `.claude/agents/`
- All hook files in `plugin/hooks/*.sh` and `*.py` → `.claude/hooks/`
- Cleans stale skill symlinks (source deleted in plugin)

---

## Plugin Configuration Status

**Current state:** No plugin.json exists anywhere in the codebase.

**Where plugin would go:**
- Future: `.claude/plugins/edify/plugin.json` (plugin name TBD: currently "edify" per session.md)
- Hooks would move from `.claude/settings.json` to plugin structure

**Current hook architecture:**
- All hooks configured in `.claude/settings.json` (legacy)
- No plugin.json for plugin-style metadata
- Hooks executed via symlinks to plugin source scripts

---

## Key Patterns and Observations

### Symlink Architecture
- All plugin content (skills, agents, hooks) exposed via relative symlinks in parent's `.claude/` directory
- Symlinks point to plugin source, enabling live editing without re-syncing
- `just sync-to-parent` manages symlink lifecycle (create, update, remove stale)

### Hook Enforcement
- PreToolUse: Block invalid operations (system /tmp/ writes, symlink edits, wrong cwd)
- PostToolUse: Warn about cwd drift (from submodule-safety.py dual-mode)
- UserPromptSubmit: Expand workflow shortcuts to full descriptions

### Agent Specialization
- Baseline agents: quiet-task.md, tdd-task.md (copied to `.claude/agents/` by prepare-runbook.py)
- Review agents: design-vet-agent, tdd-plan-reviewer, vet-fix-agent (invoked by skills)
- Utility agents: memory-refactor, test-hooks, reflect (special cases)

### Skill Organization
- Core workflow skills: design, plan-adhoc, plan-tdd, orchestrate
- Helper skills: commit, gitmoji, handoff, handoff-haiku, next, shelve
- Analysis skills: reflect, remember, vet, review-tdd-plan, opus-design-question, token-efficient-bash

### Validation Infrastructure
- Pre-commit validators: validate-*.py scripts for consistency
- Task context recovery: task-context.sh uses git log to find task definition
- Runbook processing: prepare-runbook.py central orchestrator for step generation

---

## Migration Considerations for Plugin

**To migrate from symlink architecture to plugin:**

1. Create `.claude/plugins/edify/plugin.json` with hook definitions
2. Move hook scripts from `.claude/hooks/` to plugin directory
3. Move skill/agent definitions into plugin structure (if Claude Code plugin system supports it)
4. Update `.claude/settings.json` to remove hook definitions (keep permissions/sandbox)
5. Validate hook event dispatching works the same way

**Open questions:**
- Can skills/agents be served from plugin, or only from .claude/ directory?
- Does plugin.json support nested hooks array structure (PreToolUse → [array])?
- How does plugin version/discovery interact with symlinked plugin updates?

---

## Files Referenced

- **Justfile:** `/Users/david/code/edify-plugin-migration/plugin/justfile`
- **Hooks:** `/Users/david/code/edify-plugin-migration/plugin/hooks/*.sh`, `*.py`
- **Hook config:** `/Users/david/code/edify-plugin-migration/.claude/settings.json`
- **Skills:** `/Users/david/code/edify-plugin-migration/plugin/skills/*/SKILL.md`
- **Agents:** `/Users/david/code/edify-plugin-migration/plugin/agents/*.md`
- **Symlinks:** `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` (all relative to project root)
