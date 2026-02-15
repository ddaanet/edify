# Session Handoff: 2026-02-15

**Status:** workflow-improvements worktree merged to main.

## Completed This Session

**Merged workflow-improvements worktree:**
- `_worktree merge` only merged submodule (known bug) — manual parent merge required
- Cleaned untracked file debris from partial merge attempts (sandbox + `.claude/` writes)
- Resolved 4 session file conflicts: jobs.md, learnings.md, memory-index.md, session.md
- Fixed 4 orphan memory-index entries (3 structural heading removals, 1 stale key update)
- Integrated 7 new pending tasks and 17 new learnings from worktree
- Added workflow-rca-fixes as complete in jobs.md (20 FRs, 6 phases, 16 steps)
- Removed "Blocked on: workflow improvements" from error-handling worktree task
- 884 tests passing, precommit OK

## Pending Tasks

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

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

## Worktree Tasks

- [ ] **Remember skill update** → `remember-skill-update` — Resume `/design` Phase B | sonnet
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Immediate sub-task: Migrate 64 learning titles to When/How format (FR-7)
- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
  - Outline: `plans/error-handling/outline.md`
- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus

## Blockers / Gotchas

**Execution feedback gap connects to error-handling:**
- FR-17 documents requirement, implementation in `wt/error-handling`
- RCA data (when-recall test plan redesign incident) provides grounding for error-handling design
- All 5 RCAs provide grounding material for error classification taxonomy

**Diagnostic review methodology converging:**
- Taxonomy, iteration protocol, priming template designed in conversation
- Opus critique validated approach, identified haiku paradox (resolved: discovery at capable tier, pre-assembled context for haiku)
- Methodology skill + design-vet-agent integration planned as follow-on task

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit
- Autofix only handles placement, ordering, and structural entry removal — not orphans

**Rule file directive adherence unreliable:**
- Agents ignore injected "load X before modifying" directives
- Same failure mode as passive index (2.9% baseline recall)
- Blocking hooks or inline code comments may be more effective than suggestion-based rules

**Learnings.md bloated after pushback merge (400 lines, 69 entries):**
- Pushback worktree accumulated 62 entries over its lifecycle
- Merge unioned both files — all worktree entries show 0 days (merge commit date)
- Cannot consolidate: 0 entries ≥7 active days despite 5x soft limit
- Many entries may already be consolidated in pushback's permanent docs — need manual review
- Title migration to When/How format (FR-7) should happen before or alongside consolidation

**Pushback S3 agreement momentum:**
- Known limitation — prompt-level self-monitoring can't detect agreement momentum without persistent state across turns
- Not pursuing further (arXiv 2509.21305 confirms sycophancy is mechanistically distinct)

## Next Steps

Review pending tasks list for next work item.

## Reference Files

- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/remember-skill-update/outline.md` — Design outline (reviewed, Phase B ready)
- `plans/remember-skill-update/reports/explore-remember-skill.md` — Full pipeline exploration
- `plans/reports/memory-index-actionability-review.md` — Opus actionability review of all index entries
- `plans/when-recall/reports/baseline-recall-analysis.md` — 2.9% baseline recall measurement
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/workflow-rca-fixes/design.md` — 20 FRs, 6 phases (complete)
