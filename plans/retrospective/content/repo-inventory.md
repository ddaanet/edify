# Repo Inventory — Retrospective Expansion

Extracted: 2026-03-11

## Pre-claudeutils Repos (6)

### rules
- **Path:** `~/code/rules`
- **Commits:** 15 (expected ~15)
- **Date range:** 2025-09-30 to 2025-10-02
- **Agentic commits (path):** 9 — rules.md (9 commits), renamed to AGENTS.md on final commit
  - `eacf188` 2025-10-02 Rename rules.md to AGENTS.md and update
  - `13b357c` 2025-09-30 Adjust rules.md, re french typography
  - `677118d` 2025-09-30 Condense rules.md
  - `824ed21` 2025-09-30 Incorporate zed rules into rules.md, adjusted by hand
  - `0e63527` 2025-09-30 Merge rules.md improvement from the Downloads project
  - `538285f` 2025-09-30 Manual fixes to rules.md
  - `80ce05f` 2025-09-30 Merge and simplify rules from rules.md and rules-claude.md
  - `202f31c` 2025-09-30 Update development rules
  - `7b0a4b4` 2025-09-30 Initial commit
- **Notes:** Earliest known agent instruction file. Started as `rules.md`, renamed to `AGENTS.md` on final day. 9 of 15 commits touch agent instructions — this repo IS the agent rules.

### oklch-theme
- **Path:** `~/code/oklch-theme`
- **Commits:** 8 (expected ~8)
- **Date range:** 2025-11-28 to 2025-12-09
- **Agentic commits (path):** 2
  - `64cbf8f` 2025-12-01 Update: AGENTS.md with LLM awareness and project design document
  - `b0c0d64` 2025-11-28 Initial commit
- **Notes:** Gemini agent project. AGENTS.md titled "Agent Memory" with retrospective-driven rule updates. Added "LLM Limitation Awareness" section — earliest known metacognitive rules.

### scratch/box-api
- **Path:** `~/code/claudeutils/scratch/box-api`
- **Commits:** 46 (expected ~46)
- **Date range:** 2025-11-14 to 2025-12-08
- **Agentic commits (path):** 23 — heavy AGENTS.md activity
  - `0bbdbf8` 2025-11-23 Add AGENTS.md and improve justfile agent commands
  - `791a962` 2025-11-23 Flesh out AGENTS.md (incorporate relevant rules for tuick)
  - `af16150` 2025-11-23 Move code quality rules to specialized agent file
  - `85c9f38` 2025-11-27 Add technical debt, architecture, and coding patterns to AGENTS.md
  - `b3aa473` 2025-12-05 Update AGENTS.md: one-letter commands, Python GIL version
  - `331f5ce` 2025-12-08 Add real worker integration tests with optimized teardown
- **Notes:** Most AGENTS.md-heavy of the scratch repos. Shows cross-pollination from tuick project. Agent-specific `just` recipes pattern established here.

### scratch/emojipack
- **Path:** `~/code/claudeutils/scratch/emojipack`
- **Commits:** 70 (expected ~70)
- **Date range:** 2025-10-12 to 2026-01-08
- **Agentic commits (path):** 8
  - `9cc5c62` 2025-10-12 Initial commit (includes AGENTS.md)
  - `5a3c445` 2025-10-15 AGENTS.md: Testing, assert value of complex object
  - `996158f` 2025-10-18 AGENTS.md TDD: Red-Green does not apply when removing code
  - `4d6a333` 2025-10-18 Overhaul AGENTS.md
- **Notes:** Earliest structured TDD rules. "Red-Green does not apply when removing code" — first exception-based refinement.

### scratch/home
- **Path:** `~/code/claudeutils/scratch/home`
- **Commits:** 76 (expected ~76)
- **Date range:** 2025-11-05 to 2026-01-13
- **Agentic commits (path):** 8
  - `e31a4c0` 2026-01-12 Initial commit
  - `deb0d91` 2026-01-13 Formalize orchestrator constraints and subagent protocol
  - `055c6db` 2026-01-13 Update AGENTS.md: strengthen subagent protocol
  - `52f34eb` 2026-01-13 Fix AGENTS.md: make commit delegation explicit
  - `d749bf7` 2026-01-13 AGENTS.md: add terse prompt guidance
- **Notes:** Most architecturally significant. Introduces: orchestrator model (opus orchestrates, haiku/sonnet execute), file organization table, session management, sub-agent delegation protocol, commit workflow delegation. All in 2 days.

### scratch/pytest-md
- **Path:** `~/code/claudeutils/scratch/pytest-md`
- **Commits:** 55 (expected ~55)
- **Date range:** 2026-01-02 to 2026-01-12
- **Agentic commits (path):** 19
  - `1600882` 2026-01-02 Initial commit: pytest markdown console output
  - `fd939eb` 2026-01-03 Add Claude Code settings configuration
  - `69bf88b` 2026-01-12 Add TDD workflow skills and session log design
  - `94d2622` 2026-01-12 Restructure skills to Claude Code format
  - `aa8ee90` 2026-01-12 Add commit and handoff skills for Claude Code
- **Notes:** Bridge between Claude Desktop era and Claude Code. First `.claude/` directory, first skills (commit, handoff), first session log design.

## Parallel Projects (8)

### pytest-md
- **Path:** `~/code/pytest-md`
- **Commits:** 49 (expected ~49)
- **Date range:** 2026-01-02 to 2026-01-10 (main); agent-core nested: 204 commits, 2026-01-15 to 2026-02-06
- **Agentic commits (path):** 30
  - `f82e7a2` 2026-01-28 Add CLAUDE.md with @file references and update agent-core submodule
  - `16f7953` 2026-01-20 Restructure Claude Code skills and add agent-core submodule
  - `eaa2498` 2026-02-06 Migrate to agent-core Tier 2 structure
- **Agent-core nested repo:** 204 commits (2026-01-15 to 2026-02-06). Agent-core's origin before submodule extraction.

### home
- **Path:** `~/code/home`
- **Commits:** 157 (expected ~157)
- **Date range:** 2025-11-05 to 2026-03-11
- **Migration:** `091073f` 2026-01-18 "Rename AGENTS.md→CLAUDE.md, add load rule for session context"
- **Agent-core adoption:** `83cef17` 2026-01-22 "Add agent-core submodule and symlink skills/agents"
- **Agentic commits (path):** 63 — heaviest consumer of agent-core patterns

### tuick
- **Path:** `~/code/tuick`
- **Commits:** 190 (expected ~190)
- **Date range:** 2025-10-25 to 2026-01-03
- **Agent instruction files:** Both AGENTS.md and CLAUDE.md (coexistence, not migration)
- **CLAUDE.md purpose:** "Follow all rules in @AGENTS.md — this file contains Claude-specific directives only" (task delegation, haiku model usage)
- **Agentic commits (path):** 42

### jobsearch
- **Path:** `~/code/jobsearch`
- **Commits:** 129 (expected ~129)
- **Date range:** 2025-10-02 to 2026-01-22
- **Migration:** `eec32b4` 2025-10-07 "Merge CLAUDE.md into AGENTS.md" — reverse migration (CLAUDE.md→AGENTS.md)
- **Agentic commits (path):** 28

### devddaanet
- **Path:** `~/code/devddaanet`
- **Commits:** 63 (expected ~63)
- **Date range:** 2026-03-05 to 2026-03-11
- **Pattern usage:** worktree, deliverable-review, runbook/orchestrate (20+ commits)
- **Agentic commits (path):** 63 — every commit is agentic

### deepface
- **Path:** `~/code/deepface`
- **Commits:** 2024 (brief said "Feb 2026 commits")
- **Agent instruction files:** None
- **Agentic commits (path):** 0
- **Notes:** Large OSS project. Claude-assisted test contributions visible in session logs only, not in repo.

### emojipack (standalone)
- **Path:** `~/code/emojipack`
- **Commits:** 70 — identical to scratch/emojipack (same repo, same history)
- **Notes:** Not an independent data point.

### ddaanet
- **Path:** `~/code/ddaanet`
- **Commits:** 214 (expected ~214)
- **Date range:** 2020-04-02 to 2026-02-18
- **Migration:** `f8ece02` 2025-07-11 "Add auto-generated CLAUDE.md" → `2c61287` 2026-01-08 "Replace CLAUDE.md with AGENTS.md"
- **Agentic commits (path):** 11 (all Jan 2026)

## Non-agentic Repos (2)

### celebtwin
- **Path:** `~/code/celebtwin`
- **Commits:** 256 (expected ~256)
- **Date range:** 2025-05-31 to 2025-07-22
- **Agent instruction files:** None
- **Gitmoji usage:** 40/256 commits (16%)

### calendar-cli
- **Path:** `~/code/calendar-cli`
- **Commits:** 11 (expected ~11)
- **Date range:** 2025-04-18 to 2025-07-31
- **Agent instruction files:** None
- **Gitmoji usage:** 0/11

## Special: pytest-md/agent-core (nested)
- **Path:** `~/code/pytest-md/agent-core`
- **Commits:** 204
- **Date range:** 2026-01-15 to 2026-02-06
