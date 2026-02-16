# Session Handoff: 2026-02-16

**Status:** 3 worktrees merged (merge-data-loss, rm-amend, remaining-workflow-items). 2 worktrees active. Vet gate discussion: script Gate B, remove ambient vet fragment.

## Completed This Session

**worktree-merge-data-loss merged:**
- Lint debt fixed in worktree (70 ruff violations, 3 files over 400-line limit)
- Conflict resolved: `agent-core/skills/commit/SKILL.md` — main's separate-Bash-calls + branch's Gate bullet
- 13 TDD cycles (Track 1 removal guard + Track 2 merge correctness) + 1 general step (SKILL.md Mode C)
- Deliverable review (3 opus agents parallel): 0 critical, 3 major, 6 minor
  - Root: incomplete exit 2 handling in `_delete_branch` (cli.py:351)
  - Report: `plans/worktree-merge-data-loss/reports/deliverable-review.md`

**worktree-rm-amend merged:**
- Auto-amend merge commit when `rm` modifies session.md on merge commit HEAD
- Conflicts: `cli.py` (guard logic + amend feature combined), `scrape-validation.py` (lint reformatting)
- `_is_merge_commit` moved to utils.py, `_update_session_and_amend` extracted as helper
- Test assertions adapted for guard-aware output format

**Backlog re-scored:** 27 tasks, rev 2. Expand runbook topped at 2.6 (now complete). Report: `plans/reports/prioritization-2026-02-16.md`

**remaining-workflow-items merged:**
- FR-1: Reflect skill exit paths — produce session.md task format instead of prose descriptions
- FR-2: Tool-batching.md — Task tool parallelization section
- FR-3: Delegation.md — Delegate Resume pattern (resume before relaunch, 15-message heuristic)
- FR-4: Agent output audit — simplified verbose output in 3 agents (quiet-task, review-tdd-process, refactor)
- FR-5: Commit skill — removed Gate A (session freshness), kept Gate B (vet checkpoint) with proportionality
- Conflict: SKILL.md Gate A/B — branch deleted both, kept Gate B from main with proportionality update
- Artifacts: `plans/remaining-workflow-items/requirements.md`, `plans/remaining-workflow-items/reports/vet-review.md`

**Vet gate discussion (design decision):**
- Commit Gate A (session freshness) removed — handoff timing is user's decision
- Commit Gate B (vet checkpoint) kept but should be scripted (file classification + report existence check)
- Ambient vet requirement (`vet-requirement.md` fragment in CLAUDE.md) should be removed:
  - Unenforceable (aspirational rule, no gating mechanism)
  - Sub-agents don't see CLAUDE.md fragments — only fires in main session
  - Redundant: orchestrator handles vet via pipeline-contracts.md, commit gate catches interactive work
  - ~100 lines loaded every session for no enforcement value
- Execution context template + UNFIXABLE protocol → move to on-demand reference (memory index)

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-16.md (rev 2) -->

- [ ] **Address merge data loss review** — Fix 3 major findings from deliverable review | sonnet
  - Major 1: `_delete_branch` exit 2 on unexpected failure (cli.py:351)
  - Major 2: `sys.stderr.write` → `click.echo(..., err=True)` in merge.py + test capfd migration
  - Major 3: SKILL.md Mode C rm exit 2 handling
  - Report: `plans/worktree-merge-data-loss/reports/deliverable-review.md`

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Script commit vet gate** — Replace prose Gate B with scripted check (file classification + vet report existence) | sonnet
  - Part of commit skill optimization (FR-5 partially landed — Gate A removed, Gate B still prose)
  - Also: remove `vet-requirement.md` from CLAUDE.md `@`-references, move execution context template to memory index

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule

- [ ] **Vet delegation routing** — Route review to artifact-appropriate agent (vet-fix for code, skill-reviewer for skills, agent-creator for agents) | sonnet
  - General rule affecting vet-requirement.md and /runbook review delegation
  - agent-creator: Write+Read, confirmed cooperative in review mode (decisions/project-config.md:266)
  - skill-reviewer: Read/Grep/Glob only — cannot autofix, would need tool additions
  - No hook reviewer exists; no doc reviewer exists (readme skill is creation, not review)
  - Precedent: agent-creator repurposed for review via prompting (`/when agent-creator reviews agents`)

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart

- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Learnings consolidation done (491→32 lines) — FR-7 migration partially addressed via consolidation
  - **New scope:** `/remember` consolidation should validate trigger names before graduating to `/when` entries

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Memory-index auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check

- [ ] **Agent rule injection** — process improvements batch | sonnet
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Diagnostic opus review** — Interactive post-vet RCA methodology | `/requirements` | opus
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject vs index-and-recall
  - Methodology as skill referenced in design-vet-agent + outline-review-agent `skills:` frontmatter

- [ ] **Handoff insertion policy** — Change "append" to "insert at estimated priority position" in handoff skill | sonnet
  - Evidence: `p:` tasks distribute evenly (n=29), not append-biased. Agents correctly judge position.
  - Scripts: `plans/prototypes/correlate-pending-v2.py`

- [ ] **Pretool hook cd pattern** — Allow `cd <path> &&` pattern, check security implications | sonnet | restart
  - Load plugin-dev:hook-development skill for hook modification guidance
  - Current hook blocks ALL bash when cwd wrong, including `cd` to restore — creates catch-22

- [ ] **Handoff wt awareness** — Only consolidate memory in main repo or dedicated worktree | sonnet

- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet

- [ ] **Remember agent routing** — blocked on memory redesign | sonnet
  - When consolidating learnings actionable for sub-agents, route to agent templates (quiet-task.md, tdd-task.md) as additional target

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

- [ ] **Behavioral design** — `/design` nuanced conversational pattern intervention | opus
  - Requires synthesis from research on conversational patterns

- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` frontmatter | sonnet

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Existing: `bin/last-output`, `scripts/scrape-validation.py`, `plans/prototypes/*.py`
  - Requirements: `plans/prototypes/requirements.md` (multi-project scanning, directive extraction, git correlation)

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Rename vet agents** — `vet-fix-agent` → `correct-agent`, `vet-agent` → `review-agent` | sonnet | restart
  - Mechanical rename across agent definitions, fragments, skills, memory-index

- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart

- [ ] **Worktree skill adhoc mode** — Add mode for creating worktree from specific commit without task tracking | sonnet

- [ ] **Explore Anthropic plugins** — Install all 28 official plugins, explore for safety+security relevance | sonnet | restart
  - Repo: `github.com/anthropics/claude-plugins-official`

- [ ] **Ground state-machine review criteria** — Research state coverage validation in plan review | opus

- [ ] **Pre-merge untracked file fix** — `new --session` leaves session.md untracked on main | sonnet

- [ ] **Safety review expansion** — Implement pipeline changes from grounding research | opus
  - Input: `plans/reports/safety-review-grounding.md`
  - Depends on: Explore Anthropic plugins

- [ ] **Test diagnostic helper** — Replace `subprocess.run(..., check=True)` in test setup with stderr surfacing | sonnet

- [ ] **Runbook model assignment** — runbook skill assigns sonnet/haiku to prose edits on architectural artifacts; should apply design-decisions.md directive (opus for skill/fragment/agent edits) | opus

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design.md complete, vet in progress, planning next (design refreshed Feb 13)

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

- [ ] **Design workwoods** → `design-workwoods` — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: requirements

## Blockers / Gotchas

**Diagnostic review methodology converging:**
- Taxonomy, iteration protocol, priming template designed in conversation
- Opus critique validated approach, identified haiku paradox (resolved: discovery at capable tier, pre-assembled context for haiku)
- Methodology skill + design-vet-agent integration planned as follow-on task

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Headings must include "To" (e.g., "How To Augment Agent Context")
- Index keys must NOT include "to" — validator adds it automatically

## Next Steps

Next: Address merge data loss review (sonnet). 2 worktrees active (error-handling-design, design-workwoods). Learnings at 97/80 lines — run `/remember` soon.

## Reference Files

- `plans/reports/prioritization-2026-02-16.md` — WSJF task prioritization (rev 2, 27 tasks)
- `plans/worktree-merge-data-loss/reports/deliverable-review.md` — Consolidated review (3 major findings)
- `plans/reports/task-prioritization-methodology.md` — WSJF-adapted prioritization methodology
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/reports/safety-review-grounding.md` — Safety review grounding research
- `plans/remaining-workflow-items/requirements.md` — 6 FRs (reflect, batching, delegation, agents, commit)
