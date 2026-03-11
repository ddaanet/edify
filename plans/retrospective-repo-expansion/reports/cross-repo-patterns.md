# Cross-Repo Patterns — New Evidence Beyond Existing 5 Topics

Three cross-repo patterns not captured by the existing topic reports.

## 1. Agent Instruction Evolution Arc

The naming and structure of agent instruction files evolved through distinct phases:

### Phase A: rules.md (Sep 2025)

**Repo:** `rules` | **Evidence:** 9 of 15 commits

Initial form: flat list of development rules. No agent self-modification. Human curates, agent consumes.

```
# Development Rules         (rules, 7b0a4b4, 2025-09-30)
## Version Control
## Python Environment
## Code Quality
## File Operations
```

Renamed to AGENTS.md on final day (`eacf188`, 2025-10-02). The rename signals: these aren't just rules — they're specifically for agents.

### Phase B: AGENTS.md with hash-tag directives (Oct 2025)

**Repos:** `scratch/emojipack` → `tuick` → `jobsearch`

Template propagation visible across repos. Same core content, project-specific additions:

```
# AI Agent and Development Rules    (scratch/emojipack, 9cc5c62, 2025-10-12)
- #todo Do the first item of TODO.md
- #tdd Follow TDD: Red-Green-Commit-Refactor-Commit
- #just Run `just agent` before every commit
```

The `#hashtag` prefix is inline metadata — labels for rules, enabling reference. Dropped by Dec 2025 (tuick removes them in `7dfefca`).

### Phase C: Agent Memory model (Nov 2025)

**Repo:** `oklch-theme` | **Evidence:** `b0c0d64`, `64cbf8f`

Gemini-era departure: AGENTS.md as "Agent Memory" with self-update protocol. Agent performs retrospective, writes to AGENTS.md. First agent→file write loop.

### Phase D: Structured AGENTS.md with sections (Nov-Dec 2025)

**Repos:** `scratch/box-api` → `tuick`

Evolution from flat list to structured document with sections:
- Agent-specific commands (just agent, just agent-check)
- Role-separated sections (agent vs human commands)
- Multi-agent system (`tuick`: core.md + agent-specific files)
- Cognitive protocols experiment (`tuick`: added then removed)

### Phase E: AGENTS.md + CLAUDE.md coexistence (Dec 2025 – Jan 2026)

**Repos:** `tuick`, `jobsearch`

Three different coexistence models:
1. **tuick:** CLAUDE.md as overlay: "Follow all rules in @AGENTS.md — Claude-specific directives only"
2. **jobsearch:** CLAUDE.md merged INTO AGENTS.md (reverse migration, Oct 2025)
3. **ddaanet:** Auto-generated CLAUDE.md replaced by hand-crafted AGENTS.md (Jan 2026)

No settled convention. The CLAUDE.md name existed as early as Oct 2025 (jobsearch) but wasn't standard.

### Phase F: Claude Code era with .claude/ directory (Jan 2026)

**Repos:** `scratch/pytest-md` → `pytest-md` → `home`

`.claude/` directory, settings.json, skills, agents. AGENTS.md→CLAUDE.md migration.
- `scratch/pytest-md` (`fd939eb`, 2026-01-03): First `.claude/settings.json`
- `home` (`091073f`, 2026-01-18): "Rename AGENTS.md→CLAUDE.md"
- `pytest-md` (`f82e7a2`, 2026-01-28): "Add CLAUDE.md with @file references"

### Phase G: CLAUDE.md + agent-core + fragments (Jan-Feb 2026)

**Repos:** `pytest-md/agent-core` → `home` → `claudeutils`

Extraction into shared infrastructure. Per-project AGENTS.md/CLAUDE.md → shared fragments + decisions + skills.

### Summary Timeline

| Date | Phase | Repo | Key Commit |
|------|-------|------|-----------|
| 2025-09-30 | A: rules.md | rules | `7b0a4b4` Initial commit |
| 2025-10-02 | A→B: rename | rules | `eacf188` Rename to AGENTS.md |
| 2025-10-12 | B: #hashtag directives | scratch/emojipack | `9cc5c62` Template propagated |
| 2025-10-25 | B: propagation | tuick | `7d2fa67` Same template |
| 2025-11-28 | C: Agent Memory | oklch-theme | `b0c0d64` Self-update protocol |
| 2025-11-23 | D: structured sections | scratch/box-api | `0bbdbf8` Role-separated commands |
| 2025-12-15 | D: multi-agent | tuick | `7a97ef3` Multi-agent restructuring |
| 2026-01-03 | F: .claude/ | scratch/pytest-md | `fd939eb` Settings.json |
| 2026-01-12 | F: skills | scratch/pytest-md | `aa8ee90` Commit/handoff skills |
| 2026-01-15 | G: agent-core | pytest-md/agent-core | `5783aef` Shared infrastructure |
| 2026-01-18 | F: migration | home | `091073f` AGENTS.md→CLAUDE.md |

## 2. Pattern Propagation Timeline

Which claudeutils practices appeared in parallel projects and when.

### Patterns and their propagation

| Pattern | Origin | First external appearance | Evidence |
|---------|--------|--------------------------|----------|
| `just agent` commit gate | scratch/emojipack (Oct 12) | tuick (Oct 25), scratch/box-api (Nov 23) | Same recipe name and purpose across 3+ repos |
| TDD Red-Green-Refactor | scratch/emojipack (Oct 12) | tuick (Oct 25), scratch/box-api (Nov 23) | Identical TDD section text in AGENTS.md |
| Gitmoji convention | scratch/emojipack (Oct 18) | tuick (Oct 25), jobsearch (Oct 8) | Gitmoji reference in AGENTS.md |
| Session.md tracking | scratch/home (Jan 12) | home (Jan 12), ddaanet (Jan 8) | Session management section in AGENTS.md |
| Commit delegation | scratch/home (Jan 13) | home (Jan 13) | "Use /commit-commands:commit to commit" |
| .claude/ directory | scratch/pytest-md (Jan 3) | pytest-md (Jan 3), jobsearch (Jan 21) | settings.json files |
| Agent-core submodule | pytest-md (Jan 20) | home (Jan 22), devddaanet (Mar 5) | .gitmodules + agent-core/ |
| CLAUDE.md with @refs | pytest-md (Jan 28) | home (Jan 23) | @file reference pattern |
| Worktree workflow | claudeutils (Feb 2026) | devddaanet (Mar 2026) | worktree-sync feature |
| Deliverable-review | claudeutils (Feb 2026) | devddaanet (Mar 2026) | Full review→fix→re-review cycle |

### Propagation speed

- **Fast (days):** scratch/home → home (same content, immediate propagation — same developer, parallel work)
- **Medium (weeks):** scratch/emojipack patterns → tuick, scratch/box-api (template copy with project-specific adaptation)
- **Slow (months):** claudeutils patterns → devddaanet (full pipeline adoption required infrastructure maturity)

## 3. Agent-core Extraction Story

### Phase 1: Per-project duplication (Oct 2025 – Jan 2026)

Each project maintained its own AGENTS.md. Cross-pollination via copy-paste-adapt:
- `rules` → `scratch/emojipack` → `tuick` → `scratch/box-api` (template chain visible in content similarity)
- Each copy diverged over time (tuick added cognitive protocols, scratch/box-api added infrastructure sections)

### Phase 2: Skills emerge (Jan 2026)

`scratch/pytest-md` creates `.claude/` directory with skills (commit, handoff, TDD workflow). Skills are per-project — no sharing mechanism yet.

### Phase 3: Extraction into agent-core (Jan 15, 2026)

`pytest-md/agent-core` initialized with `5783aef` "Initialize agent-core repository structure."

First 5 commits show extraction sequence:
1. Repository structure
2. Extract shared justfile recipes
3. Extract shared ruff and mypy configurations
4. Add agent instruction fragments
5. Add baseline task agent and weak orchestrator pattern

### Phase 4: Submodule adoption (Jan 20 – Mar 2026)

| Date | Repo | Event |
|------|------|-------|
| 2026-01-20 | pytest-md | First agent-core submodule addition |
| 2026-01-22 | home | Agent-core submodule + skill symlinks |
| 2026-02-06 | pytest-md | Migrate to agent-core Tier 2 structure |
| 2026-03-05 | devddaanet | Born with agent-core (initial commit includes submodule) |

### Phase 5: Maturation (Feb – Mar 2026)

Agent-core accumulates 204 commits in the pytest-md nested repo (Jan 15 – Feb 6), then the claudeutils main repo becomes the primary development location. By March, new projects (devddaanet) are born with agent-core from the start — adoption cost approaches zero.
