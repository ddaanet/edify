# Brief: Retrospective Repo Expansion

Extend the retrospective evidence base (plans/retrospective/) with git history from additional repos under ~/code. The existing retrospective covers claudeutils only (Dec 2025–present). These repos contain the pre-history and parallel evolution.

## Repo Inventory

### Pre-claudeutils agentic evolution (chronological)
- `~/code/rules` — Oct 2025, 15 commits. Earliest AGENTS.md (renamed from rules.md). Proto-agent instructions.
- `~/code/oklch-theme` — Nov-Dec 2025, 8 commits. Early Claude Desktop era. First AGENTS.md with "LLM awareness."
- `~/code/claudeutils/scratch/box-api` — Nov-Dec 2025, 46 commits. Worker integration tests, AGENTS.md, celery+websocket.
- `~/code/claudeutils/scratch/emojipack` — Oct 2025-Jan 2026, 70 commits. CLI tooling, justfile recipes.
- `~/code/claudeutils/scratch/home` — Nov 2025-Jan 2026, 76 commits. Orchestrator delegation, subagent protocols, commit workflow.
- `~/code/claudeutils/scratch/pytest-md` — Jan 2026, 55 commits. TDD workflow skills, session log design, skill restructuring.

### Parallel agentic projects (contemporaneous)
- `~/code/pytest-md` — Jan 2026, 49 commits. pytest-markdown-report. Has agent-core as nested repo (204 commits, Jan-Feb 2026) — agent-core's origin before submodule extraction.
- `~/code/home` — Nov 2025-Mar 2026, 157 commits. Dotfiles + context bar. Agent-core consumer. Shows pattern propagation.
- `~/code/tuick` — Oct 2025-Jan 2026, 190 commits. TUI toolkit. Both AGENTS.md and CLAUDE.md (migration signal). Release automation.
- `~/code/jobsearch` — Oct 2025-Jan 2026, 129 commits. Claude.ai import, skill invocation patterns.
- `~/code/devddaanet` — Mar 2026, 63 commits. Worktree-sync feature. Deliverable-review used in the wild.
- `~/code/deepface` — OSS contribution, Feb 2026 commits. Claude-assisted test writing on external project.
- `~/code/emojipack` — Oct 2025-Jan 2026, 70 commits. Standalone (not scratch copy).
- `~/code/ddaanet` — 2020-Feb 2026, 214 commits. Long-lived project, late-stage .claude/ addition.

### Non-agentic but Claude-assisted (pre-history)
- `~/code/celebtwin` — May-Jul 2025, 256 commits. Pre-agentic Claude project. GitHub Actions, gitmoji.
- `~/code/calendar-cli` — Apr-Jul 2025, 11 commits. Early Claude-assisted CLI.

### Excluded
- `~/code/claudeutils/tmp/test_rm_debug` — mirror of claudeutils (test artifact)
- `~/code/devddaanet/claudeutils` — shallow clone (1 commit)
- `~/code/django`, `~/code/openstreetmap-carto` — upstream forks, not Claude work
- `~/code/claude-code-system-prompts` — collected prompts, not a development project

## Evidence Value

**For existing retrospective topics:**
- Memory system evolution: `scratch/home` (subagent-protocol, AGENTS.md iteration) → `scratch/pytest-md` (session log design) → `pytest-md/agent-core` (memory-index origin)
- Pushback protocol: `rules` (earliest agent instructions) → evolution of AGENTS.md across repos shows pre-pushback state
- Structural enforcement: `scratch/home` (orchestrator delegation rules) → `scratch/box-api` (AGENTS.md) → progressive formalization visible across repos
- AGENTS.md → CLAUDE.md migration: `tuick` has both files, transition visible in commit history

**New cross-repo patterns:**
- How agent instructions evolved: `rules` (flat rules.md) → `oklch-theme` (AGENTS.md) → `scratch/*` (specialized per-project) → claudeutils (CLAUDE.md + fragments + decisions)
- Pattern propagation: which practices from claudeutils appeared in parallel projects and when
- Agent-core extraction: `scratch/pytest-md` → `pytest-md/agent-core` → claudeutils submodule

## Hazards

- Nested repos: `claudeutils/scratch/*` are repos inside a repo. `pytest-md/agent-core` is a nested repo. `devddaanet/claudeutils` is a shallow clone. Git operations must target specific repos, not recurse blindly.
- `scratch/*` repos are under claudeutils but have independent git histories — they predate claudeutils's current structure.
- Some repos may have been created with Claude Desktop (chat), not Claude Code (CLI). Commit style and AGENTS.md presence are the distinguishing signals.
