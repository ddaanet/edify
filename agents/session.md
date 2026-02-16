# Session Handoff: 2026-02-16

**Status:** Established grounded task prioritization methodology (WSJF-adapted) and grounding skill research synthesis. Two new skills pending creation.

## Completed This Session

**Task prioritization research & methodology:**
- Researched prioritization frameworks: WSJF, RICE, ICE, CD3, Lean Value/Effort, MoSCoW, Eisenhower (6 web searches, 2 web fetches)
- Opus brainstorm produced 13 project-specific evaluation axes (defect compounding, artifact readiness, downstream unblock, knowledge decay, model tier cost, workflow friction, parallelizability, bootstrap risk, decision reversibility, restart amortization, agent reliability, context locality, consolidation pressure)
- Selected WSJF as base framework — CoD decomposed into Workflow Friction + Decay Pressure + Compound Risk Reduction, with project-specific Fibonacci scoring tables
- Scored all 27 pending tasks; top 5: precommit improvements (4.5), vet proportionality (3.8), remember skill update (3.2), RED pass protocol (3.2), review runbook delegation (3.0)
- Report: `plans/reports/task-prioritization-methodology.md`

**Grounding skill research & design:**
- Researched: Double Diamond (Design Council 2005), Rapid Review (evidence synthesis), RAG-as-grounding (LLM hallucination mitigation)
- Synthesized 4-phase procedure: Scope → Diverge (parallel internal + external) → Converge → Output
- Grounding quality labels (Strong/Moderate/Thin/None) from Rapid Review's rigor/speed tradeoff acknowledgment
- Report: `plans/reports/ground-skill-research-synthesis.md`

**Design discussions:**
- Both methodologies should be skills (not decision documents) for plugin portability
- Grounding skill should itself be grounded (meta-recursive — applied its own methodology)
- Research deliverables belong in plans/reports/, not tmp/

## Pending Tasks

- [ ] **Prioritization skill** — Create plugin skill for WSJF-adapted backlog scoring | sonnet
  - Research: `plans/reports/task-prioritization-methodology.md` (WSJF adapted with project-specific CoD decomposition)
  - Methodology: Workflow Friction + Decay Pressure + Compound Risk Reduction / Job Size
  - Scheduling modifiers: model tier cohort, restart batching, self-referential flag, parallelizability
  - Skill output: priority-ordered table + parallel batches

- [ ] **Grounding skill** — Create plugin skill for research-anchored methodology synthesis | sonnet
  - Research: `plans/reports/ground-skill-research-synthesis.md` (Double Diamond + Rapid Review + RAG grounding)
  - Pattern: Scope → Diverge (parallel internal brainstorm/explore + external web research) → Converge → Output
  - Parameterized: internal branch type (brainstorm/explore), model tier, research breadth, output format
  - Grounding quality label: Strong/Moderate/Thin/None attached to output

- [ ] **Remember skill update** — Resume `/design` Phase B | sonnet
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Learnings consolidation done (491→32 lines) — FR-7 migration partially addressed via consolidation

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Pushback design** — `/design plans/pushback/requirements.md` | opus

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Precommit improvements** — Expand precommit checks | sonnet
  - Validate session.md references point to versioned files (reject tmp/ references) — recurring failure mode
  - Validate session.md pending tasks/worktree structure
  - Reject references to tmp/ files in all committed content
  - Autofix or fail on duplicate memory index entries (blocked on memory redesign)

- [ ] **Handoff wt awareness** — Only consolidate memory in main repo or dedicated worktree | sonnet

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 18 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` frontmatter | sonnet

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet

- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: requirements

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Remember agent routing** — blocked on memory redesign
  - When consolidating learnings actionable for sub-agents, route to agent templates (quiet-task.md, tdd-task.md) as additional target

- [ ] **Agent rule injection** — process improvements batch
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Behavioral design** — `/design` nuanced conversational pattern intervention | opus
  - Requires synthesis from research on conversational patterns

- [ ] **Diagnostic opus review** — Interactive post-vet RCA methodology | `/requirements` | opus
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject vs index-and-recall
  - Methodology as skill referenced in design-vet-agent + outline-review-agent `skills:` frontmatter

- [ ] **Review runbook delegation** — Update validation language to match orchestrator responsibility | sonnet
  - Step validation sections say "Delegate to skill-reviewer" but execution agents can't spawn plugin-dev agents
  - Fix: validation delegation is orchestrator responsibility, not execution agent

- [ ] **Remaining workflow items** — Sub-items not captured in workflow-rca-fixes | sonnet
  - Orchestrate evolution — designed, ready for `/runbook` (design refreshed Feb 13)
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work (no mechanism exists)
  - Agent output optimization — remove summarize/report language from agents
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit

- [ ] **Memory-index auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Vet proportionality** — Trivial edits shouldn't require full vet-fix-agent delegation | sonnet
  - 1-line bullet addition to runbook skill triggered full vet agent
  - Needs: proportionality threshold in vet-requirement.md fragment
  - Also review Gate B in commit skill — same over-application pattern

- [ ] **Pretool hook cd pattern** — Allow `cd <path> &&` pattern, check security implications | sonnet | restart
  - Load plugin-dev:hook-development skill for hook modification guidance
  - Current hook blocks ALL bash when cwd wrong, including `cd` to restore — creates catch-22

- [ ] **Error handling design** — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

## Blockers / Gotchas

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

## Next Steps

Prioritization skill: Create skill using `plans/reports/task-prioritization-methodology.md` as reference, following plugin-dev:skill-development process.

## Reference Files

- `plans/reports/task-prioritization-methodology.md` — WSJF-adapted prioritization methodology
- `plans/reports/ground-skill-research-synthesis.md` — Grounding skill research synthesis (Double Diamond + Rapid Review + RAG)
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/remember-skill-update/outline.md` — Design outline (reviewed, Phase B ready)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `plans/error-handling/reports/explore-error-handling.md` — Error handling landscape
- `plans/error-handling/reports/explore-cps-chains.md` — CPS chain mechanics
- `plans/reports/memory-index-actionability-review.md` — Opus actionability review of all index entries
- `plans/when-recall/reports/baseline-recall-analysis.md` — 2.9% baseline recall measurement
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
