# Session Handoff: 2026-02-15

**Status:** Workflow RCA fixes complete — orchestration + deliverable review + fixes applied.

## Completed This Session

**Deliverable review (workflow-rca-fixes):**
- Three parallel opus review agents: agent definitions, skill definitions, human documentation
- Found 2 Critical, 8 Major, 14 Minor across 21 deliverables (5,748 lines)
- Fixed 2C, 7M, 7m directly; 1M deferred (memory-index sync mechanism); 6m accepted
- Critical fixes: non-existent `runbook-review-agent` → `plan-reviewer` in workflows-terminology.md; memory-index skill synced with canonical (3 entries missing, ordering fixed)
- Major fixes: FR-18 added to outline-review-agent + plan-reviewer; general-patterns.md references added to runbook skill; agent-name validation expanded; vet enforcement Constraints field; orchestration-execution refactor agent path
- Reports: `plans/workflow-rca-fixes/reports/deliverable-review*.md` (4 reports)
- 11 files edited across agent-core/ and agents/decisions/

## Pending Tasks

- [ ] **RCA failures to load skills during /runbook** — Investigate why plugin-dev skills required explicit invocation | sonnet
  - Context: /runbook skill documentation perimeter says "Load plugin-dev:skill-development before planning"
  - Expected: Auto-load or clearer failure message when missing
  - Actual: User had to manually invoke skills before runbook promotion could proceed
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
  - Orchestrate evolution — designed, stale Feb 10, refresh after RCA
  - Fragments cleanup — remove fragments duplicating skills/workflow
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work
  - Agent output optimization — remove summarize/report language from agents
  - Investigation prerequisite rule review
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit
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

Review pending tasks list for next work item. Workflow RCA fixes plan is fully complete (orchestrated + deliverable-reviewed + fixed).

---
*Handoff by Sonnet. Deliverable review complete: 2C/7M/7m fixed across 11 files.*
