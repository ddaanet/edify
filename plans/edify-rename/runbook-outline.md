# Runbook Outline: Edify Rename SP-1 (agent-core → plugin)

## Scope

SP-1 only: submodule directory rename `agent-core` → `plugin`. Two atomic commits per D-4.
Also updates `claudeutils` → `edify` inside submodule (per outline: "do both identities in submodule at once to avoid re-traversal").

Post-SP-3 measured counts:
- Submodule: 55 files with `agent-core` refs, 54 files with `claudeutils` refs
- Parent repo: 232 files with `agent-core` refs (excluding submodule, edify-rename plan, plugin-migration plan, retrospective)

## Requirements Mapping

| Requirement | Phase |
|------------|-------|
| FR-2 (URL update) | Phase 2 (.gitmodules) |
| FR-3 (directory rename) | Phase 2 (git mv) |
| FR-4 (config path propagation) | Phase 2 |
| FR-5 (source code paths) | Phase 2 |
| FR-6 (test paths) | Phase 2 |
| FR-7 (agentic prose paths) | Phase 1 (submodule) + Phase 2 (parent) |
| FR-8 (active plan paths) | Phase 2 |
| FR-9b (CLI command in submodule) | Phase 1 |

## Key Decisions

- D-3: Atomic commits per SP — all updates in one commit per boundary
- D-4: Two-commit pattern — submodule internal first, parent repo second
- D-5: No shims — clean break
- Recall: full-tree grep discovery (C-3), not manual file lists ("when step file inventory misses codebase references")

---

## Phase 1: Submodule internal references (type: general)

All edits inside `agent-core/`. Commit inside submodule repo at end.

### Step 1.1: Discovery — grep actual reference inventory
- `grep -r 'agent-core' agent-core/ --include='*.md' --include='*.py' --include='*.sh' --include='*.json' --include='*.yaml'` — capture file list
- `grep -r 'claudeutils' agent-core/ --include='*.md' --include='*.py' --include='*.sh' --include='*.json' --include='*.yaml'` — capture file list
- Record exact file paths and occurrence counts for verification

### Step 1.2: Parallel batch — update submodule references
Dispatch parallel file-scoped agents, one per directory scope:
- **agent-core/skills/** — replace `agent-core/` → `plugin/` and `claudeutils` → `edify` in all SKILL.md and reference files
- **agent-core/fragments/** — replace in all fragment .md files
- **agent-core/agents/** — replace in all agent definition .md files
- **agent-core/bin/** — replace in all scripts (.py, .sh)
- **agent-core/docs/** — replace in all documentation
- **agent-core/configs/** — replace in config templates
- **agent-core/hooks/** — replace in hook scripts
- **agent-core/references/** — replace in reference files
- **agent-core root files** — README.md, justfile, .claude-plugin/plugin.json, any other root files

Each agent: read files in scope, apply replacements, report changed file count.

### Step 1.3: Verification grep + submodule commit
- `grep -r 'agent-core' agent-core/` — must return zero matches (exclude plans/edify-rename references if any)
- `grep -r 'claudeutils' agent-core/` — must return zero matches
- `git -C agent-core add -A && git -C agent-core commit` — atomic submodule commit

---

## Phase 2: Parent repo rename + references (type: general)

Git mv, .gitmodules update, then parallel reference updates across parent repo. Single atomic commit.

### Step 2.1: Structural rename
- `git mv agent-core plugin`
- Edit `.gitmodules`: `[submodule "agent-core"]` → `[submodule "plugin"]`, path → `plugin`, URL → `git@github.com:ddaanet/edify-plugin.git`
- `git submodule sync`
- Fix `.envrc` symlink: `agent-core/templates/dotenvrc` → `plugin/templates/dotenvrc`

### Step 2.2: Parallel batch — update parent repo references
Dispatch parallel file-scoped agents, one per directory/file scope:
- **src/claudeutils/*.py** — replace `agent-core` → `plugin` in all source files (~39 occurrences across 6 files)
- **tests/*.py** — replace `agent-core` → `plugin` in all test files (~172 occurrences across 41 files)
- **CLAUDE.md** — replace all `@agent-core/` → `@plugin/`
- **justfile** — replace `agent-core/` → `plugin/`
- **.claude/settings.json** — replace `agent-core/bin/` → `plugin/bin/`
- **.claude/rules/*.md** — replace `agent-core` → `plugin`
- **pyproject.toml** — replace `agent-core` → `plugin` in ruff exclude
- **agents/*.md** (session.md, learnings.md, decisions/, memory-index.md, plan-archive.md) — replace `agent-core` → `plugin`
- **plans/*/** (active plans, excluding edify-rename) — replace `agent-core` → `plugin`
- **README.md + docs/** — replace `agent-core` → `plugin`

Each agent: read files in scope, apply replacements, report changed file count.

### Step 2.3: Verification + test + commit
- `grep -r 'agent-core' . --exclude-dir=.git --exclude-dir=plugin --exclude-dir=plans/edify-rename` — must return zero (only edify-rename plan and submodule internal refs may remain)
- `just test` — full test suite pass
- `just precommit` — full validation
- Stage all changes + updated submodule pointer, atomic commit

---

## Execution Model

**Dispatch protocol:** Orchestrator reads this outline. For Steps 1.2 and 2.2, dispatches N parallel agents via Task tool. Each agent receives:
- Directory scope (which files to process)
- Replacement pairs (`agent-core` → `plugin`, `claudeutils` → `edify` for Phase 1)
- Instruction: grep scope for patterns, apply replacements via Edit tool, report count

**Recall injection:** Each agent receives the 5 resolved recall entries inline (path references, grep discovery, hook paths, naming). Compact constraint format.

**Model:** Sonnet for all agents (mechanical grep-replace, no design decisions).

**Checkpoints:**
- After Step 1.3: submodule committed, zero agent-core/claudeutils refs inside submodule
- After Step 2.3: parent committed, zero agent-core refs in parent tree, tests pass

**Error escalation:**
- Agent reports file it cannot edit (permission, binary) → orchestrator handles
- Verification grep returns non-zero → orchestrator dispatches targeted fix agent for remaining matches
- Test failure → orchestrator reads failure, dispatches targeted fix agent

## Weak Orchestrator Metadata

**Total Steps:** 6 (2 sequential phases × 3 steps each)
**Parallel Dispatch:** Steps 1.2 and 2.2 each fan out to ~9-10 parallel agents
**Execution Model:**
- All steps: Sonnet (mechanical replacement)
**Step Dependencies:** Phase 1 → Phase 2 (sequential). Within each phase: discovery → parallel batch → verification (sequential)
**Error Escalation:** Sonnet → User (structural git issues, unexpected binary files)
**Report Locations:** `plans/edify-rename/reports/`
**Success Criteria:** Zero `agent-core` matches in parent tree (excluding edify-rename plan), zero `agent-core`/`claudeutils` matches in submodule, full test suite green
**Prerequisites:** SP-3 complete (verified), clean git tree
