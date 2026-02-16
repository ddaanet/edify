# Session Handoff: 2026-02-16

**Status:** Vet proportionality merged. Commit skill allowlist fix applied. worktree-merge-data-loss blocked on lint debt. 4 worktrees active.

## Completed This Session

**Worktree skill fixes:**
- Sandbox bypass annotations on all mutation commands (`new`, `merge`, `rm`) in SKILL.md and sandbox-exemptions.md
- Mode C step 3: `_worktree rm` session.md cleanup now amends merge commit (not separate commit)

**Vet proportionality (merged from worktree):**
- Proportionality threshold in `vet-requirement.md` — self-review for ≤5 lines, ≤2 files, additive/corrective
- Commit skill Gate B updated with trivial-edit path

**Commit skill allowlist fix:**
- Removed batched `exec/set-xeuo` patterns — individual Bash calls for permission allowlist compatibility
- Added "one command per Bash call" constraint to Critical Constraints

**worktree-merge-data-loss merge attempted, reverted:**
- Merge succeeded but precommit failed: 70 ruff violations, 3 files over 400-line limit
- `git reset --hard` to pre-merge state, worktree still active with branch intact
- Lint debt must be fixed in worktree before next merge attempt

**Parallel worktree setup:**
- Created worktrees for error-handling-design, design-workwoods, worktree-rm-amend
- Cleaned stale debris from prior failed attempts (orphaned branches in parent + submodule)
- Model tier corrections: fragment authoring and design recovery are opus, not sonnet

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-16.md -->

- [ ] **Remaining workflow items** — Sub-items not captured in workflow-rca-fixes | sonnet
  - Orchestrate evolution — designed, ready for `/runbook` (design refreshed Feb 13)
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work (no mechanism exists)
  - Agent output optimization — remove summarize/report language from agents
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

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

- [ ] **Handoff insertion policy** — Change "append" to "insert at estimated priority position" in handoff skill | sonnet
  - Evidence: `p:` tasks distribute evenly (n=29), not append-biased. Agents correctly judge position.
  - Scripts: `plans/prototypes/correlate-pending-v2.py`

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Existing: `bin/last-output`, `scripts/scrape-validation.py`, `plans/prototypes/*.py`
  - Requirements: `plans/prototypes/requirements.md` (multi-project scanning, directive extraction, git correlation)

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Rename vet agents** — `vet-fix-agent` → `correct-agent`, `vet-agent` → `review-agent` | sonnet | restart
  - Pattern: outline must be corrected by one stronger than the generator (pipeline-contracts.md T2 table)
  - Mechanical rename across agent definitions, fragments, skills, memory-index
  - Conflict risk nullified: plugin-dev plugin provides skill-reviewer and agent-creator, no namespace collision

- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart
- [ ] **Expand runbook** — `/runbook plans/worktree-merge-data-loss/design.md` | sonnet
  - Outline reviewed and fixed, ready for full phase expansion
  - Phase 1: 13 TDD cycles (Track 1 removal guard + Track 2 merge correctness), haiku execution
  - Phase 2: 1 general step (SKILL.md Mode C), haiku execution
  - Opus review findings to incorporate during expansion: `plans/worktree-merge-data-loss/reports/runbook-outline-review-opus.md`
- [ ] **Worktree skill adhoc mode** — Add mode for creating worktree from specific commit without task tracking | sonnet

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

- [ ] **Design workwoods** → `design-workwoods` — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: requirements

- [ ] **Worktree rm amend** → `worktree-rm-amend` — Script amend into `_worktree rm` when HEAD is merge commit | `/design` | sonnet
  - Option B from discussion: rm detects merge commit via parent count, stages+amends session.md
  - Also address lint debt from worktree-merge-data-loss branch before merge

## Blockers / Gotchas

**worktree-merge-data-loss blocked on lint debt:**
- 70 ruff violations across 5 files, 3 files over 400-line limit
- Merge reverted — branch intact at `worktree-merge-data-loss` worktree
- Must fix in worktree, re-commit, then re-attempt merge

**Diagnostic review methodology converging:**
- Taxonomy, iteration protocol, priming template designed in conversation
- Opus critique validated approach, identified haiku paradox (resolved: discovery at capable tier, pre-assembled context for haiku)
- Methodology skill + design-vet-agent integration planned as follow-on task

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit
- Autofix only handles placement, ordering, and structural entry removal — not orphans

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Headings must include "To" (e.g., "How To Augment Agent Context")
- Index keys must NOT include "to" — validator adds it automatically
- Including "to" in key causes double-to: `"how to to X"`

**Deliverable review delegation loses context — partially addressed:**
- Two-layer model adds mandatory interactive review (Layer 2) that catches cross-project issues
- Layer 1 delegation still available for volume; Layer 2 compensates for context gap

## Next Steps

4 worktrees active. In main: Remaining workflow items (sonnet). worktree-merge-data-loss needs lint fixes before merge.

## Reference Files

- `plans/reports/ground-skill-research-synthesis.md` — Grounding skill research synthesis
- `plans/reports/deliverable-review-prioritize.md` — Prioritize skill deliverable review
- `plans/reports/task-prioritization-methodology.md` — WSJF-adapted prioritization methodology
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/remember-skill-update/outline.md` — Design outline (reviewed, Phase B ready)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/reports/prioritization-2026-02-16.md` — WSJF task prioritization (26 tasks scored)
- `plans/prototypes/requirements.md` — Session extraction feature gap requirements
