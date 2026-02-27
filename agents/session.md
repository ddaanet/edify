# Session Handoff: 2026-02-26

**Status:** Worktree merges consolidated; post-merge validation permanent gotcha; diff baseline rule; stale hook cleanup; 3 worktrees ready to create.

## Completed This Session

- **Merged python3-redirect-hook** — hook command shortening (drop python3/bash prefix, drop $CLAUDE_PROJECT_DIR), permissionDecision:deny migration, hook output audit learnings (3 new entries)
- **Merged session-scraping-prototype** — complexity routing grounding (6 frameworks → 8 principles → 7 fix points applied), execution-strategy.md decision file, session scraper prototype, 6 new learnings
- **Post-merge validation** — both merges verified: no session.md task loss, no learnings.md entry loss
- **Diff baseline rule** — ambient directive in worktree skill: use three-dot diff (`main...branch`) for merge analysis, not two-dot
- **Permanent post-merge gotcha** — session.md gotcha rewritten: validate session.md AND learnings.md after every merge, 3 known failure modes documented
- **Stale hook cleanup** — removed `tmp/test-hook-channels.py` entry from settings.json (leftover from hook output audit, produced empty user-directed message)
- **Process-critical triage** — identified 8 process-critical tasks; handoff wt awareness superseded; tool deviation hook scope redefined; merge learnings delta reevaluated
- **New task: Design grounding update** — `/ground` with session scraper exploration input

## Pending Tasks

- [ ] **Tool deviation hook** — PostToolUse hook: agents declare expected Bash outcome, hook validates actual vs declared | sonnet
  - General framework: agent declares expected exit code + output pattern before Bash call
  - PostToolUse hook compares actual result, stops or redirects to diagnose-and-compensate on mismatch
  - Broader than original scope (was: just when-resolve.py failures)

- [ ] **Compensate-continue skill** — `/ground` then `/design` | opus
  - Activated after unexpected stop. Records compensation strategy. Applies trivial workarounds inline (e.g., rename heading to route around parser bug). Creates pending task for proper fix. Resumes interrupted work via continuation-prepend.
  - Needs grounding on failure recovery patterns, compensation strategies

- [ ] **Ground workflow skills** — `/ground` each per audit | opus
  - Audit: `plans/reports/workflow-grounding-audit.md`
  - Priority: /runbook → review agents (corrector + design-corrector batch) → /orchestrate → /handoff
  - /design completed — grounded and redesigned
  - Skip low-benefit: /commit, artisan, test-driver, /shelve

- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [ ] **Diagnose compression loss** — RCA against commit `0418cedb` | sonnet
- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Cross-tree requirements** — `/requirements` skill writes to main from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)
- [–] **Handoff wt awareness** — superseded; /codify is now manual
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: orchestrate-evolution
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite
- [ ] **Test diamond migration** — Needs scoping | depends on runbook evolution (delivered)
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Ground state coverage** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Cache expiration** — Debug log token metrics, measure TTL | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **TDD test optimization** — Selective test rerun via dependency analysis | sonnet
- [ ] **Fix task-context bloat** — Filter/trim output | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [!] **Session CLI tool** — `/runbook plans/handoff-cli-tool/outline.md` | sonnet
  - Plan: handoff-cli-tool | Status: designed (outline reviewed 6 rounds, ready for runbook)
  - `_session` group (handoff, status, commit)
  - Discussion conclusions baked into outline: amend, git passthrough, deviation-only output, submodule labeling
- [ ] **UserPromptSubmit topic** — Phase 7 analysis recommends this as highest-impact recall improvement | sonnet
  - Seed keyword table from 200+ memory-index triggers
  - Inject matching decision content via additionalContext on prompt submit
  - Complementary to recall pass (cheap first layer vs deep pipeline integration)
- [ ] **Prioritize script** — Automate mechanical parts of prioritization scoring | sonnet
- [ ] **Task classification** — `/runbook plans/task-classification/outline.md` | sonnet
  - Plan: task-classification | Status: designed (outline reviewed, ready for runbook)
  - `/prime` skill (ad-hoc plan context) + two-section task list (In-tree / Worktree Tasks)
  - Scope: `session.py`, `resolve.py`, `aggregation.py`, `session_structure.py`, handoff skill, execute-rule.md
- [ ] **Recall CLI integration** — Production `claudeutils _recall` CLI (check/resolve/diff), Click, TDD | sonnet
  - Prototype delivered via recall-tool-anchoring worktree
- [ ] **Prose gate terminology** — Find proper name for D+B pattern, ground, update docs | opus
- [ ] **Recall tool consolidation** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet
- [ ] **Orchestrate evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
  - 14 steps: 12 TDD cycles (sonnet) + 2 general steps (opus)
  - Phase 1: agent caching model (4 cycles)
  - Phase 2: orchestrator plan format + verify-step.sh (4 cycles)
  - Phase 3: TDD agent generation + verify-red.sh (4 cycles)
  - Phase 4: SKILL.md rewrite + refactor.md/delegation.md updates (2 steps, opus)
  - Checkpoints: light at phase boundaries, full at Phase 4 (final)
- [ ] **Markdown migration** — `/design` | opus
  - Wrap existing markdown parser with Claude-specific lenient normalization
  - Line-wrap all files, replace ad-hoc regex parsers (prepare-runbook, session merge, validate-runbook, markdown cleanup)
  - Token counting API + sqlite user cache, threshold migration (line counts → tokens)
  - `just setup` sandbox config for cache dir
  - Parsing fixes batch delivered — parser can now replace regex code
- [ ] **Review auto-commit** — after fixing all issues in deliverable-review, auto handoff and commit | sonnet
- [ ] **Worktree fuzzy matching** — `_worktree new` accepts approximate task names instead of exact match | sonnet
- [ ] **Stale recall artifact** — diagnose /design producing old-style recall artifact instead of memory key list | sonnet
- [ ] **Skill disclosure** — `/design plans/skill-progressive-disclosure/brief.md` | opus
  - Plan: skill-progressive-disclosure | Status: requirements
  - Segment loading at gate boundaries: initial load → write-outline → write-design (/design); tier assessment → tier3-planning → expansion (/runbook)
  - Complementary with skills-quality-pass FR-3 extractions
- [ ] **Runbook outline review** — update runbook skill: user review gate after outline correction, iterative fix cycle until approved | sonnet
- [ ] **Runbook recall expansion** — `/design plans/runbook-recall-expansion/requirements.md` | sonnet
  - Plan: runbook-recall-expansion | Status: requirements
  - prepare-runbook.py recall injection, corrector.md self-loading, two-pattern docs (7 FRs)
- [ ] **Recall pipeline** — `d:` when-resolve.py stdin/recall-artifact support, session log dedup | opus
  - Accept recall keys on stdin (ignore post-"|" memory-index format), change recall-artifact format (dash separator unsafe)
  - Session log scraping to auto-eliminate already-recalled entries
- [ ] **Recall learnings design** — `d:` whether learnings.md entries should be resolvable via when-resolve.py | opus
  - Implies memory-index format changes (new source type), resolver changes — genuine design uncertainty
- [ ] **Generate memory index** — `/design` | opus
  - Each decision/learning declares keywords for index. Index generated from declarations. Diff displayed after update for agent review. Supersedes manual append workflow in `/codify` step 4a.
- [ ] **Skill prompt-composer** — migrate skill authoring to use prompt-composer pattern | sonnet

- [ ] **Session scraping** — `/design plans/session-scraping/requirements.md` | sonnet
  - Requirements captured, ready for design
  - Key decisions: all ~/.claude/projects/ (not just claudeutils), agent files are first-class sources, many-to-many session↔commit, tool I/O noise by default

- [ ] **Agentic prose terminology** — replace "LLM prose"/"LLM-consumed prose" variants across codebase | sonnet
  - Search: "llm prose", "llm-prose", "LLM-prose", "LLM-consumed prose", "LLM generated prose" (with/without hyphens)
  - Replace with "agentic prose" / "agentic-prose" as appropriate per context
- [ ] **Recall deduplication** — integrate session context scraping into `when-resolve.py` to filter already-loaded entries | sonnet
  - Session scraper prototype: `plans/prototypes/session-scraper.py`
  - Dedup should be opt-in (`--new-only` flag or `null` mode), not default — explicit queries may resolve for sub-agent prompts
- [ ] **Tier threshold grounding** — calibrate Tier 1/2/3 file-count thresholds against empirical data | opus
  - Thresholds (<6, 6-15, >15) are ungrounded operational parameters
  - Needs measurement from execution history, not confabulated heuristics
- [ ] **when-resolve null mode** — add no-op `null` argument to `when-resolve.py` for gate anchoring | sonnet
  - Equalizes tool call cost between positive/negative recall paths
  - Prevents fast-pathing past recall gates
  - Referenced by `/design` A.2.5 post-explore recall gate

- [x] **Merge learnings delta** — `x` | sonnet

- [ ] **Artifact staleness gate** — sonnet
  - Mechanical checkpoint at /requirements, /design, /runbook exit points
  - `when-resolve.py` touches sentinel; skill compares sentinel mtime to recall-artifact.md AND primary skill artifact (requirements.md, outline.md, design.md, runbook.md)
  - If recall newer than either artifact, trigger update step
  - Two drift vectors: stale recall-artifact (entries loaded not persisted) and stale skill artifacts (decisions loaded after artifact written)
- [ ] **Codify learnings** — `/codify` | sonnet
  - learnings.md at ~125 lines, soft limit 80
- [x] **Create inline skill** — `x` | opus
  - Plan: inline-execute
  - Deliverables: `agent-core/skills/inline/SKILL.md`, `agent-core/skills/inline/references/corrector-template.md`
  - Corrector + skill-reviewer both dispatched; all in-scope issues fixed
  - Review: `plans/inline-execute/reports/review-skill.md`
- [x] **Design skill integration** — `x` | opus
  - Plan: inline-execute
  - FR-1 + FR-9 applied, corrector clean (1 major fixed). Review: `plans/inline-execute/reports/review-design-integration.md`
- [ ] **Entry gate propagation** — `/design` | opus
  - Add git-clean + precommit entry gates to /orchestrate, /deliverable-review, corrector agent
  - Cross-cutting pattern — needs /design to resolve: each skill body vs shared fragment vs hook, and per-consumer questions (corrector double-gating, orchestrate checkpoint overlap, deliverable-review session context)
  - Follow-on after /inline delivery
- [x] **Execution feedback** — sonnet
  - Corrector fixes all applied (2 critical, 1 major, 2 minor — FIXED by corrector)
  - All 6 issues classified: 4 inline skill design (delegation protocol), 1 tooling (when-resolve.py stdin — existing task), 1 resolved
  - Reclassified hook false positive: prompt discipline (no template placeholders), not hook matching bug
  - Design refinements: entry gate, delegation protocol, D-4 fix, Tier 2 absorption, no mid-execution checkpoints
  - FR-10 expanded: Tier 1 + Tier 2 → /inline. /runbook becomes planning-only for Tiers 1-2.
  - New pending: entry gate propagation
- [ ] **Fix inline-exec findings** — `/design plans/inline-execute/reports/deliverable-review.md` | opus
  - Plan: inline-execute | Status: rework
  - Classification format mismatch (grep pattern vs /design list-marker format)
  - Pivot Transactions table missing /inline entry
  - Unspecified A.3-5 restructure in /design (Minor/excess)
- [ ] **Fix when-resolve.py** — `x` | sonnet
  - Deduplicate fuzzy matches in output (same entry resolved multiple times)
  - Accept recall-artifact on stdin (line-per-trigger format)
  - Current workaround: zsh array expansion `triggers=("${(@f)$(< file)}") && when-resolve.py "${triggers[@]}"`
- [x] **Pipeline integration** — `x` | opus
  - Plan: inline-execute
  - FR-10 + T6.5 + memory-index + continuation-passing applied, corrector clean (1 critical, 1 major, 1 minor fixed). Review: `plans/inline-execute/reports/review-integration.md`
  - Cross-skill review: `plans/inline-execute/reports/cross-skill-review.md` — 2 major pre-existing (continuation frontmatter) → Retrofit task
- [ ] **Retrofit skill pre-work** — `/design` | opus
  - Many skills lack initial task context loading (task-context.sh, brief.md, recall-artifact) and skill-adapted recall
  - Continuation-passing retrofit: /design and /runbook lack `continuation:` frontmatter blocks and `## Continuation` body sections (cross-skill review: `plans/inline-execute/reports/cross-skill-review.md`, issues 1-4)
  - /runbook lacks "Downstream Consumers" summary section (issue 5)
  - Audit skills for cold-start gaps; retrofit where beneficial
  - Follow-on after /inline delivery
- [ ] **Runbook post-explore gate** — opus
  - /runbook Tier 3 Phase 0.5 has recall (resolve + augment) and Phase 0.75 has recall-diff, but no post-exploration re-scan of memory-index for domains discovered during Glob/Grep verification (step 3). /design has A.2.5 for this. Same pattern needed after Phase 0.5 step 3 discovers file areas not anticipated during step 1 recall.
  - Separate from inline-execute delivery — standalone skill edit
- [x] **Triage feedback script** — sonnet
  - Plan: inline-execute
  - 7 TDD cycles, 13 tests, corrector review dispatched

## Worktree Tasks

- [ ] **Design grounding update** → `design-grounding-update` — `/ground` with session scraper exploration input | opus
  - Session scraper (`plans/prototypes/session-scraper.py`) extracts actual session behavior as grounding evidence
  - Feeds into /design skill grounding refresh — complements external framework research with empirical session data
  - Prior grounding: `plans/reports/design-skill-grounding.md` (6 frameworks, 8 principles, 7 gaps)

- [ ] **Session.md validator** → `session-md-validator` — Scripted precommit check | sonnet
  - Plan: session-validator | worktree-cli-default merged; all FRs can proceed

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Post-merge validation (permanent):**
- After every worktree merge, validate session.md (pending tasks from branch carried over) AND learnings.md (no entries lost from either side)
- Known failure modes: autostrategy drops branch pending tasks, orphaned duplicate lines in append-only files, branch overwrites main-only learnings entries
- Not automated — manual check required until worktree-merge-resilience delivered

**Validator autofix handles placement:**
- `claudeutils validate memory-index` autofixes placement (file section) and ordering issues
- All 37 orphan headers now indexed; 3 duplicates resolved

**Memory index `/how` operator mapping (resolved):**
- Operator prefix no longer used in matching — bare trigger matching handles both `/when` and `/how` entries
- `removeprefix("to ")` in resolver strips leftover "to" from "how to X" invocations

**Learnings at 102 lines, 22 entries:**
- Well over 80-line soft limit. `/codify` needed.

**SessionStart hook #10373 still open:**
- Output discarded for new interactive sessions. Stop hook fallback deployed (Phase 4).

**`_worktree new` requires sandbox bypass:**
- Writes `.claude/settings.local.json` which is in sandbox deny list. Must use `dangerouslyDisableSandbox: true`.

**Custom agents not discoverable as subagent_types:**
- `.claude/agents/*.md` files with proper frontmatter weren't available via Task tool. Built-in types work. May need platform investigation.

**`_worktree rm --force` doesn't restore task to Pending:**
- `rm --force` removes worktree but leaves task in Worktree Tasks section. Manual session.md edit needed to move back to Pending.

**`_worktree rm` fails on merge commits:**
- `_update_session_and_amend` calls `git commit --amend` which fails on merge commits (exit 128). Then `--force` can fail on submodule removal. Manual `rm -rf` of directory needed after.

**Orphaned remember-skill-update directory:**
- `/Users/david/code/claudeutils-wt/remember-skill-update` — git deregistered but directory remains. Needs manual removal.

**Worktree merge drops session.md Worktree Tasks entries:**
- Focused session in branch lacks main's full Worktree Tasks section. Autostrategy resolves in favor of branch, dropping main-only entries. Manual post-merge validation required until merge.py fixed.

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

**Possible Claude Code skill caching:**
- On-disk skills current, but `/design` and `/reflect` invocations received older content. No structural fix — awareness only.

**brief.md in planstate inference:**
- Added as recognized artifact so precommit doesn't flag brief-only plans. But inferred next-action command uses `requirements.md` template (wrong for brief-only). Tasks with brief-only plans must preserve `/design plans/{name}/brief.md` command manually in session.md.

## Next Steps

3 worktrees to create: design-grounding-update, merge-learnings-delta, session-md-validator. Then proceed with next in-tree task.

## Reference Files

- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for all workflow skills/agents
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-02-24.md` — WSJF scoring, 37 tasks ranked
- `plans/task-classification/outline.md` — `/prime` skill + two-section task list design
- `plans/runbook-recall-expansion/requirements.md` — Step agent + corrector recall during full orchestration (7 FRs)
- `plans/skill-progressive-disclosure/brief.md` — Segment loading at gate boundaries (/design and /runbook)
- `plans/reports/design-skill-grounding.md` — Design skill grounding (Strong — 6 frameworks, 8 principles, 7 gaps)