# Session Handoff: 2026-03-01

**Status:** 4 worktrees active (3 original + 1 deliverable review). Continuation-prepend merged. RCA: lock contention hook fix. Decisions: autostrategy filter, task notation [✗]→[†].

## Completed This Session

- **Worktree parallel setup** — 6 tasks branched for parallel execution
  - Runbook recall expansion, Pushback grounding, Fix planstate detector, UPS topic injection, Task classification, Continuation prepend
- **Pushback grounding merge** — worktree merged to main and removed
  - Branch delivered: `plans/pushback-grounding/classification.md`, test additions
  - Validated: no session.md or learnings.md loss (62 lines pre/post)
  - flatten-hook-tiers plan status changed to `delivered` during merge
- **Runbook recall expansion merge** — worktree merged to main and removed
  - Branch delivered: recall artifact resolution in prepare-runbook.py
  - 1 new learning (TDD after full codebase exploration)
  - Validated: learnings 62→66 lines, task removed from Worktree Tasks
  - `_worktree rm` needed `--force` (directory not empty on merge commits — existing blocker)
- **Discussion: wt fuzzy matching** — concluded fuzzy matching belongs at agent layer (inherent in LLM name resolution), not CLI. Agent reads session.md, copies exact name. CLI strict matching prevents silent wrong-task matches. Recommend canceling task.
- **Requirements: worktree-ad-hoc-task** — captured requirements for adding task to session.md before `_worktree new` when task absent from Pending Tasks
  - Plan: worktree-ad-hoc-task | Status: requirements
  - Skill-layer fix only (SKILL.md Mode A), no CLI changes
- **Continuation-prepend merge** — worktree merged to main and removed
  - Branch delivered: continuation-prepend plan, cooperative-protocol-gaps classification, integration tests
  - Validator failure during merge: 4 `[x]` tasks from branch leaked into Pending (autostrategy bug)
  - Manual fix: removed completed tasks, amended merge commit
- **RCA: lock contention** — 3-layer root cause analysis
  - Hook message fixed: "retry the git command" → "Retry your git command — do not delete lock files"
  - Decision updated: `operational-tooling.md` "When git lock error occurs" — concurrent worktree contention
  - Learning added: "When hook messages conflict with behavioral rules"
- **Design-context-gate brief** — `/design` tail-call decision based on context budget
  - Mechanism: UPS hook injects context % from statusline infrastructure (already exists)
  - Threshold needs empirical calibration
- **Deliverable review: runbook-recall-expansion worktree** — created with slug `runbook-recall-expansion`
- **Decisions written** — `operational-tooling.md`:
  - "When merging completed tasks from branch" — filter `[x]`/`[–]` from additive union
  - "When choosing task status markers" — `[✗]` → `[†]` (dagger = dead, visually distinct from `[x]`)
  - Memory index updated with both entries

## Pending Tasks

### Tier 1: Recall/when-resolve (foundational)

- [ ] **Recall tool consolidation** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet
  - Recall simplification: remove sibling expansion (redundant with index scanning). Resolver = pure lookup (key in, section out).
  - Mode reduction: default (per-key, 2 passes), all (per-file, iterated), everything (full corpus). Drop `broad` and `deep` from formal mode set.
  - Grounding: `plans/reports/recall-lifecycle-grounding.md` (per-point mode assignments, lifecycle role contract)
  - Absorbs: Stale recall artifact — diagnose /design producing old-style recall artifact instead of memory key list
- [ ] **Artifact staleness gate** — sonnet
  - Mechanical checkpoint at /requirements, /design, /runbook exit points
  - `claudeutils _recall resolve` touches sentinel; skill compares sentinel mtime to recall-artifact.md AND primary skill artifact (requirements.md, outline.md, design.md, runbook.md)
  - If recall newer than either artifact, trigger update step
  - Two drift vectors: stale recall-artifact (entries loaded not persisted) and stale skill artifacts (decisions loaded after artifact written)
- [ ] **Recall usage scoring** — Post-resolve relevance scoring at skill transitions (/design exit, /runbook exit, /inline exit) | sonnet
  - Per-entry assessment: referenced / informed / unused. Accumulates in `plans/<job>/recall-usage.md`
  - Parallel to triage-feedback.sh: compares pre-execution selection against post-execution usage
  - Grounding: `plans/reports/recall-lifecycle-grounding.md` §Revised Mode Assignment
- [ ] **Generate memory index** — `/design` | opus
  - Each decision/learning declares keywords for index. Index generated from declarations. Diff displayed after update for agent review. Supersedes manual append workflow in `/codify` step 4a.
- [ ] **Delivery supercession** — `d:` memory-index pass at plan delivery for supercession | opus
- [ ] **Recall deduplication** — integrate session context scraping into `claudeutils _recall resolve` to filter already-loaded entries | sonnet
  - Session scraper prototype: `plans/prototypes/session-scraper.py`
  - Dedup should be opt-in (`--new-only` flag or `null` mode), not default — explicit queries may resolve for sub-agent prompts
- [ ] **Recall pipeline** — `d:` recall-artifact stdin format parsing, session log dedup | opus
  - Stdin support delivered (basic). Remaining: parse recall-artifact format on stdin (strip post-"|" keywords, post-"—" relevance notes)
  - Session log scraping to auto-eliminate already-recalled entries
- [ ] **Recall learnings design** — `d:` whether learnings.md entries should be resolvable via `claudeutils _recall resolve` | opus
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
- [ ] **Remove wt rm --force** — remove `--force` flag from `_worktree rm` CLI | sonnet
  - Structural safety: `--force` bypasses the uncommitted-work check that exists to prevent data loss
  - Emergency cleanup via raw `git worktree remove --force` + `rm -rf`

### Tier 3: Workflow non-prose

- [ ] **Orchestrate evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
  - 14 steps: 12 TDD cycles (sonnet) + 2 general steps (opus)
  - Phase 1: agent caching model (4 cycles)
  - Phase 2: orchestrator plan format + verify-step.sh (4 cycles)
  - Phase 3: TDD agent generation + verify-red.sh (4 cycles)
  - Phase 4: SKILL.md rewrite + refactor.md/delegation.md updates (2 steps, opus)
  - Checkpoints: light at phase boundaries, full at Phase 4 (final)
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
- [ ] **Runbook outline review** — update runbook skill: user review gate after outline correction, iterative fix cycle until approved | sonnet
- [ ] **Review auto-commit** — after fixing all issues in deliverable-review, auto handoff and commit | sonnet
- [ ] **Execute flag lint** — precommit lint gate for `/inline ... execute` in session.md | haiku
  - Scan session.md pending tasks for `/inline plans/.* execute` pattern
  - Flag as error: execute entry point in session.md bypasses Phase 2 recall (D+B anchor)
- [ ] **Moderate outline gate** — `/design` skill update | opus
  - When requirements lack structural decisions (module layout, function decomposition, wiring), generate lightweight outline before routing to /runbook
  - Single data point so far — trigger condition needs sharper criteria before implementing
  - Self-modification risk: editing /design during active use
- [ ] **Registry cache to tmp** — inline | sonnet
  - Move continuation registry cache from TMPDIR to project-local tmp/
- [ ] **Block cd-chaining in bash** — PreToolUse hook to block `cd * && *` and `cd *; *`, recommend `git -C` or subshell | sonnet
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **Merge lock retry** — add lock-contention retry to `claudeutils _worktree merge` | sonnet
  - Catch index.lock errors, retry after model latency (no explicit sleep)
  - Bounded retries (3 attempts), report after exhaustion
  - Concurrent worktree sessions cause transient lock contention on shared .git
- [ ] **Merge completed filter** — filter `[x]` and `[–]` tasks from merge additive union in `resolve.py` | sonnet
  - Single-line fix: exclude blocks whose first line matches completed/canceled markers
  - Prevents branch-completed tasks from leaking into main's Pending Tasks
- [ ] **Task notation migration** — replace `[✗]` → `[†]` across codebase | sonnet
  - 23 files reference ✗; active files: execute-rule.md, task-failure-lifecycle.md, error-classification.md, handoff skill, session.md, validators, justfiles
  - Update `extract_task_blocks` regex, session-structure validator
  - Plans/reports are historical — update only active behavioral files
- [ ] **Design context gate** — `/design plans/design-context-gate/brief.md` | sonnet
  - Plan: design-context-gate | Status: brief
  - /design tail-call /inline only when context budget allows, otherwise handoff+commit
  - Mechanism: UPS hook injects context percentage from statusline infrastructure
  - Threshold needs empirical calibration (no confabulated number)

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
- [–] **Worktree fuzzy matching** — canceled; agent layer handles name resolution inherently
- [ ] **Worktree ad-hoc task** — `/design plans/worktree-ad-hoc-task/requirements.md` | sonnet
  - Plan: worktree-ad-hoc-task | Status: requirements
  - Add task to session.md before `_worktree new` when task not yet present
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
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart
  - `python -c` one-liner allowance evaluated before `uv run` redirect
  - `uv run` redirect message mentions `uv sync` as dependency-change path
  - SessionStart: verify `claudeutils` importable, emit `STOP:` if not
  - agent-core SessionStart can assume claudeutils (all consumers have it; post-migration edify ships in plugin)
- [ ] **Calibrate topic params** — extend session-scraper.py | sonnet
  - Blocked by: UPS topic injection (needs production data first)

- [ ] **Dev integration branch** — `/design` persistent worktree for merge landing, async issue resolution | opus
- [ ] **Wt ls session ordering** — `_worktree ls` prints plans in pending task order from session.md | sonnet

## Worktree Tasks

- [ ] **Fix planstate detector** → `fix-planstate-detector` — `/design plans/fix-planstate-detector/requirements.md` | sonnet
  - Plan: fix-planstate-detector | Status: requirements
  - Missing `outlined` status: outline.md grouped under `requirements` fallback

- [ ] **UPS topic injection** → `ups-topic-injection` — `/runbook plans/userpromptsubmit-topic/outline.md` | sonnet
  - Plan: userpromptsubmit-topic | Status: outlined (planstate detector shows `requirements` — fix-planstate-detector bug)




- [ ] **Diagnose wt rm dirty-state** — `plans/wt-rm-dirty/brief.md` | sonnet

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

- `test_markdown_fixtures.py::test_full_pipeline_remark` xfail renders full traceback in markdown report, visually identical to real failure [from: recall-cli-integration]
- `just precommit` shows `✗ Precommit failed` when test sentinel invalidates (any test file change forces rerun) [from: recall-cli-integration]
- All 30 recall tests pass. The `✗` is from xfail report formatting, not a real failure [from: recall-cli-integration]
- Fix is in `pytest-markdown-report` (separate repo), not here [from: recall-cli-integration]

**`test_merge_learnings_segment_diff3_prevents_orphans` ordering dep:**
- Fails during `_worktree merge` precommit, passes in isolation and standalone full suite
- Non-reproducible after merge completes. On reoccurrence: capture `pytest -v` output to identify predecessor test
- Root cause unknown — not CWD pollution (test uses monkeypatch.chdir), not UPS tests (verified), not worktree presence
- Inline TDD after full codebase exploration produces test-after with ceremony. All 15 tests passed on first attempt — no behavioral RED. Must delegate to test-driver in fresh context when task is marked TDD and design session loaded implementation context. [from: runbook-recall-expansion]
## Next Steps

4 worktrees active (fix-planstate-detector, ups-topic-injection, task-classification, runbook-recall-expansion). Userpromptsubmit-topic worktree still registered (merged, needs `wt-rm userpromptsubmit-topic`). Mechanical tasks ready: autostrategy completed filter (single-line fix), task notation migration (23 files). Learnings at 70 lines — approaching `/codify` threshold.

## Reference Files

- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for all workflow skills/agents
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-02-28.md` — WSJF scoring, 71 tasks ranked (supersedes 2026-02-27)
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
- `plans/pushback-grounding/requirements.md` — Claim verification + recall for `d:` discussion mode
- `plans/worktree-ad-hoc-task/requirements.md` — Add task to session.md before worktree creation when absent