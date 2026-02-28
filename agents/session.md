# Session Handoff: 2026-02-28

**Status:** Hook cwd-drift bypass diagnosed and fixed. Supercession passes complete (recall-null + hook fix). Recall-null deliverable review still pending.

## Completed This Session

- **Recall-null planning** — `/design` triage → Moderate → `/runbook` Tier 2 assessment → outline with Execution Model
  - Scope discussion: null mode + D+B gate language + post-explore gates. Artifact generation for sub-agents excluded (that's runbook-recall-expansion scope).
  - Inventoried recall gate state across 4 pipeline skills: /requirements, /design, /runbook, /inline
  - Classification: Moderate (behavioral code forces minimum), mixed artifact destination (production + agentic-prose)
  - Tier 2: 6 files, benefits from agent isolation (TDD sonnet + prose opus), no full orchestration
  - Plan: recall-null | Outline: `plans/recall-null/outline.md` (has Execution Model — ready for /inline)
- **Per-consumer recall artifacts** — curated subsets of recall-artifact for each agent type
  - `tdd-recall-artifact.md` (5 entries: CLI testing, assertions, lint gate)
  - `review-recall-artifact.md` (7 entries: D+B pattern, model selection, holistic fixes)
  - `skill-review-recall-artifact.md` (6 entries: skill editing, D+B propagation)
- **Recall broad** — loaded 16/21 decision files. Remaining 5 (data-processing, deliverable-review, markdown-tooling, operational-tooling, validation-quality) irrelevant to recall gates
- **Recall lifecycle grounding** — `/ground` research on artifact lifecycle across pipeline stages
  - Three grounded patterns: accumulator with stage provenance (LangGraph+OpenLineage), forward-only refinement (HL7 CRMI), lifecycle role contract (RUP+TOGAF)
  - Per-point retrieval mode assignment across 10 pipeline recall points: 8 per-key (default), 2 per-file iterated (all)
  - Recall system simplification: no sibling expansion (redundant with index scanning), per-key and per-file only
  - Revised mode set: default (per-key, two passes, scored selection), all (per-file, iterated), everything (full corpus). `broad` and `deep` drop from pipeline usage.
  - Post-resolve relevance scoring at skill transitions (not per-point) — design input for recall calibration
  - Reports: grounding (`plans/reports/recall-lifecycle-grounding.md`), internal inventory (`plans/reports/recall-lifecycle-internal-codebase.md`), external research (`plans/reports/recall-lifecycle-external-research.md`)
- **Recall everything** — loaded all 21 decision files (full corpus for grounding context)
- **Recall-null delivery** — `/inline plans/recall-null` executed (Tier 2)
  - Phase 1 (TDD, sonnet): 2 cycles — null query silent exit, mixed null+real filtering. Tests: `tests/test_when_null.py`
  - Phase 2 (inline, opus): D+B gate anchoring propagated to /requirements, /runbook (T1/T2 + T3), /inline. /design A.2.5 verified canonical (no-op). Post-explore recall gates added to /requirements and /runbook T3
  - Null artifact format: explicit `null — no relevant entries found` entry in /requirements and /design artifact format blocks
  - Corrector: 0C/0M/2m — Tier 2 parenthetical consistency, fragile test assertion. Both fixed. Report: `plans/recall-null/reports/review.md`
  - Triage feedback: no-classification (no divergence)
- **Hook cwd-drift bypass** — diagnosed and fixed
  - Root cause: `.claude/hooks/submodule-safety.py` used relative path in settings.json. After cwd drift (`cd agent-core && ...`), hook file not found → hook errors are non-blocking → guard silently disabled
  - Fix: prefixed 4 relative hook paths with `$CLAUDE_PROJECT_DIR/` (submodule-safety ×2, block-tmp, symlink-redirect, recall-check)
  - New decision: "When Hook Commands Use Relative Paths" in hook-patterns.md + memory-index entry
- **Supercession passes** — recall-null + hook fix
  - Recall-null: updated "When Selecting Gate Anchor Tools" (null mode now delivered, not proposed). 6 other entries checked — describe patterns recall-null conforms to, no supersession
  - Hook fix: new decision entry, no existing entries superseded

## Pending Tasks

### Tier 1: Recall/when-resolve (foundational)

- [x] **Fix when-resolve.py** — dedup, stdin, navigation simplification delivered
- [x] **Review when-resolve** — delivered, 0C/0M/4m (3 fixed inline)
- [x] **Recall-null delivery** — `/inline plans/recall-null` | opus
  - Plan: recall-null | Status: delivered
  - Phase 1: null mode TDD (2 cycles, test-driver at sonnet). Phase 2: skill gate language (5 inline edits, opus direct)
  - Absorbs: when-resolve null mode + runbook post-explore gate
- [ ] **Review recall-null** — `/deliverable-review plans/recall-null` | opus | restart
- [ ] **Recall CLI integration** — Production `claudeutils _recall` CLI (check/resolve/diff), Click, TDD | sonnet
  - Prototype delivered via recall-tool-anchoring worktree
- [ ] **UserPromptSubmit topic** — Phase 7 analysis recommends this as highest-impact recall improvement | sonnet
  - Seed keyword table from 200+ memory-index triggers
  - Inject matching decision content via additionalContext on prompt submit
  - Complementary to recall pass (cheap first layer vs deep pipeline integration)
- [ ] **Runbook recall expansion** — `/design plans/runbook-recall-expansion/requirements.md` | sonnet
  - Plan: runbook-recall-expansion | Status: requirements
  - prepare-runbook.py recall injection, corrector.md self-loading, two-pattern docs (7 FRs)
- [ ] **When-resolve bloat** — group resolved entries by source file when batch-resolving multiple queries | sonnet
- [ ] **Recall tool consolidation** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet
  - Recall simplification: remove sibling expansion (redundant with index scanning). Resolver = pure lookup (key in, section out).
  - Mode reduction: default (per-key, 2 passes), all (per-file, iterated), everything (full corpus). Drop `broad` and `deep` from formal mode set.
  - Grounding: `plans/reports/recall-lifecycle-grounding.md` (per-point mode assignments, lifecycle role contract)
- [ ] **Artifact staleness gate** — sonnet
  - Mechanical checkpoint at /requirements, /design, /runbook exit points
  - `when-resolve.py` touches sentinel; skill compares sentinel mtime to recall-artifact.md AND primary skill artifact (requirements.md, outline.md, design.md, runbook.md)
  - If recall newer than either artifact, trigger update step
  - Two drift vectors: stale recall-artifact (entries loaded not persisted) and stale skill artifacts (decisions loaded after artifact written)
- [ ] **Recall usage scoring** — Post-resolve relevance scoring at skill transitions (/design exit, /runbook exit, /inline exit) | sonnet
  - Per-entry assessment: referenced / informed / unused. Accumulates in `plans/<job>/recall-usage.md`
  - Parallel to triage-feedback.sh: compares pre-execution selection against post-execution usage
  - Grounding: `plans/reports/recall-lifecycle-grounding.md` §Revised Mode Assignment
- [ ] **Generate memory index** — `/design` | opus
  - Each decision/learning declares keywords for index. Index generated from declarations. Diff displayed after update for agent review. Supersedes manual append workflow in `/codify` step 4a.
- [x] **Runbook post-explore gate** — absorbed into recall-null delivery (outline item 2.4)
- [ ] **Delivery supercession** — `d:` memory-index pass at plan delivery for supercession | opus
- [ ] **Stale recall artifact** — diagnose /design producing old-style recall artifact instead of memory key list | sonnet
- [ ] **Recall deduplication** — integrate session context scraping into `when-resolve.py` to filter already-loaded entries | sonnet
  - Session scraper prototype: `plans/prototypes/session-scraper.py`
  - Dedup should be opt-in (`--new-only` flag or `null` mode), not default — explicit queries may resolve for sub-agent prompts
- [ ] **Recall pipeline** — `d:` recall-artifact stdin format parsing, session log dedup | opus
  - Stdin support delivered (basic). Remaining: parse recall-artifact format on stdin (strip post-"|" keywords, post-"—" relevance notes)
  - Session log scraping to auto-eliminate already-recalled entries
- [ ] **Recall learnings design** — `d:` whether learnings.md entries should be resolvable via when-resolve.py | opus
  - Implies memory-index format changes (new source type), resolver changes — genuine design uncertainty
- [ ] **Lint-gated recall** — PostToolUse hook: inject memory-index on first lint/precommit red after green (state-transition gated) | sonnet
- [ ] **Lint recall gate** — PreToolUse recall pass before lint fix attempt; depends on when-resolve null mode | sonnet

### Tier 2: Workflow prose (load bearing)

- [ ] **Skill disclosure** — `/design plans/skill-progressive-disclosure/brief.md` | opus
  - Plan: skill-progressive-disclosure | Status: requirements
  - Segment loading at gate boundaries: initial load → write-outline → write-design (/design); tier assessment → tier3-planning → expansion (/runbook)
  - Complementary with skills-quality-pass FR-3 extractions
- [ ] **Ground workflow skills** — `/ground` each per audit | opus
  - Audit: `plans/reports/workflow-grounding-audit.md`
  - Priority: /runbook → review agents (corrector + design-corrector batch) → /orchestrate → /handoff
  - /design completed — grounded and redesigned
  - Skip low-benefit: /commit, artisan, test-driver, /shelve
- [ ] **Skill-dev skill** — `/design` | sonnet
  - Front-load plugin-dev:skill-development with project-specific skill editing patterns via ad-hoc continuation passing
  - Content: description field rules, extraction safety, control flow verification, entry point naming, prose quality ref
  - Replace ambient `.claude/rules/skill-development.md` path trigger with explicit skill invocation
- [ ] **Agentic prose terminology** — replace "LLM prose"/"LLM-consumed prose" variants across codebase | sonnet
  - Search: "llm prose", "llm-prose", "LLM-prose", "LLM-consumed prose", "LLM generated prose" (with/without hyphens)
  - Replace with "agentic prose" / "agentic-prose" as appropriate per context
- [ ] **Skill prompt-composer** — migrate skill authoring to use prompt-composer pattern | sonnet
- [ ] **Retrofit skill pre-work** — `/design` | opus
  - Many skills lack initial task context loading (task-context.sh, brief.md, recall-artifact) and skill-adapted recall
  - Continuation-passing retrofit: /design and /runbook lack `continuation:` frontmatter blocks and `## Continuation` body sections (cross-skill review: `plans/inline-execute/reports/cross-skill-review.md`, issues 1-4)
  - /runbook lacks "Downstream Consumers" summary section (issue 5)
  - Audit skills for cold-start gaps; retrofit where beneficial
  - Follow-on after /inline delivery
- [ ] **Prose gate terminology** — Find proper name for D+B pattern, ground, update docs | opus
- [ ] **Memory-index loading docs** — update references claiming memory-index is @-ref from CLAUDE.md | sonnet
- [ ] **Decision drift audit** — audit decision files and learnings.md for stale operational assumptions (e.g., `uv run` references when sandbox-denied) | sonnet

### Tier 3: Workflow non-prose

- [ ] **Orchestrate evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
  - 14 steps: 12 TDD cycles (sonnet) + 2 general steps (opus)
  - Phase 1: agent caching model (4 cycles)
  - Phase 2: orchestrator plan format + verify-step.sh (4 cycles)
  - Phase 3: TDD agent generation + verify-red.sh (4 cycles)
  - Phase 4: SKILL.md rewrite + refactor.md/delegation.md updates (2 steps, opus)
  - Checkpoints: light at phase boundaries, full at Phase 4 (final)
- [ ] **Task classification** — `/runbook plans/task-classification/outline.md` | sonnet
  - Plan: task-classification | Status: designed (outline reviewed, ready for runbook)
  - `/prime` skill (ad-hoc plan context) + two-section task list (In-tree / Worktree Tasks)
  - Scope: `session.py`, `resolve.py`, `aggregation.py`, `session_structure.py`, handoff skill, execute-rule.md
- [ ] **Handoff --commit removal** — remove --commit from /handoff, expand standalone to chain, deduplicate [handoff, commit] | sonnet
  - ~60 occurrences: skills, fragments, tests, continuation infrastructure, decision files
  - Motivation: decouple handoff from commit-ready state (handoff should work on dirty tree)
- [ ] **Markdown migration** — `/design` | opus
  - Wrap existing markdown parser with Claude-specific lenient normalization
  - Line-wrap all files, replace ad-hoc regex parsers (prepare-runbook, session merge, validate-runbook, markdown cleanup)
  - Token counting API + sqlite user cache, threshold migration (line counts → tokens)
  - `just setup` sandbox config for cache dir
  - Parsing fixes batch delivered — parser can now replace regex code
- [ ] **Entry gate propagation** — `/design` | opus
  - Add git-clean + precommit entry gates to /orchestrate, /deliverable-review, corrector agent
  - Cross-cutting pattern — needs /design to resolve: each skill body vs shared fragment vs hook, and per-consumer questions (corrector double-gating, orchestrate checkpoint overlap, deliverable-review session context)
  - Follow-on after /inline delivery
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Runbook outline review** — update runbook skill: user review gate after outline correction, iterative fix cycle until approved | sonnet
- [ ] **Review auto-commit** — after fixing all issues in deliverable-review, auto handoff and commit | sonnet
- [ ] **Block cd-chaining in bash** — PreToolUse hook to block `cd * && *` and `cd *; *`, recommend `git -C` or subshell | sonnet
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus

### Tier 4: Rest

- [ ] **Session scraping** — `/design plans/session-scraping/requirements.md` | sonnet
  - Requirements captured, ready for design
  - Key decisions: all ~/.claude/projects/ (not just claudeutils), agent files are first-class sources, many-to-many session↔commit, tool I/O noise by default
- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tool deviation hook** — PostToolUse hook: agents declare expected Bash outcome, hook validates actual vs declared | sonnet
  - General framework: agent declares expected exit code + output pattern before Bash call
  - PostToolUse hook compares actual result, stops or redirects to diagnose-and-compensate on mismatch
  - Broader than original scope (was: just when-resolve.py failures)
- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [ ] **Fix task-context bloat** — Filter/trim output | sonnet
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **Plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Tier threshold grounding** — calibrate Tier 1/2/3 file-count thresholds against empirical data | opus
  - Thresholds (<6, 6-15, >15) are ungrounded operational parameters
  - Needs measurement from execution history, not confabulated heuristics
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet
- [ ] **Cross-tree requirements** — `/requirements` skill writes to main from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Worktree fuzzy matching** — `_worktree new` accepts approximate task names instead of exact match | sonnet
- [ ] **TDD test optimization** — Selective test rerun via dependency analysis | sonnet
- [ ] **Session.md validator** — Scripted precommit check | sonnet
  - Plan: session-validator
  - Includes plan-archive coverage check (deleted plans must have archive entry)
- [ ] **Update prioritize skill** — use `claudeutils _worktree ls` instead of `list_plans()` ad-hoc Python | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Compensate-continue skill** — `/ground` then `/design` | opus
  - Activated after unexpected stop. Records compensation strategy. Applies trivial workarounds inline (e.g., rename heading to route around parser bug). Creates pending task for proper fix. Resumes interrupted work via continuation-prepend.
  - Needs grounding on failure recovery patterns, compensation strategies
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Diagnose compression loss** — RCA against commit `0418cedb` | sonnet
- [ ] **Test diamond migration** — Needs scoping | depends on runbook evolution (delivered)
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [ ] **Cache expiration** — Debug log token metrics, measure TTL | sonnet
- [ ] **Prioritize script** — Automate mechanical parts of prioritization scoring | sonnet
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart
- [ ] **Ground state coverage** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus

### Blocked / Terminal

- [–] **Handoff wt awareness** — superseded; /codify is now manual
- [!] **Session CLI tool** — `/design plans/handoff-cli-tool/requirements.md` | sonnet
  - Plan: handoff-cli-tool | Status: requirements
  - `_session` group (handoff, status, commit)
  - Discussion conclusions baked into outline: amend, git passthrough, deviation-only output, submodule labeling
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: orchestrate-evolution

## Worktree Tasks

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

Hook fix committed. Restart required (settings.json hook paths changed). Next: **Deliverable review: recall-null** — `/deliverable-review plans/recall-null` (opus, restart).

## Reference Files

- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for all workflow skills/agents
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-02-27.md` — WSJF scoring, 61 tasks ranked (supersedes 2026-02-24)
- `plans/task-classification/outline.md` — `/prime` skill + two-section task list design
- `plans/runbook-recall-expansion/requirements.md` — Step agent + corrector recall during full orchestration (7 FRs)
- `plans/skill-progressive-disclosure/brief.md` — Segment loading at gate boundaries (/design and /runbook)
- `plans/reports/design-skill-grounding.md` — Design skill grounding (updated with session empirical data)
- `plans/inline-execute/outline.md` — /inline skill design outline
- `plans/inline-execute/reports/cross-skill-review.md` — Cross-skill review (continuation frontmatter gaps)
- `agents/decisions/pipeline-contracts.md` — Pipeline contract decision file (new)
- `plans/recall-null/outline.md` — Recall-null execution outline with Execution Model (Tier 2, ready for /inline)
- `plans/reports/recall-lifecycle-grounding.md` — Grounded recall artifact lifecycle (3 patterns, per-point mode assignments, mode reduction)
- `plans/reports/recall-lifecycle-internal-codebase.md` — Internal inventory: recall-artifact handling across all pipeline skills
- `plans/reports/recall-lifecycle-external-research.md` — External research: 10 frameworks (HL7 CRMI, PROV-DM, OpenLineage, ADK, LangGraph, etc.)