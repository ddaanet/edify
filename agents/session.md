# Session Handoff: 2026-02-15

**Status:** Skill-loading fix committed. Workflow improvements task triaged.

## Completed This Session

**Skill-loading directive fix (committed: 3c81326):**
- Runbook Phase 0.5 now consumes "Skill-loading directives" from design Documentation Perimeter
- Root cause: planner read directive text but had no instruction to invoke listed skills
- Fix: 1-line addition to `agent-core/skills/runbook/SKILL.md`

**Workflow improvements currency review:**
- Assessed all 8 sub-items against current codebase state
- Dropped 2: fragments cleanup (superseded — no duplication found), investigation prerequisite rule (complete)
- Report: `tmp/workflow-improvements-currency.md`

## Pending Tasks

- [ ] **Diagnostic opus review methodology** — New task from design discussion | `/requirements` | opus
  - Interactive post-vet RCA using domain-specific methodology + iterative deepening
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Needs: review methodology documents (design-review, agent-review), integration into workflow
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
  - Design review methodology conversation: `tmp/design-review-methodology-synthesis.md`, `tmp/design-review-methodology-critique.md`
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject (skills prolog) vs index-and-recall (on-demand). Haiku paradox resolved: discovery stays with capable agents, haiku gets pre-assembled context
  - Methodology as skill referenced in design-vet-agent + outline-review-agent `skills:` frontmatter
- [ ] **Review runbook skill delegation language** — Validation steps delegate to skill-reviewer/vet but orchestrator does delegation, not execution agent | sonnet
  - Context: Step validation sections say "Delegate to skill-reviewer" but execution agents can't spawn plugin-dev agents
  - Pattern used: orchestrator handled reviews from main session after agents committed
  - Fix: Update validation language to match orchestrator responsibility
- [ ] **Workflow improvements** — Remaining sub-items not captured in workflow-rca-fixes | sonnet
  - Orchestrate evolution — designed, ready for `/runbook` (design refreshed Feb 13)
  - Reflect skill output — RCA should produce pending tasks, not inline fixes (3 exit paths exist, inline still default)
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work (no mechanism exists)
  - Agent output optimization — remove summarize/report language from agents (scope unclear)
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit (needs clarification)
- [ ] **Memory-index skill auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Context: Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check
  - Prevents sub-agent discovery gaps when canonical index grows
- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule
  - Override flag for precommit skip
  - Combined status output after commit
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)
  - Separate requirements artifact needed
- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [ ] **Learning ages computation after consolidation** — Verify age calculation correct when learnings consolidated/rewritten | sonnet
- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart
- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
- [ ] **Update vet requirement proportionality** — Trivial edits to existing artifacts shouldn't require full vet-fix-agent delegation | sonnet
  - Context: 1-line bullet addition to runbook skill triggered full vet agent, user flagged as pointless
  - Needs: proportionality threshold in vet-requirement.md fragment (e.g., trivial edits exempt)
  - Also review Gate B in commit skill — same over-application pattern
- [ ] **Upstream plugin-dev: document skills frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

## Worktree Tasks

- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
- [ ] **Workflow improvements** → `workflow-improvements` — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
- [ ] **Worktree fixes** → `worktree-fixes` — `/design plans/worktree-fixes/` | opus

## Blockers / Gotchas

**Execution feedback gap connects to error-handling:**
- FR-17 documents requirement, implementation in `wt/error-handling`
- RCA data (when-recall test plan redesign incident) provides grounding for error-handling design
- All 5 RCAs provide grounding material for error classification taxonomy

**Diagnostic review methodology converging:**
- Taxonomy, iteration protocol, priming template designed in conversation
- Opus critique validated approach, identified haiku paradox (resolved: discovery at capable tier, pre-assembled context for haiku)
- Methodology skill + design-vet-agent integration planned as follow-on task
- Synthesis and critique in tmp/ (ephemeral — capture in requirements before cleanup)

## Next Steps

Review pending tasks list for next work item.

---
*Handoff by Sonnet.*
