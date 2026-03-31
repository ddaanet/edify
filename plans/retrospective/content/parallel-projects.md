# Parallel Project Evidence — Retrospective Expansion

Evidence from 8 parallel agentic projects showing pattern propagation and plugin adoption.

## pytest-md

- **Date range:** 2026-01-02 to 2026-02-06
- **Agent instruction files:** AGENTS.md → CLAUDE.md (full migration)
- **Migration:** `f82e7a2` 2026-01-28 "Add CLAUDE.md with @file references"
- **Agent-core adoption:** `16f7953` 2026-01-20 "Restructure Claude Code skills and add plugin submodule"
- **Pattern usage:** TDD workflow skills, commit/handoff skills, session log design, plan directory structure

### Key commits

| Date | Hash | Event |
|------|------|-------|
| 2026-01-02 | `1600882` | Initial commit with AGENTS.md |
| 2026-01-03 | `fd939eb` | First `.claude/settings.json` |
| 2026-01-04 | `901623a` | Enable context7 and code-review plugins |
| 2026-01-12 | `69bf88b` | Add TDD workflow skills and session log design |
| 2026-01-12 | `94d2622` | Restructure skills to Claude Code format |
| 2026-01-12 | `aa8ee90` | Add commit and handoff skills |
| 2026-01-20 | `16f7953` | Add plugin submodule |
| 2026-01-28 | `f82e7a2` | Add CLAUDE.md with @file references |
| 2026-01-30 | `de59b20` | Phase 5-6 TDD runbook with design and agent tooling |
| 2026-02-06 | `eaa2498` | Migrate to plugin Tier 2 structure |

### Agent-core nested repo (origin)

204 commits (2026-01-15 to 2026-02-06). First: "Initialize plugin repository structure". Last: "Add memory-refactor agent for documentation splitting."

This is plugin's birthplace before extraction as a submodule to edify. Contains the full early history of fragments, skills, agents, and workflow patterns.

First 5 commits:
- `5783aef` Initialize plugin repository structure
- `66af17c` Step 2: Extract shared justfile recipes from existing projects
- `0e2f365` Step 3: Extract shared ruff and mypy configurations
- `e5c3ba3` Phase 1: Add agent instruction fragments and documentation enhancements
- `1543cc2` Add baseline task agent and weak orchestrator pattern

Last 5 commits:
- `06984d3` Add worktree parallel session support to execute-rule
- `56c7f4e` Fix prose gate skipping with D+B hybrid pattern
- `d243fad` Fix linter warnings in hook scripts
- `a7bb5ae` Fix memory-refactor agent missing Bash tool
- `a7dc72e` Add memory-refactor agent for documentation splitting

## home

- **Date range:** 2025-11-05 to 2026-03-11
- **Agent instruction files:** AGENTS.md → CLAUDE.md (migrated 2026-01-18)
- **Migration:** `091073f` 2026-01-18 "Rename AGENTS.md→CLAUDE.md, add load rule for session context"
- **Agent-core adoption:** `83cef17` 2026-01-22 "Add plugin submodule and symlink skills/agents"
- **Pattern usage:** Full edify workflow adoption, statusline context bar, memory infrastructure

### Key commits

| Date | Hash | Event |
|------|------|-------|
| 2026-01-12 | `e31a4c0` | Initial AGENTS.md with orchestrator model |
| 2026-01-13 | `deb0d91` | Formalize orchestrator constraints and subagent protocol |
| 2026-01-18 | `091073f` | Rename AGENTS.md→CLAUDE.md |
| 2026-01-22 | `83cef17` | Add plugin submodule |
| 2026-01-23 | `7c67a7a` | Update CLAUDE.md based on plugin |
| 2026-01-24 | `404ede3` | Add token-efficient bash rules |
| 2026-01-29 | `f236481` | Update plugin with dotenvrc, intent comments |
| 2026-01-30 | `88f05ad` | Replace handoff-lite with handoff-haiku skill |
| 2026-02-02 | `e065fbb` | Add plugin agent and hook symlinks |
| 2026-02-27 | `59a4829` | Add plugin hooks, agents, and skills symlinks |
| 2026-02-27 | `ebcabc1` | Set up memory infrastructure and consolidate decision files |

**Notes:** Longest continuous agentic evolution (Nov 2025 – Mar 2026). Shows full lifecycle: early AGENTS.md → CLAUDE.md migration → plugin adoption → memory infrastructure → hooks. Most complete pattern propagation evidence.

## tuick

- **Date range:** 2025-10-25 to 2026-01-03
- **Agent instruction files:** Both AGENTS.md AND CLAUDE.md (coexistence)
- **CLAUDE.md content:** "Follow all rules in @AGENTS.md — this file contains Claude-specific directives only." Claude-specific additions: task delegation with haiku model.
- **Pattern usage:** Errorformat integration, cognitive protocols, multi-agent system restructuring

### Key commits

| Date | Hash | Event |
|------|------|-------|
| 2025-10-25 | `7d2fa67` | Initial AGENTS.md (TDD rules from emojipack) |
| 2025-10-29 | `f4c8cca` | AGENTS.md: Sleep is forbidden in tests |
| 2025-10-31 | `6275f86` | AGENTS.md: try make Claude use "just agent" |
| 2025-11-07 | `c73d5c0` | AGENTS.md: retrospective updates |
| 2025-11-10 | `7dfefca` | Restructure AGENTS.md for clarity and logical flow |
| 2025-12-08 | `bf92d0e` | Test for TUICK_VERBOSE environment inheritance |
| 2025-12-12 | `a3e15a1` | Update AGENTS.md with cognitive protocols |
| 2025-12-15 | `7a97ef3` | Restructure agent rules into multi-agent system |
| 2025-12-15 | `26c3b5d` | Remove epistemic standards from core.md |
| 2026-01-03 | `6973336` | Add Claude Code settings |

**Notes:** Most AGENTS.md iterations of any project (18 direct AGENTS.md commits). Shows: retrospective-driven rule refinement, cognitive protocol experiments (later abandoned), multi-agent system architecture (AGENTS.md + agent-specific files). The "epistemic standards" and "cognitive protocols" represent an evolutionary dead end — removed Dec 15.

## jobsearch

- **Date range:** 2025-10-02 to 2026-01-22
- **Agent instruction files:** Both CLAUDE.md and AGENTS.md
- **Migration:** REVERSE — `eec32b4` 2025-10-07 "Merge CLAUDE.md into AGENTS.md with Global and Project sections"
- **Pattern usage:** Claude.ai import, skill invocation, `just agent` recipes

### Key commits

| Date | Hash | Event |
|------|------|-------|
| 2025-10-02 | `f250be3` | Early development with CLAUDE.md |
| 2025-10-03 | `e7fe28e` | Update CLAUDE.md and README.md |
| 2025-10-07 | `eec32b4` | Merge CLAUDE.md INTO AGENTS.md |
| 2025-10-08 | `b2127be` | Add 'just agent' command |
| 2025-10-08 | `8f97c74` | AGENTS.md: gitmojis! |
| 2025-10-21 | `534fd64` | Big update, reorganize, strict linting |
| 2026-01-21 | `9744bac` | Add project setup and Claude Code skills |
| 2026-01-22 | `4021e31` | Install default .claude/settings.json |

**Notes:** Earliest CLAUDE.md usage (Oct 2025) — predates convention. Reverse migration (CLAUDE.md→AGENTS.md) shows naming convention not yet settled. Late Claude Code adoption (Jan 2026, 3 months later).

## devddaanet

- **Date range:** 2026-03-05 to 2026-03-11
- **Agent instruction files:** CLAUDE.md via plugin
- **Pattern usage:** Worktree-sync, deliverable-review, plan-specific agents, inline execution
- **Agent-core adoption:** `b7e48cd` 2026-03-05 (initial commit includes plugin submodule)

### Key commits

| Date | Hash | Event |
|------|------|-------|
| 2026-03-05 | `7a0bcdf` | Initial commit with plugin submodule |
| 2026-03-05 | `73c2918` | Replace rsync with Unison bidirectional sync |
| 2026-03-08 | `b714bd8` | Reorder sync to git-first with per-tree unison gating |
| 2026-03-09 | `feed833` | Capture worktree-sync requirements from sync gap analysis |
| 2026-03-09 | `c93f1a8` | Prepare worktree-sync runbook for orchestration |
| 2026-03-10 | `265c8c7` | Deliverable review worktree-sync: 1 critical, 3 minor |
| 2026-03-10 | `cae9155` | Fix worktree-sync deliverable-review findings |
| 2026-03-10 | `4ffb1ea` | Re-review worktree-sync: all findings resolved, delivered |

**Notes:** Most mature pattern consumer. Every commit is agentic. Shows full pipeline in production: requirements → design → runbook → orchestrate → deliverable-review → fix → re-review → delivered. Born with plugin from day 1.

## deepface

- **Date range:** 2020-02-08 to 2025-07-23
- **Agent instruction files:** None
- **Pattern usage:** None visible in repo
- **Notes:** Large OSS project (2024 commits). Claude-assisted test contributions visible in session logs only, not in repo history. No agent instruction files committed. Excluded as data point — no agentic evidence in git.

## emojipack (standalone)

- **Date range:** 2025-10-12 to 2026-01-08
- **Notes:** Identical history to emojipack under `~/code/edify/scratch/emojipack`. Same repo. Not an independent data point.

## ddaanet

- **Date range:** 2020-04-02 to 2026-02-18
- **Agent instruction files:** CLAUDE.md (auto-generated Jul 2025) → AGENTS.md (manual, Jan 2026)
- **Migration:** Replacement — auto-generated CLAUDE.md deleted, replaced with hand-crafted AGENTS.md

### Key commits

| Date | Hash | Event |
|------|------|-------|
| 2025-07-11 | `f8ece02` | Add auto-generated CLAUDE.md |
| 2026-01-08 | `2c61287` | Replace CLAUDE.md with AGENTS.md and add session tracking |
| 2026-01-08 | `ed04899` | Update agent guidance, add design decisions, session tracking |
| 2026-01-08 | `68459ae` | Add commit message density guideline |
| 2026-01-08 | `87d2b3d` | Document Skill tool fully qualified name requirement |
| 2026-01-08 | `ee996a3` | Eliminate session.md churn |
| 2026-01-08 | `0f21638` | Add git lock file retry guideline |
| 2026-01-08 | `b84d70b` | Add commit workflow guideline |

**Notes:** Late-stage adoption. 203 pre-agentic commits, then 11 agentic commits in one day (Jan 8). Shows: auto-generated CLAUDE.md (Jul 2025, likely Claude Code scaffold) replaced by sophisticated AGENTS.md with session tracking, design decisions, commit workflow — all edify patterns.
