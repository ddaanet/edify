# Session Handoff: 2026-02-25

**Status:** Batch fix of 3 pending tasks: precommit validation wired, autofix removed from hook, orphan headers indexed.

## Completed This Session

- **Parsing fixes batch executed** — all 6 cycles, 2 fixes + 3 verifications + 1 dead code cleanup
  - Cycle 1: validate-runbook model-tags extension filter — `.sh` files under artifact paths no longer flagged (only `.md`)
  - Cycle 2: validate-runbook lifecycle `known_files` parameter — pre-existing files exempt from modify-before-create
  - Cycle 3: C1 model propagation — verified already fixed, regression test added
  - Cycle 4: C2 phase numbering — verified already fixed (gapped phases 1,3,5 preserved), regression test added
  - Cycle 5: C3 phase context completeness — documented post-cycle content not in preamble by design
  - Cycle 6: Dead code — removed discarded `splitlines()` in prepare-runbook.py, discarded expression in memory_index_checks.py
  - Test file compaction: extracted `_run_validate` and `_run_prepare` helpers, both files under 400-line limit
  - Plans delivered: parsing-fixes-batch, runbook-generation-fixes (absorbed)
- **Memory index orphan investigation** — tracked `when validating runbook pre-execution` entry
  - Entry added in `bbcafd3c`, section never created (content only in T4.5 table row)
  - `check_orphan_entries()` correctly detects it via `claudeutils validate memory-index`
  - Precommit gap: `just precommit` runs ruff/docformatter/mypy/pytest/line-limits but NOT `claudeutils validate`
  - Scale: 12 orphan index entries + 33 orphan headers + 3 cross-file duplicates
- **Parsing fixes batch scoping** (prior session) — surveyed all pipeline/parsing issues, batched 7 items into Tier 2 plan
  - Plan written: `plans/parsing-fixes-batch/plan.md` — 6 cycles, Tier 2 lightweight delegation
  - Absorbs runbook-generation-fixes scope
  - Markdown xfail excluded (separate task, requires multiline paragraph parsing)
- **Workflow grounding audit** — inventoried all workflow skills/agents for grounding provenance
  - Report: `plans/reports/workflow-grounding-audit.md`
  - 2 grounded from scratch (/ground, /prioritize), 3 partially grounded, 5 high-leverage ungrounded
  - /design identified as highest-leverage grounding gap — gates all downstream work
  - Discussion: /design's accumulated patches (triage gate, sufficiency gate, recall artifact, D+B anchors) are symptom-oriented fixes that grounded foundations might have prevented
- **Bugfix process discussion** — converged on: structured-bugfix skill absorbed into grounded /design (fix-category assessment as routing outcome, not separate skill)
  - Compensate-and-continue remains separate (operational recovery, not design-time)
  - Three-part model: tool deviation detection (hook) → compensation+continue (skill) → proper fix (via grounded /design)
- **Deliverable review: parsing-fixes-batch** — 0 critical, 2 major, 2 minor
  - Report: `plans/parsing-fixes-batch/reports/deliverable-review.md`
  - Findings fixed: added `test_lifecycle_known_file_cli` (CLI `--known-file` arg path), refactored `test_model_tags_non_markdown_artifact_not_flagged` to use `_run_validate` helper, moved `datetime` import to module-level alongside `UTC`
  - Extended `_run_validate` helper with keyword-only `extra_args` parameter
- **Batch fix: 3 pending tasks**
  - Removed `ruff check --fix-only` from `posttooluse-autoformat.sh` — hook now formats only, no autofix
  - Fixed 3 duplicate decision headers: comparing-file-versions, constraining-task-names, step-file-inventory (kept more complete version, relocated memory-index entries)
  - Added 37 memory-index entries for orphan headers, renamed `Inline Eligibility Criteria` → `When Phase Qualifies As Inline`
  - Wired `claudeutils validate memory-index` into `run-checks()` in justfile
  - Scoped to memory-index only — learnings/tasks/planstate/session-structure validators have pre-existing errors
  - when-recall section lookup bug already fixed in prior commit (orphan entry removed in `09e1b700`)

## Pending Tasks

- [x] **Deliverable review: parsing-fixes-batch** — reviewed, 0 critical, 2 major
  - Plan: parsing-fixes-batch | Status: delivered
  - Report: `plans/parsing-fixes-batch/reports/deliverable-review.md`

- [x] **Wire validation into precommit** — memory-index validator wired into `run-checks()`
  - Scoped to memory-index only; other validators deferred (pre-existing errors)

- [x] **Remove autofix from PostToolUse hook** — `ruff check --fix-only` removed, format-only now

- [x] **Fix when-recall section lookup bug** — orphan entry already removed in prior commit

- [ ] **Wire remaining precommit validators** — fix pre-existing errors in learnings/tasks/planstate/session-structure validators, wire each into `run-checks()` | sonnet
  - Learnings: title length limit (7 entries exceed 5-word max), orphaned content block
  - Tasks: 25-char slug limit (30+ tasks exceed), forbidden characters (:, /, ()
  - Planstate: 12 plans with no artifacts or missing phase files, 10 archived plans with remaining directories
  - Session-structure: 2 glob-pattern reference files not found

- [ ] **Tool deviation detection hook** — PostToolUse hook on Bash to detect when-resolve.py failures | sonnet
  - Check exit code + stderr patterns from specific scripts
  - Narrower than governor agent (PreToolUse on everything), but catches the specific failure class

- [ ] **Design compensate-and-continue skill** — `/ground` then `/design` | opus
  - Activated after unexpected stop. Records compensation strategy. Applies trivial workarounds inline (e.g., rename heading to route around parser bug). Creates pending task for proper fix. Resumes interrupted work via continuation-prepend.
  - Needs grounding on failure recovery patterns, compensation strategies

- [ ] **Ground /design skill** — `/ground` then redesign | opus
  - Highest-leverage grounding target — every task flows through /design
  - Ground against established design methodology (requirements engineering, architectural decision processes, complexity assessment)
  - Absorbs structured-bugfix process as routing outcome (fix-category assessment in triage)
  - Compare grounded structure against current /design to identify structural gaps vs cosmetic differences

- [ ] **Ground workflow skills (priority order)** — `/ground` each per audit | opus
  - Audit: `plans/reports/workflow-grounding-audit.md`
  - Priority: /runbook → review agents (corrector + design-corrector batch) → /orchestrate → /handoff
  - /design done separately (above) as highest priority
  - Skip low-benefit: /commit, artisan, test-driver, /shelve

- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet
- [ ] **Precommit python3 redirect** — `/design plans/precommit-python3-redirect/brief.md` | sonnet
  - PreToolUse hook: intercept python3/uv-run/ln patterns, redirect to correct invocations
- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)
- [ ] **Handoff wt awareness** — Only consolidate memory in main repo | sonnet
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: orchestrate-evolution
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **Merge learnings delta** — Reconcile learnings.md after diverged merge | sonnet
  - Plan: merge-learnings-delta | Strategy: main base + branch delta
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite
- [ ] **Migrate test suite to diamond** — Needs scoping | depends on runbook evolution (delivered)
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Session.md validator** — Scripted precommit check | sonnet
  - Plan: session-validator | worktree-cli-default merged; all FRs can proceed
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Ground state-machine review criteria** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Cache expiration prototype** — Debug log token metrics, measure TTL | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **TDD cycle test optimization** — Selective test rerun via dependency analysis | sonnet
- [ ] **Fix task-context.sh task list bloat** — Filter/trim output | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [!] **Session CLI tool** — `/runbook plans/handoff-cli-tool/outline.md` | sonnet
  - Plan: handoff-cli-tool | Status: designed (outline reviewed 6 rounds, ready for runbook)
  - `_session` group (handoff, status, commit)
  - Discussion conclusions baked into outline: amend, git passthrough, deviation-only output, submodule labeling
- [ ] **UserPromptSubmit topic detection hook** — Phase 7 analysis recommends this as highest-impact recall improvement | sonnet
  - Seed keyword table from 200+ memory-index triggers
  - Inject matching decision content via additionalContext on prompt submit
  - Complementary to recall pass (cheap first layer vs deep pipeline integration)
- [ ] **Prioritize script assistance** — Automate mechanical parts of prioritization scoring | sonnet
- [ ] **Task classification** — `/runbook plans/task-classification/outline.md` | sonnet
  - Plan: task-classification | Status: designed (outline reviewed, ready for runbook)
  - `/prime` skill (ad-hoc plan context) + two-section task list (In-tree / Worktree Tasks)
  - Scope: `session.py`, `resolve.py`, `aggregation.py`, `session_structure.py`, handoff skill, execute-rule.md
- [ ] **Recall CLI integration** — Production `claudeutils _recall` CLI (check/resolve/diff), Click, TDD | sonnet
  - Prototype delivered via recall-tool-anchoring worktree
- [ ] **Prose gate anchoring terminology** — Find proper name for D+B pattern, ground, update docs | opus
- [ ] **Consolidate recall tooling** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet
- [ ] **Execute orchestrate-evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
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
- [ ] **Deliverable review auto-commit** — after fixing all issues in deliverable-review, auto handoff and commit | sonnet
- [ ] **Worktree new fuzzy matching** — `_worktree new` accepts approximate task names instead of exact match | sonnet
- [ ] **Design skill stale recall artifact format** — diagnose /design producing old-style recall artifact instead of memory key list | sonnet
- [ ] **Skill progressive disclosure** — `/design plans/skill-progressive-disclosure/brief.md` | opus
  - Plan: skill-progressive-disclosure | Status: requirements
  - Segment loading at gate boundaries: initial load → write-outline → write-design (/design); tier assessment → tier3-planning → expansion (/runbook)
  - Complementary with skills-quality-pass FR-3 extractions
- [ ] **Runbook outline review loop** — update runbook skill: user review gate after outline correction, iterative fix cycle until approved | sonnet
- [ ] **Runbook recall expansion** — `/design plans/runbook-recall-expansion/requirements.md` | sonnet
  - Plan: runbook-recall-expansion | Status: requirements
  - prepare-runbook.py recall injection, corrector.md self-loading, two-pattern docs (7 FRs)
- [ ] **Recall pipeline improvements** — `d:` when-resolve.py stdin/recall-artifact support, session log dedup | opus
  - Accept recall keys on stdin (ignore post-"|" memory-index format), change recall-artifact format (dash separator unsafe)
  - Session log scraping to auto-eliminate already-recalled entries
- [ ] **Recall learnings integration** — `d:` whether learnings.md entries should be resolvable via when-resolve.py | opus
  - Implies memory-index format changes (new source type), resolver changes — genuine design uncertainty
- [ ] **Generate memory index from decisions** — `/design` | opus
  - Each decision/learning declares keywords for index. Index generated from declarations. Diff displayed after update for agent review. Supersedes manual append workflow in `/codify` step 4a.

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Merge resolution produces orphaned lines in append-only files:**
- When branch modifies existing entry in-place AND both sides add at tail, git appends modified line as duplicate.
- Manual post-merge check required until worktree-merge-resilience automated

**Validator autofix handles placement:**
- `claudeutils validate memory-index` autofixes placement (file section) and ordering issues
- All 37 orphan headers now indexed; 3 duplicates resolved

**Memory index `/how` operator mapping (resolved):**
- Operator prefix no longer used in matching — bare trigger matching handles both `/when` and `/how` entries
- `removeprefix("to ")` in resolver strips leftover "to" from "how to X" invocations

**Learnings healthy — 40 lines, 7 entries:**
- `/codify` completed and merged. Next consolidation not urgent.

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

**when-resolve.py "Section not found" (resolved):**
- Orphan entry "When Validating Runbook Pre-execution" removed in commit `09e1b700`. No code bug — data issue only.

## Next Steps

Wire remaining precommit validators (learnings, tasks, planstate, session-structure) — fix pre-existing errors then add each to `run-checks()`.

## Reference Files

- `plans/parsing-fixes-batch/plan.md` — Tier 2 cycle plan (6 cycles, validate-runbook + prepare-runbook + dead code)
- `plans/parsing-fixes-batch/recall-artifact.md` — Testing decisions, diagnostic context
- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for all workflow skills/agents
- `plans/runbook-generation-fixes/brief.md` — C1-C3 bug diagnostics (absorbed into parsing-fixes-batch)
- `plans/prepare-runbook-fixes/diagnostic.md` — Bug 1-2 diagnostics (delivered)
- `plans/recall-pass/brief.md` — 4-pass model, reference forwarding, discussion conclusions
- `plans/reports/recall-pass-grounding.md` — Moderate grounding (CE + Agentic RAG synthesis)
- `plans/reports/recall-pass-internal-brainstorm.md` — 27 dimensions, project-specific constraints
- `plans/planstate-delivered/outline.md` — Plan lifecycle design (7 decisions, 3 phases)
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-02-24.md` — WSJF scoring, 37 tasks ranked
- `plans/recall-tool-anchoring/outline.md` — Recall gate tool-anchoring design (D+B + reference manifest)
- `plans/recall-tool-anchoring/recall-artifact.md` — 11 entries, reference manifest format
- `plans/recall-tool-anchoring/reports/recall-gate-inventory.md` — 31 gates inventoried across 13 files
- `plans/task-classification/outline.md` — `/prime` skill + two-section task list design (8 rounds, reviewed)
- `plans/task-classification/reports/outline-review.md` — Corrector review (0 critical, 3 major fixed)
- `plans/task-lifecycle/outline.md` — Planstate-derived commands + STATUS continuation design
- `plans/when-resolve-fix/diagnostic-double-to.md` — Double-to + cross-operator bugs, TDD plan, code paths
- `plans/when-resolve-fix/reports/corrector-review.md` — Corrector review of 4-bug fix (0 critical, 0 major)
- `plans/skills-quality-pass/design.md` — Skills quality pass design (3 workstreams, 10 FRs, 7 NFRs)
- `plans/skills-quality-pass/recall-artifact.md` — 10 resolution keys (corrected from inline summaries)
- `plans/skills-quality-pass/runbook-outline.md` — 5 phases, 16 steps, parallel 4-agent execution model
- `plans/skills-quality-pass/reports/runbook-outline-review.md` — Corrector review (0 critical, 3 major fixed)
- `plans/runbook-recall-expansion/requirements.md` — Step agent + corrector recall during full orchestration (7 FRs)
- `plans/skills-quality-pass/reports/skill-inventory.md` — Sonnet scout v2: 30 skills, content segmentation, compression opportunities
- `plans/skills-quality-pass/reports/full-gate-audit.md` — Sonnet scout: 12 prose-only gates, fix directions
- `plans/reports/skill-optimization-grounding.md` — Segment→Attribute→Compress framework (LLMLingua/ProCut)
- `plans/skill-progressive-disclosure/brief.md` — Segment loading at gate boundaries (/design and /runbook)
- `plans/skills-quality-pass/reports/phase-{2-5}-report.md` — Execution agent reports (changes, NFR verification, line counts)
- `plans/skills-quality-pass/reports/review-r{1-4}-phase{2-5}.md` — Convergence skill reviews (4 reviewers)
- `plans/skills-quality-pass/reports/behavior-invariance-review.md` — 50-path independent verification (0 issues)
- `plans/skills-quality-pass/reports/resolved-recall.md` — Pre-resolved recall dump for shared agent consumption
- `plans/parsing-fixes-batch/reports/deliverable-review.md` — Deliverable review (0 critical, 2 major fixed)
