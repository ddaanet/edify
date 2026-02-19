# Session Handoff: 2026-02-19

**Status:** Skill optimization applied. Handoff 330→159 lines (52%), commit 237→133 lines (44%), template inlined, consolidation flow extracted.

## Completed This Session

**Skill prose optimization (Segment → Attribute → Compress):**
- Handoff SKILL.md: 330→159 lines (52%). Template inlined, consolidation flow extracted to reference, conditional paths compressed, redundancy with execute-rule.md removed, learnings line count gate removed (→ SessionStart hook), discussion substance check added, tool-call batching (parallel wc + learning-ages)
- Commit SKILL.md: 237→133 lines (44%). Critical Constraints and Context Gathering sections removed (redundant with always-loaded fragments), "separate Bash calls" consolidated from 3→1, one example removed, added `Bash(git diff:*)` to allowed-tools (pre-existing gap found by reviewer)
- New: `references/consolidation-flow.md` (27 lines, extracted from handoff 4c)
- Deleted: `references/template.md` (81 lines, inlined into handoff SKILL.md)
- Parallel opus skill-reviewer reviews: handoff passed (2 fixes applied — D-6 dangling reference, learnings.md added to Reference), commit passed with pre-existing allowed-tools gaps noted (submodule subshells, pbcopy)
- Methodology: `plans/reports/skill-optimization-grounding.md`. Actual reductions exceeded estimates (52%/44% vs 27%/24%) — grounding report was conservative on principles/trim/continuation sections

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-18.md (rev 4) -->

- [ ] **Handoff CLI tool** — Mechanical handoff+commit pipeline in CLI | `/design` | sonnet
  - Same pattern as worktree CLI: mechanical ops in CLI, judgment stays in agent
  - **Inputs:** status line (overwrite), completed text (overwrite committed / append uncommitted), optional files to add/remove, optional commit message with gitmoji
  - **Outputs (conditional):** learnings age status, precommit result, git status+diff (skip if precommit red), worktree ls. Suppress "nothing to report" outputs.
  - **Cache on failure:** Inputs written to state file. On rerun, reads cached inputs — agent doesn't re-enter skill. Fix obstruction, rerun tool until green.
  - **Domain boundaries:** Handoff CLI owns status line + completed section + git ops + checks. Worktree CLI owns `→ slug` markers. Agent Edit owns: pending task mutations (insertion point = judgment), learnings append + invalidation, blockers, reference files.
  - **Learnings flow:** Agent writes learnings (Edit) → reviews combined file for invalidation (semantic anchoring) → then calls CLI. Manual append before invalidation improves conflict detection via spatial proximity.
  - **Gitmoji:** Script using lightweight embeddings + cosine similarity over 78 pre-computed description vectors. Build initial script first (address pain), then validate against git log corpus (exact/acceptable/wrong match rates). Tune or reject based on empirical results.

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule

- [ ] **Script commit vet gate** — Replace prose Gate B with scripted check (file classification + vet report existence) | sonnet
  - Part of commit skill optimization (FR-5 partially landed — Gate A removed, Gate B still prose)
  - Also: remove `vet-requirement.md` from CLAUDE.md `@`-references, move execution context template to memory index

- [ ] **PostToolUse auto-format hook** — PostToolUse hook on Write/Edit running formatter on changed file. Catches lint/format drift before it compounds into multi-round fix cycles | sonnet | restart

- [ ] **Design quality gates** — `/design plans/runbook-quality-gates/` | opus | restart
  - Requirements at `plans/runbook-quality-gates/requirements.md`
  - 3 open questions: script vs agent (Q-1), insertion point (Q-2), mandatory vs opt-in (Q-3)
  - Not blocked on error-handling design (quality gates are pre-execution validation, not execution-time)

- [ ] **Runbook quality gates Phase B** — TDD for validate-runbook.py (4 subcommands) | sonnet
  - Plan: runbook-quality-gates | Status: ready
  - model-tags, lifecycle, test-counts, red-plausibility
  - Graceful degradation bridges gap (NFR-2)

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Merge learnings delta** — Reconcile learnings.md after merge when branch diverged before consolidation | sonnet
  - Plan: merge-learnings-delta | Status: requirements
  - 3 FRs: detect consolidation divergence, reconstruct correct file, handle edge cases
  - Main base + branch delta strategy (not ours, not theirs)

- [ ] **Fix worktree rm dirty check** — Must not fail if parent repo is dirty, only if target worktree is dirty | sonnet

- [ ] **Fix worktree rm on broken worktree** — `git worktree remove --force` returns 255 on empty dir from failed `new` | sonnet
  - `new` with bare slug can leave empty directory (no `.git`, no checkout). `rm` fails because git doesn't recognize it as a worktree. `_git()` swallows stderr, hiding actual error.
  - Fix: detect non-worktree directory in `rm`, fall back to `prune` + `rmdir` + branch delete

- [ ] **Fix worktree rm submodule branch cleanup** — `rm --confirm` deletes parent branch but not agent-core submodule branch | sonnet
  - Leaves stale submodule branches requiring manual `git -C agent-core branch -d <slug>`

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `new "Task Name" --branch <slug>` form solves 29-char slug limit
  - **Scope expansion:** Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: Pre-merge untracked file fix (`new` leaves session.md untracked), Worktree skill adhoc mode (covered by `--branch`)

- [ ] **Pipeline skill updates** — `/design` | opus | restart
  - Orchestrate skill: create `/deliverable-review` pending task at exit (opus, restart)
  - Deliverable-review skill Phase 4: create one pending task for all findings → `/design`; no merge-readiness language
  - Design skill: add Phase 0 requirements-clarity gate (well-specified → triage, underspecified → `/requirements`)
  - Insights input: Diamond TDD definition needed at `/design` (direct execution path), `/runbook` (step generation), `tdd-task` agent (cycle execution)
  - Discussion context in runbook-skill-fixes worktree session

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents task (FR-3), augments Codebase quality sweep (FR-4)

- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main tree from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Planstate `infer_state()` now auto-discovers plans (workwoods merged) — no jobs.md write needed
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)

- [ ] **Test diagnostic helper** — Replace `subprocess.run(..., check=True)` in test setup with stderr surfacing | sonnet

- [ ] **Memory-index auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check

- [ ] **Session.md validator** — Scripted precommit check for session.md format (like validate-memory-index.py) | sonnet
  - Plan: session-validator | Status: requirements
  - 5 FRs: section schema, task format, reference validity, worktree marker cross-ref, status line
  - Prior handoff validation task was dropped (agent review impractical) — this is scripted/mechanical
  - FR-2/FR-4 depend on worktree-cli-default (format finalization); FR-1/FR-3/FR-5 can proceed now

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
  - Specific targets from quality-infrastructure FR-4: `_git_ok`, `_fail` helpers, 13 raw subprocess replacements, 18 SystemExit replacements, custom exception classes

- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Requirements: `plans/remember-skill-update/requirements.md` (9 FRs + FR-10 rename, FR-11 agent routing)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Absorbs: Rename remember skill (FR-10), Remember agent routing (FR-11, deferred until redesign)
  - **New scope:** `/remember` consolidation should validate trigger names before graduating to `/when` entries

- [ ] **Handoff wt awareness** — Only consolidate memory in main repo or dedicated worktree | sonnet

- [ ] **Agent rule injection** — process improvements batch | sonnet
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Handoff insertion policy** — Change "append" to "insert at estimated priority position" in handoff skill | sonnet
  - Evidence: `p:` tasks distribute evenly (n=29), not append-biased. Agents correctly judge position.
  - Scripts: `plans/prototypes/correlate-pending-v2.py`

- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **SessionStart status hook** — Bundled SessionStart hook: (1) dirty tree warning via `git status --porcelain`, (2) learnings line count vs 80-line limit (gate moves from handoff skill), (3) stale worktree detection via last commit age, (4) model tier display via `additionalContext` (absorbs Model tier awareness hook), (5) user tip rotation from tips file. All checks <1s total. `systemMessage` for user-visible, `additionalContext` for model tier | sonnet | restart

- [ ] **Task agent guardrails** — Mechanical bounds for Task agents: tool-call count limits (stop/report if exceeded), test regression detection between steps (GREEN baseline comparison), model escalation trigger on quality gate failure. Per-agent execution bounds, distinct from orchestrator-level error handling. Source: insights friction (haiku committed with 3 failing regressions, agent stuck at 300 tool uses) | sonnet

- [ ] **Cache expiration prototype** — Scrape session debug log (`~/.claude/debug/`) for cache_read/cache_creation token metrics, measure actual TTL empirically. Prototype countdown display for Stop hook. API default 5min, observed ~3min in Claude Code (#14628) | sonnet

- [ ] **Simplify when-resolve CLI** — Accept single argument with when/how prefix instead of two args, update skill prose | sonnet

- [ ] **Explore Anthropic plugins** — Install all 28 official plugins, explore for safety+security relevance | sonnet | restart
  - Repo: `github.com/anthropics/claude-plugins-official`

- [ ] **Behavioral design** — `/design` nuanced conversational pattern intervention | opus
  - Requires synthesis from research on conversational patterns

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Existing: `bin/last-output`, `scripts/scrape-validation.py`, `plans/prototypes/*.py`
  - Requirements: `plans/prototypes/requirements.md` (multi-project scanning, directive extraction, git correlation)

- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart
  - Insights input: headless mode (`claude -p`) as sub-agent delegation path — sub-agents can't spawn Task agents but can invoke headless CLI via Bash, addressing "sub-agents cannot spawn sub-agents" constraint

- [ ] **Fix task-context.sh task list bloat** — Script outputs too much content, needs filtering/trimming | sonnet

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

- [ ] **Diagnostic opus review** — Interactive post-vet RCA methodology | `/requirements` | opus
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject vs index-and-recall

- [ ] **Ground state-machine review criteria** — Research state coverage validation in plan review | opus

- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` frontmatter | sonnet

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design.md complete, vet in progress, planning next (design refreshed Feb 13)
  - Design runbook evolution now complete — blocker lifted
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Blocked on: Error handling design (needs D-3 escalation criteria, D-5 rollback semantics)
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation

- [ ] **Safety review expansion** — Implement pipeline changes from grounding research | opus
  - Input: `plans/reports/safety-review-grounding.md`
  - Depends on: Explore Anthropic plugins

- [ ] **Migrate test suite to diamond** — needs scoping | depends on runbook evolution design
  - Existing 1027 tests, separate design from runbook evolution

- [ ] **Model directive pipeline** — Model guidance flows design → runbook → execution | opus
  - Touches: design skill, outline format, runbook skill, prepare-runbook.py, orchestrate skill, plan-reviewer
  - Absorbs: Runbook model assignment, Fix prepare-runbook.py model override, Fix plan-reviewer model adequacy gap

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files
- Always use `dangerouslyDisableSandbox: true` for any merge operation

**`_update_session_and_amend` exit 128 during rm:**
- `_worktree rm` calls `_update_session_and_amend` which runs `git add agents/session.md` → exit 128
- Root cause unclear — same command succeeds manually. Workaround: manual amend before `rm --confirm`

**`slug` and `--task` mutually exclusive in `_worktree new`:**
- Cannot override slug for long task names while keeping session integration
- Workaround: bare slug + manual session.md editing
- Fix: worktree-cli-default task adds `--branch` flag

**Merge ours resolution loses worktree content:**
- `just wt-merge` uses `checkout --ours` for session.md, learnings.md
- Drops worktree-side changes silently — must verify post-merge
- Learnings.md: merge brings pre-consolidation content when branch diverged before `/remember`. See `plans/merge-learnings-delta/requirements.md`

**`wt rm` blocks on dirty parent repo:**
- `claudeutils _worktree rm` exits 2 if parent has uncommitted changes
- Workaround: `git stash && wt rm && git stash pop`

**`wt rm` leaves stale submodule config:**
- `.git/modules/agent-core/config` `core.worktree` points to deleted directory
- Breaks all `git -C agent-core` operations on main until manually fixed

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Index keys must NOT include "to" — validator adds it automatically
## Next Steps

Handoff CLI tool is next high-priority task. Error-handling worktree still ready to merge.

## Reference Files

- `plans/reports/prioritization-2026-02-18.md` — WSJF task prioritization (rev 4, 43 tasks — stale, pre-consolidation)
- `plans/merge-learnings-delta/requirements.md` — Learnings merge reconciliation (3 FRs, Q-1 consolidation marker)
- `plans/session-validator/requirements.md` — Session.md validator (5 FRs, precommit integration)
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug, Worktree Tasks elimination)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `plans/runbook-quality-gates/design.md` — Quality gates design (6 FRs, simplification agent)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring