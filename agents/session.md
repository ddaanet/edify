# Session Handoff: 2026-02-17

**Status:** Worktree infrastructure fixes + rm safety requirements captured. 4 worktrees active.

## Completed This Session

**Fix stale agent-core submodule after worktree removal:**
- `wt rm runbook-skill-fixes` left `.git/modules/agent-core/config` `core.worktree` pointing to removed directory — broke all `git -C agent-core` commands
- Fix: manually edited config to `../../../agent-core`, merged orphaned agent-core branch (3 files with real diffs: claude-config-layout.md, submodule-safety.py, worktree/SKILL.md)
- Root cause: `wt rm` removes worktree directory but doesn't restore submodule config when the worktree held the submodule's main worktree reference

**Cross-tree sandbox access for worktrees:**
- `_worktree new` now adds main repo to worktree's `permissions.additionalDirectories` (cli.py + justfile)
- Enables worktree agents to write to main's tree (requirements transport, cross-tree operations)
- Test updated: `test_new_sandbox_registration` asserts main repo path in worktree sandbox dirs

**Worktree RM safety gate requirements:**
- Captured 5 FRs in `plans/worktree-rm-safety/requirements.md`
- FR-1/2: detect uncommitted changes in parent + submodule; FR-3: exit 2 convention; FR-4: --force bypass; FR-5: skill layer confirmation
- Created worktree `worktree-rm-safety-gate` for implementation

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

- [ ] **Runbook model assignment** — apply design-decisions.md directive (opus for skill/fragment/agent edits)
  - Partially landed via remaining-workflow-items merge
- [ ] **Runbook quality gates Phase B** — TDD for validate-runbook.py (4 subcommands) | sonnet
  - Depends on Phase A merge (SKILL.md references script)
  - Graceful degradation bridges gap (NFR-2)
  - model-tags, lifecycle, test-counts, red-plausibility

- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main tree from worktree | sonnet
  - Sandbox access landed (main repo in worktree's additionalDirectories)
  - Remaining: requirements skill path flag/auto-detection, main path resolution via `git worktree list`
  - Workwoods impact: planstate `infer_state()` will auto-discover plans — no jobs.md write needed post-workwoods
  - Pre-workwoods: write requirements.md + append jobs.md line (interim)

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

- [ ] **Design workwoods** → `design-workwoods` — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: designed (runbook planned, 33 TDD + 10 general steps)

- [ ] **Runbook skill fixes** → `runbook-skill-fixes` — Batch: model assignment, design quality gates | opus
  - Runbook model assignment: apply design-decisions.md directive (opus for skill/fragment/agent edits) — partially landed
  - Design quality gates: `/design plans/runbook-quality-gates/` | restart
    - Requirements at `plans/runbook-quality-gates/requirements.md`

- [ ] **Worktree RM safety gate** → `worktree-rm-safety-gate` — `/design plans/worktree-rm-safety/` | sonnet
  - Plan: worktree-rm-safety | Status: requirements
  - 5 FRs: dirty check (parent+submodule), exit 2, --force bypass, skill confirmation

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

**`wt rm` leaves stale submodule config:**
- Removing a worktree can leave `.git/modules/agent-core/config` `core.worktree` pointing to the deleted directory
- Breaks all `git -C agent-core` operations on main until manually fixed
- Related to worktree-rm-safety work — rm needs submodule awareness

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Headings must include "To" (e.g., "How To Augment Agent Context")
- Index keys must NOT include "to" — validator adds it automatically

## Next Steps

Next: Execute plugin migration (opus) or Script commit vet gate (sonnet). 4 worktrees active (error-handling-design, design-workwoods, runbook-skill-fixes, worktree-rm-safety-gate). Learnings at 128/80 lines — run `/remember` soon.

## Reference Files

- `plans/reports/prioritization-2026-02-16.md` — WSJF task prioritization (rev 2, 27 tasks)
- `plans/worktree-merge-data-loss/reports/deliverable-review.md` — Consolidated review (all 3 major findings resolved)
- `plans/reports/task-prioritization-methodology.md` — WSJF-adapted prioritization methodology
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/reports/safety-review-grounding.md` — Safety review grounding research
- `plans/runbook-quality-gates/design.md` — Quality gates design (6 FRs, simplification agent)