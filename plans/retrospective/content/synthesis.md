# Agentic Programming: Evidence from 16 Repos

How agent instructions evolved from a 14-rule flat file to a shared framework with fragments, skills, hooks, and a recall system — traced through git history across 16 repositories, September 2025 to March 2026.

---

## The Landscape

**16 repos. 1,459 commits with agentic evidence. 6 months.**

The repos fall into four eras:

| Era | Period | Repos | What happened |
|-----|--------|-------|---------------|
| Pre-agentic | Apr–Jul 2025 | calendar-cli, celebtwin | Claude-assisted development with no agent instructions |
| Foundation | Sep–Oct 2025 | rules, emojipack, jobsearch, tuick | First agent instructions, TDD rules, gitmoji |
| Expansion | Nov 2025–Jan 2026 | oklch-theme, box-api, home, pytest-md | LLM awareness, orchestration, delegation, session management |
| Consolidation | Jan–Mar 2026 | pytest-md, home, ddaanet, devddaanet | Agent-core extraction, CLAUDE.md migration, full pipeline |

Two repos produced no agentic evidence: `deepface` (OSS contribution, Claude-assisted but no instructions committed) and `emojipack` standalone (identical to scratch copy). `celebtwin` and `calendar-cli` serve as pre-agentic contrast.

**Note on `scratch/` paths:** Several repos appear in git history under `~/code/claudeutils/scratch/` (box-api, home, pytest-md, emojipack). These are the same projects that live in `~/code/` — the scratch/ copies were a workaround to access multiple repos from within the claudeutils Claude Code session (predating `/add-dir` or as an alternative to it). The scratch/ path is a tooling artifact, not an architectural decision or distinct era.

---

## Before Agent Instructions

**calendar-cli** (Apr 2025, 11 commits): The earliest Claude-assisted project. Commit messages are informal paragraphs. No gitmoji, no build system, no linting. Represents the zero state.

**celebtwin** (May–Jul 2025, 256 commits): Claude-assisted with some tooling — gitmoji (16% of commits), GitHub Actions CI, mypy, make-based build. But no AGENTS.md, no session tracking, no TDD formalization, no commit gates. Claude helps write code; nothing tells Claude how to behave.

The gap between celebtwin (Jul 2025) and the first agent instructions (Sep 2025) is two months. What changed: Claude Desktop → Claude Code, and the realization that behavioral rules could be stored in the repo.

---

## Phase 1: The Template (Sep–Oct 2025)

### rules — The Origin

`~/code/rules`, 15 commits over 3 days.

The first `rules.md` (`7b0a4b4`, 2025-09-30) is 14 rules in flat markdown:

```
# Development Rules
## Version Control
- Commit changes regularly with descriptive messages
## Code Quality
- Write fully typed code
- Use modern type hints features
```

Two days later (`eacf188`, 2025-10-02): renamed to `AGENTS.md`. The naming convention is born. Nine of fifteen commits touch this file — the repo exists to develop the rules.

### emojipack — TDD Takes Shape

`~/code/emojipack` (also `~/code/claudeutils/scratch/emojipack`), 70 commits, Oct 2025–Jan 2026.

Takes the rules template and adds structured TDD:

```
- #tdd Follow TDD: Red-Green-Commit-Refactor-Commit
- #just Run `just agent` before every commit
```

The `#hashtag` prefix is inline metadata — labels for rules. Dropped by December. But the `just agent` commit gate persists across every subsequent project.

Key refinement (`996158f`, 2025-10-18): "Red-Green does not apply when removing code." First exception-based rule — the TDD discipline encounters a real case it doesn't cover, and the instructions adapt.

### tuick — Most Iterated

`~/code/tuick`, 190 commits, Oct 2025–Jan 2026. **18 direct AGENTS.md commits** — more than any other project.

Starts with the emojipack template. Iterates through:
- Retrospective-driven updates (`c73d5c0`: "AGENTS.md: retrospective updates")
- Cognitive protocols experiment (`a3e15a1`, Dec 12: "Update AGENTS.md with cognitive protocols")
- Multi-agent restructuring (`7a97ef3`, Dec 15: core.md + agent-specific files)
- Removal of overengineered metacognition (`26c3b5d`, Dec 15: "Remove epistemic standards")

The cognitive protocols episode is an evolutionary dead end. Added and removed on the same day. The repo shows that not all experimentation survives — some ideas are tested and discarded.

tuick also introduces AGENTS.md + CLAUDE.md coexistence. CLAUDE.md says: "Follow all rules in @AGENTS.md — this file contains Claude-specific directives only." Claude-specific additions: task delegation to haiku. This is multi-agent strategy before it had a name.

### jobsearch — Naming Confusion

`~/code/jobsearch`, 129 commits, Oct 2025–Jan 2026.

Has the earliest CLAUDE.md (Oct 2, 2025) — predating the convention. Then `eec32b4` (Oct 7): "Merge CLAUDE.md into AGENTS.md with Global and Project sections." A reverse migration. The naming convention is not yet settled.

Late Claude Code adoption (Jan 2026, three months after the AGENTS.md work): `.claude/settings.json`, Claude Code skills.

---

## Phase 2: Architecture Emerges (Nov 2025–Jan 2026)

### oklch-theme — LLM Self-Awareness

`~/code/oklch-theme`, 8 commits, Nov–Dec 2025. Started with Gemini, later iterated in Claude Desktop.

AGENTS.md is titled "Agent Memory" with a self-update protocol: "At the end of each session, perform a retrospective and update this file with reusable feedback." First explicit agent→file write loop.

The LLM Limitation Awareness section (`64cbf8f`, Dec 1) is the earliest known metacognitive rules:

> Flag uncertainty and request validation when:
> - Multi-step reasoning (>3 steps): Complex logic chains accumulate errors
> - Long context (>50k tokens): Information recall degrades
> - Known failure modes: Hallucination, negation errors, context conflation

The LLM Limitation Awareness section is metacognitive wishful thinking — same class as tuick's cognitive protocols (added and removed in 3 days). Asking an LLM to "flag uncertainty" assumes a confidence-monitoring capability that doesn't exist. The section is historically notable as the earliest attempt at the problem, but it's not a precursor to pushback — it's the same dead end that cognitive protocols hit, just less elaborate.

Same commit adds: "Opus runs as orchestrator. Write design to `plans/` before validation. Cheaper to update a file than re-output the whole plan." The design-then-review pattern and the opus orchestrator both emerge here.

### box-api — Infrastructure Rules

`~/code/box-api` (also `~/code/claudeutils/scratch/box-api`), 46 commits, Nov–Dec 2025. 23 agentic commits.

Introduces agent-vs-human command separation:
```
### Agent Commands (for AI/automated use)
- `just agent` - Run all checks and tests
### Manual Developer Commands (user-only)
- `just dev` - Run checks and tests
```

Cross-pollination visible: `791a962` (Nov 23) — "Flesh out AGENTS.md (incorporate relevant rules for tuick)." Rules flow between projects manually.

### home — The Architectural Leap

`~/code/home` (also `~/code/claudeutils/scratch/home`), 76 commits, Nov 2025–Jan 2026. **Most architecturally significant pre-claudeutils repo.**

In two days (Jan 12–13), introduces everything that becomes claudeutils architecture:

**File organization table:**
```
| Content Type | Location |
|---|---|
| Behavioral direction | AGENTS.md |
| Design decisions | design-decisions.md |
| Session context | session.md |
| Designs, plans | plans/ |
```

**Orchestrator constraints:**
```
Opus orchestrator operates read-only with minimal context footprint.
Allowed: Read tools, Task delegation, Writing to plans/ and AGENTS.md only.
Delegate: All source file edits, Bash commands, Commits (via Task, not Skill).
```

**Commit delegation protocol** — 7 commits iterating on this in one day:
```
Orchestrator writes commit messages (has context), never runs git commands directly.
```

**Sub-agent instructions:**
```
Prefer specialized tools over Bash (Read, LS, Glob, Grep, Write, Edit).
Always start execution prompts with: "First, read plans/subagent-protocol.md."
```

The rapid iteration (7 commits on commit delegation alone) shows active refinement through real failures. Each commit message describes what was wrong with the previous version.

### pytest-md — Token Economy and Skills

`~/code/pytest-md` (also `~/code/claudeutils/scratch/pytest-md`), 55 commits, Jan 2026. Bridge between Claude Desktop and Claude Code eras.

Introduces:
- First `.claude/settings.json` (`fd939eb`, Jan 3)
- First skills: commit, handoff (`aa8ee90`, Jan 12)
- Session log design (`69bf88b`, Jan 12)
- Token economy as measurable requirement: "Do not guess token counts. Always use `claudeutils tokens sonnet <file>` to verify."
- Session.md size discipline: 100-line max

---

## Phase 3: Consolidation (Jan–Mar 2026)

### Agent-core Extraction

The copy-paste-adapt model of Phase 1-2 doesn't scale. Each project maintains its own AGENTS.md, diverging over time. Agent-core is the answer.

**Origin:** `~/code/pytest-md/plugin`, 204 commits, Jan 15–Feb 6, 2026. A nested repo inside pytest-md.

First commit (`5783aef`): "Initialize plugin repository structure." The next four commits show the extraction sequence: shared justfile recipes, shared ruff/mypy configs, agent instruction fragments, baseline task agent.

**Adoption timeline:**

| Date | Repo | Event |
|------|------|-------|
| Jan 15 | pytest-md/plugin | Created (204 commits over 3 weeks) |
| Jan 20 | pytest-md | First submodule addition |
| Jan 22 | home | Agent-core submodule + skill symlinks |
| Feb 6 | pytest-md | Migrate to plugin Tier 2 structure |
| Mar 5 | devddaanet | Born with plugin from initial commit |

By March, new projects include plugin in their initial commit. Adoption cost approaches zero.

### The AGENTS.md → CLAUDE.md Migration

Four different migration patterns across repos:

| Pattern | Repo | Evidence |
|---------|------|----------|
| **Rename** | home | `091073f` (Jan 18): "Rename AGENTS.md→CLAUDE.md" |
| **Coexistence** | tuick | CLAUDE.md as overlay on AGENTS.md |
| **Reverse merge** | jobsearch | CLAUDE.md merged INTO AGENTS.md (Oct 2025) |
| **Replacement** | ddaanet | Auto-generated CLAUDE.md replaced by AGENTS.md (Jan 2026) |

ddaanet's story is the most dramatic: 203 pre-agentic commits (2020–2025), an auto-generated CLAUDE.md in July 2025 (likely Claude Code scaffold), then a single-day burst in January 2026 replacing it with sophisticated AGENTS.md containing session tracking, design decisions, and commit workflow — all claudeutils patterns transplanted in one session.

### home — Longest Evolution

`~/code/home`, 157 commits, Nov 2025–Mar 2026. 63 agentic file-path commits — heaviest consumer.

Shows the complete lifecycle:
1. AGENTS.md with orchestrator model (Jan 12)
2. AGENTS.md→CLAUDE.md rename (Jan 18)
3. Agent-core submodule (Jan 22)
4. Token-efficient bash rules (Jan 24)
5. Handoff-haiku skill (Jan 30)
6. Agent-core hooks and symlinks (Feb 2, Feb 27)
7. Memory infrastructure (Feb 27)
8. Context bar statusline (Mar 2026)

Every major claudeutils pattern propagated here within days to weeks of its introduction.

### devddaanet — Full Pipeline in Production

`~/code/devddaanet`, 63 commits, Mar 5–11, 2026. **Every commit is agentic.** Born with plugin from initial commit.

Shows the full claudeutils pipeline working on a real project:
- Requirements → design → runbook → orchestrate → deliverable-review → fix → re-review → delivered

The deliverable-review cycle (`265c8c7` → `cae9155` → `4ffb1ea`) completed cleanly. However, post-delivery commits tell a different story: 3 of the next 5 commits are bug fixes — sync crash, worktree deletion bug, unison crashes — followed by a discovery mechanism overhaul. The review caught some issues but not all; the delivered result needed continued debugging.

---

## Five Topics: New Evidence

The existing retrospective covered five topics from claudeutils' own history. The expanded repos add pre-history and external validation.

### 1. Memory System

**Pre-history:** Agent instructions ARE the proto-memory system. rules.md (Sep 2025) is human-written rules consumed by agents. oklch-theme (Nov 2025) adds agent self-update: "perform a retrospective and update this file." home (Jan 2026) introduces structured file taxonomy (AGENTS.md, session.md, design-decisions.md, plans/).

**Arc:** Human-written flat rules → agent retrospective self-update → structured file taxonomy → shared infrastructure (plugin) → memory-index + recall system.

**Spontaneous recall rate: 0%.** Direct measurement across 129 recall tool invocations in 69 sessions found zero spontaneous agent-initiated lookups. Every invocation was either skill-procedural (87.6% — mandated by `/design` triage, `/runbook` steps, or discussion-mode grounding) or user-triggered (12.4%). The original "actionable index" concept — entries loaded in context that would self-trigger agent recognition — did not produce spontaneous recall behavior. Agents had the tools but never used them without procedural instruction. (Method: `plans/measure-agent-recall/report.md`)

This is a stronger finding than the previously cited 4.1% statistic, which measured user-initiated `/when`/`/how` skill invocations (users testing the tool). The 0% measures agent behavior directly: agents never independently decided to consult the recall system.

### 2. Pushback

**Pre-history:** Early AGENTS.md actively suppresses pushback: "Proceed autonomously without asking until all tasks complete" (rules, emojipack, tuick). oklch-theme's LLM Limitation Awareness (Nov 2025) and tuick's cognitive protocols (Dec 2025) both attempt metacognitive solutions — asking the agent to monitor its own uncertainty. Both are wishful thinking: LLMs can't monitor confidence they don't have. home (Jan 2026) shifts to structural enforcement: "require protocol read before execution."

**Arc:** "Proceed autonomously" (anti-pushback) → metacognitive wishful thinking (oklch-theme "flag uncertainty", tuick cognitive protocols — both dead ends) → structural enforcement → formalized pushback protocol.

### 3. Deliverable-Review

**Pre-history:** emojipack (Oct 2025) has the first quality gate exception: "Red-Green does not apply when removing code." tuick (Dec 2025) adds: "Require explanatory comments for all suppressions."

**External use:** devddaanet (Mar 2026) runs the full review cycle in production. 1 critical + 3 minor findings → fixed → re-reviewed → delivered. However, post-delivery commits include 3 bug fixes and a sync overhaul — the review didn't catch everything.

### 4. Ground Skill

**Pre-history:** Limited. rules (Sep 2025) shows human-mediated knowledge import: "Incorporate zed rules, adjusted by hand." box-api (Nov 2025) shows cross-project import: "incorporate relevant rules for tuick." These are precursors to grounding-as-methodology, but ground skill origins are mostly internal to claudeutils.

### 5. Structural Enforcement

**Pre-history:** emojipack (Oct 2025): "`just agent` before every commit" — the first commit gate. box-api (Nov 2025): agent-vs-human command separation. pytest-md (Jan 2026): `.claude/settings.json` — platform-level configuration as enforcement. home (Jan 2026): orchestrator constraints (Allowed/Delegate model).

**Arc:** `just agent` gate → agent-specific recipes → platform config → orchestrator constraints → shared infrastructure (plugin) → D+B tool-call anchoring → PreToolUse hooks.

---

## Three New Patterns

### Agent Instruction Evolution Arc

```
rules.md (flat rules)
  → AGENTS.md with #hashtag directives (inline metadata)
    → Agent Memory with self-update (agent→file write loop)
      → Structured sections with role separation (agent vs human)
        → Multi-agent file system (core.md + agent-specific)
          → AGENTS.md + CLAUDE.md coexistence (naming unsettled)
            → .claude/ directory with settings, skills, agents
              → CLAUDE.md with @file references to fragments
                → plugin submodule (shared infrastructure)
```

Not a linear progression. tuick's cognitive protocols were added and removed the same day. jobsearch's CLAUDE.md was reverse-merged into AGENTS.md. Multiple naming conventions coexisted for months.

### Pattern Propagation

Patterns propagated at different speeds:

- **Immediate** (days): home's AGENTS.md iterations propagated to claudeutils within days. The orchestrator protocol appears in both repos on the same dates.
- **Template copy** (weeks): emojipack → tuick → box-api. Core TDD and `just agent` rules copied with project-specific adaptations. Content similarity visible in AGENTS.md text.
- **Infrastructure adoption** (months): claudeutils patterns → devddaanet. Full pipeline adoption requires plugin maturity. devddaanet in March 2026 uses patterns that took months to develop in claudeutils.

### Agent-core as Extraction

The move from per-project AGENTS.md to shared plugin follows a classic library extraction pattern:

1. **Duplication** (Oct 2025–Jan 2026): Each project copies and adapts rules. Divergence accumulates.
2. **Skills emerge** (Jan 2026): pytest-md creates `.claude/` with commit and handoff skills. Per-project, not shared.
3. **Extraction** (Jan 15): Agent-core initialized in pytest-md. Shared recipes, configs, fragments, agents.
4. **Adoption** (Jan–Mar 2026): Submodule added to pytest-md, home, devddaanet. Per-project AGENTS.md replaced by CLAUDE.md + @references to shared fragments.
5. **Zero-cost adoption** (Mar 2026): New projects include plugin in their initial commit.

---

## Evidence Quality Notes

- All claims grounded in specific commit hashes, verifiable via `git -C <path> show <hash>`
- Content excerpts from `git show` at key commits, not reconstructed from memory
- deepface (2024 commits) excluded — no agentic evidence in repo despite Claude-assisted contributions
- emojipack exists at both `~/code/emojipack` and `~/code/claudeutils/scratch/emojipack` (identical history) — counted once. scratch/ copies are a tooling workaround (see note above)
- oklch-theme started with Gemini, later iterated in Claude Desktop — AGENTS.md references "Gemini agent" but final commit is Claude Desktop work
