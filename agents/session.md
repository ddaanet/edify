# Session Handoff: 2026-02-17

**Status:** Quality gates Phase B outline complete (13 TDD cycles). Phase A fully done. 3 worktrees active.

## Completed This Session

**Runbook quality gates — Phase B planning (through Phase 0.86):**
- Confirmed Phase A fully complete (all 6 architectural artifacts in worktree): simplification agent, SKILL.md Phase 0.86 + 3.5, review-plan Section 12, plan-reviewer model assignment, pipeline-contracts T2.5/T4.5, memory-index entries
- Tier assessment: Tier 3 (14 TDD cycles, 4 subcommands, cross-cycle fixture dependencies)
- Phase 0.5: Codebase discovery — prepare-runbook.py importable (line 985 `__main__` guard), D-7 resolved (importlib approach)
- Phase 0.75: Generated `runbook-outline.md` — 5 phases, 14 cycles
- Outline review (opus): 7 issues fixed (3 major: missing `extract_step_metadata`, fixture strategy contradiction, FR-6 mapping gap; 4 minor: missing `--skip-model-tags`, dependencies, hardcoded count, duplicate guidance)
- Phase 0.85: Phase 5 has external dependencies → skip consolidation
- Phase 0.86: Simplification agent merged Phase 5 cycles 5.1+5.2 → single 5.1 (14→13 cycles)
- Stopped before Phase 0.9 (complexity check)

**Runbook model assignment:** Complete — Phase A edits to SKILL.md, review-plan, plan-reviewer, pipeline-contracts, memory-index all landed opus requirements for architectural artifacts

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-16.md (rev 2) -->

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Blocked on: Error handling design (needs D-3 escalation criteria, D-5 rollback semantics)
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

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

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design.md complete, vet in progress, planning next (design refreshed Feb 13)

- [ ] **Simplify when-resolve CLI** — Accept single argument with when/how prefix instead of two args, update skill prose | sonnet

- [ ] **Debug failed merge** — Investigate the original merge failure (exit 128 during session.md conflict resolution) | sonnet
  - Context: Merge of `remaining-workflow-items` worktree on 2026-02-16
  - Branch had 1 post-merge commit (683fc7d), conflicts on `agent-core` submodule + `agents/session.md`
  - Main at 9bb45d0, merge result at 5e024c2
  - `git add agents/session.md` returned exit 128 during `_resolve_session_md_conflict` in `_phase3_merge_parent`
  - Now that error handling is fixed, we can reproduce and see the actual git error message

- [x] **Runbook model assignment** — apply design-decisions.md directive (opus for skill/fragment/agent edits)
  - Landed via Phase A edits in runbook-skill-fixes worktree
- [ ] **Runbook quality gates Phase B** — Resume `/runbook` Phase 0.9+ then expand and assemble | sonnet
  - Outline complete (13 cycles, 5 phases), reviewed, simplified
  - Next: Phase 0.9 (complexity check) → 0.95 (sufficiency check) → Phase 1 (expansion) → Phase 2-4
  - Reports: `plans/runbook-quality-gates/reports/runbook-outline-review.md`, `simplification-report.md`
  - model-tags, lifecycle, test-counts, red-plausibility

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

- [ ] **Design workwoods** → `design-workwoods` — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: designed (runbook planned, 33 TDD + 10 general steps)

- [ ] **Runbook skill fixes** → `runbook-skill-fixes` — Quality gates Phase B: resume `/runbook` expansion | sonnet
  - Model assignment: complete (Phase A landed all directives)
  - Quality gates Phase B: outline done (13 TDD cycles), resume at Phase 0.9
  - Next: `/runbook plans/runbook-quality-gates/design.md` — continue from Phase 0.9 (complexity check)

## Blockers / Gotchas

**Transient git index.lock during merge:**
- `claudeutils _worktree merge` hits `index.lock` race condition during multi-step git operations
- Likely caused by file watcher (IDE/direnv) touching the index concurrently
- Workaround: retry after brief pause, or complete merge manually after partial success

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

Next in this worktree: Resume `/runbook` Phase 0.9+ for quality gates Phase B (continue expansion of `plans/runbook-quality-gates/runbook-outline.md`). On main: Execute plugin migration (opus) or Script commit vet gate (sonnet). 3 worktrees active. Learnings at 122/80 lines — run `/remember` soon.

## Reference Files

- `plans/reports/prioritization-2026-02-16.md` — WSJF task prioritization (rev 2, 27 tasks)
- `plans/worktree-merge-data-loss/reports/deliverable-review.md` — Consolidated review (all 3 major findings resolved)
- `plans/reports/task-prioritization-methodology.md` — WSJF-adapted prioritization methodology
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/reports/safety-review-grounding.md` — Safety review grounding research
- `plans/runbook-quality-gates/design.md` — Quality gates design (6 FRs, simplification agent)
- `plans/runbook-quality-gates/runbook-outline.md` — Phase B outline (13 TDD cycles, 5 phases, reviewed+simplified)
- `plans/runbook-quality-gates/reports/runbook-outline-review.md` — Outline review (7 issues, all FIXED)
- `plans/runbook-quality-gates/reports/simplification-report.md` — Simplification (14→13 cycles)
