# Session Handoff: 2026-02-16

**Status:** Deliverable review completed for prioritize skill, all minor fixes applied.

## Completed This Session

**Deliverable review — prioritize skill:**
- Inventoried 3 artifacts (441 lines): SKILL.md (127), scoring-tables.md (150), methodology.md (164)
- Single-agent review (< 500 line threshold): universal + agentic prose + human docs axes
- Report: `plans/reports/deliverable-review-prioritize.md`
- Assessment: No critical/major issues, 4 minor fixes applied:
  - Fibonacci bound `(1,2,3,5,8,13)` → `(1,2,3,5,8)` in methodology.md
  - Added CRC cap rationale to methodology.md Context Recovery Cost section
  - Added `(from project root)` to git evidence source in scoring-tables.md
  - Replaced non-executable `diff <(...)` with prose description in methodology.md

## Pending Tasks

- [ ] **Design skill outline gate** — Update /design skill to add direct execution gate after outline validated | sonnet
  - When outline has sufficient specificity, skip Phase C (design generation) and implement directly
  - Discovered during ground skill: outline was the design

- [ ] **Outline agent Write perm** — Add Write permission to outline-review-agent, update design skill to specify report path | sonnet | restart
  - Prototype use case for third-party agents is separate (plans/reports/prototype-review-capture-script.md)

- [ ] **Handoff memory naming** — Add trigger naming guidance to handoff skill's learning-writing section | sonnet
  - Principle: triggers match activity at decision point, broadest verb, no self-assessment terms
  - Same principle as `/when choosing name`: discovery and recall over precision

- [ ] **Remember skill update** — Resume `/design` Phase B | sonnet
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Learnings consolidation done (491→32 lines) — FR-7 migration partially addressed via consolidation
  - **New scope:** `/remember` consolidation should validate trigger names before graduating to `/when` entries

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
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

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

- [ ] **Vet delegation routing** — Route review to artifact-appropriate agent (vet-fix for code, skill-reviewer for skills, agent-creator for agents) | sonnet
  - General rule affecting vet-requirement.md and /runbook review delegation
  - agent-creator: Write+Read, confirmed cooperative in review mode (decisions/project-config.md:266)
  - skill-reviewer: Read/Grep/Glob only — cannot autofix, would need tool additions
  - No hook reviewer exists; no doc reviewer exists (readme skill is creation, not review)
  - Precedent: agent-creator repurposed for review via prompting (`/when agent-creator reviews agents`)

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

Remember skill update: Resume `/design` Phase B with outline discussion. New scope addition: trigger name validation during consolidation.

## Reference Files

- `plans/reports/deliverable-review-prioritize.md` — Prioritize skill deliverable review (4 minor, all fixed)
- `plans/reports/task-prioritization-methodology.md` — WSJF-adapted prioritization methodology
- `plans/reports/ground-skill-research-synthesis.md` — Grounding skill research synthesis (Double Diamond + Rapid Review + RAG)
- `plans/reports/prototype-review-capture-script.md` — Sub-agent output capture prototype (third-party agents)
- `plans/grounding-skill/outline.md` — Ground skill design outline (8 decisions)
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/remember-skill-update/outline.md` — Design outline (reviewed, Phase B ready)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `plans/error-handling/reports/explore-error-handling.md` — Error handling landscape
- `plans/error-handling/reports/explore-cps-chains.md` — CPS chain mechanics
- `plans/reports/memory-index-actionability-review.md` — Opus actionability review of all index entries
- `plans/when-recall/reports/baseline-recall-analysis.md` — 2.9% baseline recall measurement
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
