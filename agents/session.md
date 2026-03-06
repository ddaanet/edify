# Session Handoff: 2026-03-06

**Status:** Infrastructure fixes + worktree batch merge cleanup.

## Completed This Session

- **Justfile bash prolog fix:**
  - `/usr/bin/env bash -euo pipefail` → shebang + `set` on separate line (env doesn't pass flags portably)
  - Fixed in main justfile, agent-core `justfile-base.just`, and all 7 active worktrees
- **docformatter install:** `uv tool install docformatter --python 3.13` (untokenize dependency incompatible with Python 3.14)
- **Stop hook TMPDIR fix:** `stop-health-fallback.sh` failed under `set -u` when `TMPDIR` unset — added `TMPDIR="${TMPDIR:-/tmp}"` fallback
- **Handoff --commit removal merged + worktree removed:**
  - Removed `--commit` flag from `/handoff`, expanded `hc` to chain `/handoff, /commit`
  - Decoupled handoff from commit-ready state
  - Worktree justfile discarded (already on main), worktree removed
- **Recall tool consolidation absorbed:** Scope covered by Active recall system FR-7 (mode simplification) and C-3 (infrastructure consolidation). Worktree force-removed (no deliverables).
- **skill-description-evals merged + worktree removed:** Canceled after analysis — learning captured ("When skill description triggering appears important"). Branch recreated from commit, merged to preserve analysis, then deleted.
- **Vet false positives merged + worktree removed:** "Do NOT Flag" false positive suppression added to corrector agents. Plan: vet-false-positives (delivered).
- **Explore Anthropic plugins worktree removed:** Branch commits reachable via sub-worktree merges.
- **Session scraping merged + worktree removed:** Session scraper prototype delivered. Plan: session-scraping (delivered).
- **Discussion worktree created:** `discuss` — bare worktree for discussions that don't block main.
- **Orphaned worktree directories cleaned up:** handoff-commit-removal, recall-tool-consolidation (git registration removed but filesystem dirs persisted).
- **Wt ls session ordering merged + worktree removed:** `_worktree ls` now prints plans in session.md pending task order. New in-tree task from branch: Command lint gate (haiku).
- **Worktree merge from main merged + worktree removed:** 10 TDD cycles + 1 inline step delivered. Plan: worktree-merge-from-main (ready). Adds `_worktree merge --from-main` direction parameter.
- **Retrospective worktree created:** `retrospective` — focused worktree for agentic programming blog post raw materials.

- **Plan cleanup (14 directories deleted):**
  - Delivered (11): execute-skill-dispatch, flatten-hook-tiers, inline-tdd-dispatch, recall-cli-integration, recall-null, runbook-recall-expansion, task-classification, task-pattern-statuses, userpromptsubmit-topic, when-resolve-fix, wt-rm-dirty
  - Superseded (3): merge-submodule-ordering (absorbed by merge-lifecycle-audit), fix-planstate-detector (all FRs implemented), cooperative-protocol-gaps (superseded by Retrofit skill pre-work)
  - Plan-archive updated with entries for all 14
- **Worktree cleanup:** userpromptsubmit-topic worktree removed (was merged but registered)
- **Prioritization rescore:** 73 tasks scored via `plans/prototypes/score.py` (file: `plans/reports/prioritization-2026-03-02.md`)
  - 8 removed (5 delivered, 1 absorbed, 1 no-task, 1 canceled), 10 new tasks scored
  - Top 5: Orchestrate evolution (6.0), Merge completed filter (4.0), Execute flag lint (3.0), Skill disclosure (2.6), Session.md validator (2.4)
  - 12 unscheduled plans identified (plans with artifacts but no session.md task)
- **Orphan plan RCA + cleanup (7+3+2):**
  - 7 delivered plan directories deleted + plan-archive entries: complexity-routing, fix-wt-parallel-restart, phase-scoped-agents, runbook-generation-fixes, task-lifecycle, update-grounding-skill, worktree-rm-error-ux
  - 3 stuck plans fixed: inline-execute lifecycle.md → delivered, stale worktree-merge-resilience Blocker reference removed, pushback-grounding kept (active reference)
  - 2 dropped tasks restored: discuss-to-pending, wt-exit-ceremony (lost by autostrategy merge at wt-rm-dirty)
  - Root causes: (1) handoff trim lacks plan-completion ceremony (7 plans), (2) autostrategy merge drops branch-only Pending Tasks (2 tasks), (3) lifecycle.md not updated on rework completion (1 plan)
- **UPS hook error handling fix:**
  - Added stderr diagnostic on `ImportError` for `match_topics` (line 38)
  - Narrowed bare `except Exception: pass` to report error via stderr (line 1047)
  - Topic injection confirmed working — silent fallback was the bug pattern, not a runtime failure
- **agent-core lint gap identified:** ruff excludes agent-core (pyproject.toml line 44), mypy scoped to src/tests only, docformatter scoped to src/tests. Hook scripts have zero mechanical quality enforcement.
- **Unscheduled plan resolution (2 → 0):**
  - pushback-grounding: FRs 1-3 delivered to pushback.md, FR-4 superseded by directive skill promotion. Plan directory deleted, plan-archive entry written.
  - worktree-merge-resilience: Active work, task created (Tier 3 → flat list at 2.2)
- **Learnings merge validation:** All 4 post-diff3 merges validated clean. Monotonically increasing entry counts (5→12→14→17→19). 31→5 drop was intentional `/codify` (fe1ea87e), not data loss.
- **Reprioritization + tier removal:**
  - 6 new tasks scored: Directive skill promotion (1.6), Plan-completion ceremony (1.4), agent-core lint coverage (1.0), Worktree exit ceremony (1.6), Discuss-to-pending chain (1.6), Worktree merge resilience (2.2)
  - Tier headings (1-4) removed from session.md. Flat WSJF-ordered list with scores inline.
  - Score prototype parameterized: `plans/prototypes/score.py --new <file>` accepts JSON task data (file: `plans/reports/prioritization-2026-03-02b.md`)
- **Merge completed filter (TDD):**
  - Added `completed_re` filter in `_merge_session_contents` (`resolve.py:84`) — excludes `[x]` and `[–]` blocks from additive union
  - Test: `test_merge_session_filters_completed_tasks_from_theirs` in `test_worktree_merge_session_resolution.py`
  - 1430 tests pass, lint green
- **Worktree skill model homogeneity removed:**
  - Removed model tier compatibility check from Mode B parallel group detection (worktree SKILL.md)
  - Removed from execute-rule.md parallel task detection criteria
  - Worktrees are filesystem isolation — each session sets its own model at launch
- **Task absorptions:**
  - Discuss-to-pending chain → absorbed into Directive skill promotion (brief: `plans/directive-skill-promotion/brief.md`)
  - Delivery supercession → absorbed into Plan-completion ceremony (brief: `plans/plan-completion-ceremony/brief.md`)
- **Stale decision cleanup:**
  - Removed superseded single-section entry from `workflow-advanced.md` (2026-02-20) — contradicted two-section model in `operational-tooling.md` (2026-02-28)
  - Removed corresponding memory-index trigger (`/when tracking worktree tasks in session`)
- **RCA: worktree parallelization failure:**
  - Root cause chain: D-9 classification not applied retroactively → all tasks In-tree → Worktree Tasks empty → `wt` can't dispatch
  - Compounding: stale single-section decision entry loaded alongside current two-section model
  - Learning recorded: "When reclassifying tasks after structural changes"
- **Bulk reclassification + validator fix:**
  - All 63 pending `[ ]` tasks moved from In-tree to Worktree Tasks
  - New rule: main is worktree-tasks-only except trivial fixes. Plan absence doesn't qualify for in-tree.
  - Removed `check_worktree_format` from `session_structure.py` — slug requirement invalid for pre-dispatch classification
  - Deleted `TestCheckWorktreeFormat` class, updated `test_multiple_error_types` (3→2 errors)
- **Worktree setup (4 parallel):**
  - orchestrate-evolution, execute-flag-lint, skill-disclosure, session-md-validator
  - Blast zone assessed: validator removal contained, merge asymmetry amplified (pre-existing bug, larger surface)
- **Skill-disclosure worktree merged + removed**
- **Discussion: merge ceremony redesign:**
  - Insight: "merge conflict and precommit fixing belongs out of main" — branch self-updates, main rollbacks on failure
  - Worktree-merge-from-main becomes prerequisite for merge resilience (branch updates itself before merge to main)
  - Plan-completion ceremony is merge-point side-effect (like `remerge_session_md`), not branch-side or main-side — supercession needs merged state, concurrent merges invalidate branch-side checks
  - Rejected: splitting ceremony into branch-context (supercession) + main-mechanical (deletion) — supercession must check against main's actual merged state including learnings/decisions from other merged worktrees
- **Discussion: requirements-first workflow:**
  - Always start from `/requirements` unless requirement-equivalent document exists (requirements.md, design.md with behavioral FRs, deliverable review report)
  - Brief.md is NOT requirement-equivalent — context transfer without testable acceptance criteria
  - 5 tasks have `/design` commands but only brief.md: plan-completion-ceremony, directive-skill-promotion, merge-lifecycle-audit, design-context-gate, wt-rm-task-cleanup
  - Existing blocker documents this gap (line 316-317): planstate infers requirements.md template for brief-only plans
- **`w` (wrap) command definition recovered via session scraper:**
  - Tier 1 command (no colon), sequence: findings → takeaways → submit (handoff+commit)
  - Absorbed into directive-skill-promotion task
- **Active recall system architecture discussion:**
  - Recall vs RAG: keyed recall retrieves by applicability condition (when/where entry applies), not content similarity. Precision improves with model reasoning capability, not embedding quality.
  - Hierarchical index: root index → child indices → triggers. O(log_k(N)) lookup via existing tail-recursion primitive. Required for scaling beyond ~200 entries.
  - Two trigger classes: `when` (situational, project decisions, hand-curation) vs `how` (task-descriptive, reference documentation, automation-safe)
  - Three learning categories: internal decisions (user-invalidated), external environment facts (version-invalidated), hybrid (version-triggers re-evaluation, decision may survive)
  - Automated documentation conversion: sonnet + corrector pipeline for `how` entries from reference docs (Python stdlib, pytest, pydantic, click, ruff, mypy)
  - Benchmark positioning: SWE-ContextBench sixth paradigm — recall-explore-recall pattern not covered by existing 5 paradigms
  - Plan created: `plans/active-recall/brief.md`
  - Refined `tmp/active-recall.md` — corrected RAG comparison (applicability conditions vs content similarity)
- **Session-md-validator merge:**
  - 3 validator bugs fixed on main during merge (anti-pattern — should have rolled back): worktree path pattern (`.claude/worktrees/` → sibling `-wt` container), bare skill commands (`/when`, `/how`) as absolute path false positives, worktree marker pattern matching `→` in rename descriptions
  - Session.md fixes: section order (Reference Files before Next Steps), stale worktree markers removed, 3 task commands corrected (`requirements.md` → `brief.md`)
  - Worktree recovery: force-removed without checking 2 uncommitted files (data loss), recreated at merge parent for other-session recovery, re-merged recovery commit
  - 5 new tests covering validator false positives
  - Worktree removed after second merge
- **Discussion: codify-in-branch proposal rejected:**
  - Proposal: run `/codify` in a dedicated worktree, batch small worktrees on the side
  - Rejected: merge conflict risk on shared infrastructure files (decisions/, fragments/, memory-index.md) with no ordering guarantee
  - Resolution: "worktree-tasks-only" rule scopes to task classification, not interactive skill execution — `/codify` runs on main directly
  - Learning recorded: "When worktree-tasks-only appears to block maintenance skills"
- **Codify flush (33 learnings → permanent docs):**
  - 25 consolidated across 12 files: testing.md (2), implementation-notes.md (3), operational-tooling.md (2), hook-patterns.md (1), pipeline-contracts.md (2), workflow-advanced.md (5), defense-in-depth.md (2), pushback.md (2), delegation.md (2), project-tooling.md (1), execute-rule.md (2), communication.md (1)
  - 5 already-codified entries removed (proximal requirements, delegating TDD, pipeline skills, precommit cost, deliverable review)
  - 1 codify-specific learning routed to `.claude/skills/codify/references/learnings.md`
  - 20 memory-index entries added
  - 3 learnings retained for continuity (codify branch, recovery context, worktree-tasks-only)
  - learnings.md: 157 → 23 lines
  - User correction applied: lint-gated recall entry in defense-in-depth.md updated to PreToolUse-hook-blocks-until-agent-recalls model (agent does semantic matching)
- **Worktree batch dispatch (7 parallel):**
  - session-scraping, worktree-merge-from-main, handoff-commit-removal, explore-anthropic-plugins, wt-ls-session-ordering, recall-tool-consolidation, active-recall-system
  - Skill caching confirmed: loaded worktree SKILL.md had stale model-tier filter (already removed on disk), caused sonnet-only batch excluding opus tasks

## In-tree Tasks

## Worktree Tasks

### Batch: workflow quick wins (prose-only / low code, parallelizable)

- [ ] **Agentic prose terminology** — find/replace "LLM prose" variants → "agentic prose" across codebase | haiku | 1.3
- [ ] **Memory-index loading docs** — update stale refs claiming memory-index is @-ref from CLAUDE.md | haiku | 1.2
- [ ] **Wt merge-rm shorthand** — prose edit: `wt merge rm <slug>` shorthand in worktree SKILL.md | haiku | 1.2
- [ ] **Corrector removal audit** — decision entry: corrector must verify removal covers all callers | sonnet | 1.2
- [ ] **Runbook outline review** — prose edit: user review gate after outline correction in runbook SKILL.md | haiku | 1.1
- [ ] **Review auto-commit** — prose edit: auto handoff+commit after deliverable-review fixes | haiku | 1.1
- [ ] **Task notation migration** — replace `[✗]` → `[†]` across active behavioral files + validators | haiku | 0.8
- [ ] **Discuss divergent step** — `/design plans/discuss-divergent-thinking/brief.md` | sonnet
  - Plan: discuss-divergent-thinking
  - Add alternative-framing step to d: directive before assessment
- [ ] **Settings triage protocol** — `/design plans/settings-triage-protocol/brief.md` | sonnet
  - Plan: settings-triage-protocol
  - Commit skill triage step for settings.local.json entries
- [ ] **Standardize task creation** — `/design plans/standardize-task-creation/requirements.md` | sonnet
  - Plan: standardize-task-creation
  - Skills write follow-up tasks to session.md with skill invocation commands
- [ ] **Command lint gate** — precommit lint: scan backtick commands in task entries for executability | haiku

### Active / ready

- [ ] **Active Recall** — `/requirements plans/active-recall/brief.md` | opus
  - Plan: active-recall
  - Hierarchical index, automated documentation conversion, memory format grounding
  - Relates to: recall tool consolidation, generate memory index, recall dedup, recall pipeline, recall learnings design
- [ ] **Worktree merge resilience** — `/runbook plans/worktree-merge-resilience/outline.md` | sonnet | 2.2
  - Plan: worktree-merge-resilience | Status: outlined
  - Segment-level diff3 merge for learnings.md, precommit structural validation
- [ ] **Tool deviation hook** — PostToolUse hook: agents declare expected Bash outcome, hook validates actual vs declared | sonnet | 1.9
  - General framework: agent declares expected exit code + output pattern before Bash call
  - PostToolUse hook compares actual result, stops or redirects to diagnose-and-compensate on mismatch
- [ ] **Artifact staleness gate** — sonnet | 1.9
  - Mechanical checkpoint at /requirements, /design, /runbook exit points
  - `claudeutils _recall resolve` touches sentinel; skill compares sentinel mtime to recall-artifact.md AND primary skill artifact
  - Two drift vectors: stale recall-artifact and stale skill artifacts
- [ ] **Lint-gated recall** — PostToolUse hook: inject memory-index on first lint/precommit red after green (state-transition gated) | sonnet | 1.9
- [ ] **Lint recall gate** — PreToolUse recall pass before lint fix attempt; depends on when-resolve null mode | sonnet | 1.9
- [ ] **Ground workflow skills** — `/ground` each per audit | opus | 1.9
  - Audit: `plans/reports/workflow-grounding-audit.md`
  - Priority: /runbook → review agents → /orchestrate → /handoff
- [ ] **Markdown migration** — `/design` | opus | 1.9
  - Wrap existing markdown parser with Claude-specific lenient normalization
  - Line-wrap all files, replace ad-hoc regex parsers
  - Token counting API + sqlite user cache, threshold migration (line counts → tokens)
- [ ] **Merge lifecycle audit** — `/design plans/merge-lifecycle-audit/brief.md` | sonnet | 1.8
  - Plan: merge-lifecycle-audit | Status: requirements
  - State machine audit + integration tests for merge→rm lifecycle. Absorbs merge-submodule-ordering.
- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet | 1.8
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [ ] **Block cd-chaining in bash** — PreToolUse hook to block `cd * && *` and `cd *; *`, recommend `git -C` or subshell | sonnet | 1.8
- [ ] **Fix task-context bloat** — Filter/trim output | sonnet | 1.7
- [ ] **Skill-dev skill** — `/design` | sonnet | 1.6
  - Front-load plugin-dev:skill-development with project-specific skill editing patterns
  - Replace ambient `.claude/rules/skill-development.md` path trigger with explicit skill invocation
- [ ] **Directive skill promotion** — `/design plans/directive-skill-promotion/` | opus | 1.6
  - Plan: directive-skill-promotion
  - d:, p:, w directives have prose-gate failures (grounding skip, model misclassification)
  - Absorbs: wrap command, discuss protocol grounding, p: classification gap, discuss-to-pending chain
- [ ] **Entry gate propagation** — `/design` | opus | 1.6
  - Add git-clean + precommit entry gates to /orchestrate, /deliverable-review, corrector agent
  - Follow-on after /inline delivery
- [ ] **Retrofit skill pre-work** — `/design` | opus | 1.6
  - Many skills lack initial task context loading (task-context.sh, brief.md, recall-artifact) and skill-adapted recall
  - Follow-on after /inline delivery
- [ ] **Worktree exit ceremony** — `/requirements plans/wt-exit-ceremony/brief.md` | sonnet | 1.6
  - Plan: wt-exit-ceremony | Status: requirements
  - Two UPS Tier 1 shortcuts (k/ok, g/go) + worktree lifecycle behavior codification
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet | 1.6
  - Plan: tweakcc
- [ ] **Wt rm task cleanup** — `/design plans/wt-rm-task-cleanup/brief.md` | sonnet | 1.6
  - Plan: wt-rm-task-cleanup | Status: requirements
  - rm removes completed task entry (branch `[x]` check), strips marker only if not completed
- [ ] **Worktree ad-hoc task** — `/design plans/worktree-ad-hoc-task/requirements.md` | sonnet | 1.6
  - Plan: worktree-ad-hoc-task | Status: requirements
  - Add task to session.md before `_worktree new` when task not yet present
- [ ] **Plugin migration** — Refresh outline then orchestrate | opus | 1.6
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
- [ ] **Remove wt rm --force** — remove `--force` flag from `_worktree rm` CLI | sonnet | 1.5
- [ ] **Design context gate** — `/design plans/design-context-gate/brief.md` | sonnet | 1.5
  - Plan: design-context-gate | Status: requirements
  - /design tail-call /inline only when context budget allows, otherwise handoff+commit
- [ ] **Plan-completion ceremony** — `/design plans/plan-completion-ceremony/` | opus | 1.4
  - Plan: plan-completion-ceremony
  - Handoff trim lacks plan-completion side effects (delete dir, archive entry, lifecycle.md, stale refs)
  - Absorbs: Delivery supercession
- [ ] **Generate memory index** — `/design` | opus | 1.4
  - Each decision/learning declares keywords for index. Generated from declarations.
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet | 1.4
- [ ] **Tier threshold grounding** — calibrate Tier 1/2/3 file-count thresholds against empirical data | opus | 1.4
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet | 1.3
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet | 1.3
- [ ] **Cross-tree requirements** — `/requirements` skill writes to main from worktree | sonnet | 1.3
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Absorbs: Revert cross-tree sandbox access
- [ ] **Codify branch awareness** — `/design` | opus
  - Add feature-branch gate to `/codify` + soft-limit age calculation
- [ ] **Update prioritize skill** — Phase 2: integrate as `claudeutils _prioritize score` CLI command | sonnet | 1.0
  - Phase 1 complete: prototype rewritten (JSON stdin, validation), SKILL.md updated
  - Phase 2: Click group, pyproject.toml wiring, tests, replace prototype path in SKILL.md
  - JSON input for scores, markdown output for reports. Absorbs: Prioritize script (0.7)
- [ ] **Worktree CLI UX** — sonnet | 1.0
  - `_worktree new`: stdout-only, user-friendly errors instead of tracebacks
  - `_worktree rm` dirty message improvement
- [ ] **Recall deduplication** — integrate session context scraping into `claudeutils _recall resolve` | sonnet | 1.0
- [ ] **Recall pipeline** — `d:` recall-artifact stdin format parsing, session log dedup | opus | 1.0
- [ ] **Recall usage scoring** — Post-resolve relevance scoring at skill transitions | sonnet | 1.0
- [ ] **Compensate-continue skill** — `/ground` then `/design` | opus | 1.0
- [ ] **Skill prompt-composer** — migrate skill authoring to use prompt-composer pattern | sonnet | 1.0
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus | 1.0
- [ ] **Decision drift audit** — audit decision files for stale operational assumptions | sonnet | 1.0
- [ ] **agent-core lint coverage** — `/design` | opus | 1.0
  - ruff excludes agent-core, mypy/docformatter scoped to src/tests only
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet | 1.0
- [ ] **Registry cache to tmp** — inline | sonnet | 1.0
  - Move continuation registry cache from TMPDIR to project-local tmp/
- [ ] **Merge lock retry** — add lock-contention retry to `claudeutils _worktree merge` | sonnet | 0.9
- [ ] **Diagnose compression loss** — RCA against commit `0418cedb` | sonnet | 0.9
- [ ] **Test diamond migration** — Needs scoping | sonnet | 0.9
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus | 0.9
- [ ] **Recall learnings design** — `d:` whether learnings.md entries should be resolvable via recall | opus | 0.9
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet | 0.9
  - Plan: prototypes
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus | 0.8
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet | 0.7
- [ ] **Cache expiration** — Debug log token metrics, measure TTL | sonnet | 0.7
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart | 0.6
- [ ] **Prose gate terminology** — Find proper name for D+B pattern, ground, update docs | opus | 0.5
- [ ] **Ground state coverage** — State coverage validation research | opus | 0.5
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus | 0.5
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus | 0.4
- [ ] **Wt new --base submodule** — `_worktree new --base` doesn't resolve agent-core to branch commit | sonnet
  - Requires TDD: write test, then fix
- [ ] **Retrospective materials** — `/design plans/retrospective/requirements.md` | opus
  - Plan: retrospective
  - Scrape session logs + git history for blog post raw materials on ddaa.net
- [ ] **Corrector audit** — audit 5 review-class agents for false positive evidence, add "Do NOT Flag" sections | sonnet
- [ ] **Cross-tree test sentinel** — replace mtime sentinel with content-hash in user-global cache database | sonnet
- [ ] **Design decomposition tier** — Encode decomposition methodology into `/design` as new tier | opus | restart

### Blocked / terminal

- [!] **Session CLI tool** — `/runbook plans/handoff-cli-tool/outline.md` | sonnet
  - Plan: handoff-cli-tool | Status: outlined
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration
- [ ] **Python hook ordering fix** — `/design plans/precommit-python3-redirect/requirements.md` | haiku | restart
- [-] **Calibrate topic params** — extend session-scraper.py | sonnet
  - Was blocked by UPS topic injection — now removed. Task may be moot.
- [-] **Recall tool consolidation** — absorbed into Active Recall | sonnet | 1.9
- [-] **Execute flag lint** — superseded by session validator | haiku | 3.0
- [x] **Remove UPS topics** — haiku | restart
- [x] **Orchestrate evolution** — sonnet | restart | 6.0
- [x] **Skill disclosure** — opus | 2.6
- [x] **Session.md validator** — sonnet | 2.4
- [x] **Session scraping** — sonnet | 2.2
- [x] **Worktree merge from main** — sonnet | 2.2
- [x] **Handoff --commit removal** — sonnet | 2.2
- [x] **Explore Anthropic plugins** — sonnet | restart | 2.0
- [x] **Wt ls session ordering** — sonnet | 2.0

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Post-merge validation (permanent):**
- After every worktree merge, validate session.md (pending tasks from branch carried over) AND learnings.md (no entries lost from either side)
- Known failure modes: autostrategy drops branch pending tasks, orphaned duplicate lines in append-only files, branch overwrites main-only learnings entries
- Not automated — manual check required

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

**`_worktree rm` amend restored but task entry persists:**
- `_update_session_and_amend` restored after task-classification regression. Amend works but `remove_slug_marker` only strips marker — doesn't remove completed task entry. Pending: wt-rm-task-cleanup (check branch `[x]` status).

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

**Main is worktree-tasks-only:**
- Only trivial fixes belong in In-tree. Plan absence doesn't qualify for in-tree.

- Encoded project paths use `-` for `/`, but real dashes in directory names are indistinguishable. Acceptable for prototype; production would need a different approach. [from: session-scraping]
- Task name "Remove UPS topic injection" exceeds 25-char limit (26 chars) — from worktree setup [from: rm-ups-topic]
- session.md H1 header format mismatch — now fixed by this handoff [from: rm-ups-topic]
- Retrospective needs to scan across ~90 worktree project directories (each gets its own `~/.claude/projects/` entry) [from: retrospective]
- Prototype's `scan --prefix` filters by prefix but retrospective needs multiple prefixes per topic [from: retrospective]
- May need prototype extension (requires separate `/requirements` per C-1) [from: retrospective]
## Reference Files

- `plans/reports/workflow-grounding-audit.md` — Grounding provenance for all workflow skills/agents
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-03-02b.md` — WSJF scoring, 79 tasks ranked, flat ordering (supersedes 2026-03-02)
- `plans/skill-progressive-disclosure/brief.md` — Segment loading at gate boundaries (/design and /runbook)
- `plans/reports/design-skill-grounding.md` — Design skill grounding (updated with session empirical data)
- `agents/decisions/pipeline-contracts.md` — Pipeline contract decision file (new)
- `plans/reports/recall-lifecycle-grounding.md` — Grounded recall artifact lifecycle (3 patterns, per-point mode assignments, mode reduction)
- `plans/reports/recall-lifecycle-internal-codebase.md` — Internal inventory: recall-artifact handling across all pipeline skills
- `plans/reports/recall-lifecycle-external-research.md` — External research: 10 frameworks (HL7 CRMI, PROV-DM, OpenLineage, ADK, LangGraph, etc.)
- `plans/worktree-ad-hoc-task/requirements.md` — Add task to session.md before worktree creation when absent
- `plans/wt-rm-task-cleanup/brief.md` — rm removes completed task entry (branch `[x]` check)
- `plans/merge-lifecycle-audit/brief.md` — State machine audit for merge→rm lifecycle (absorbs merge-submodule-ordering)
- `plans/active-recall/brief.md` — Active recall system: hierarchical index, documentation conversion, trigger classes, invalidation
- `tmp/active-recall.md` — Discussion decisions: recall-explore-recall, tree navigation, benchmark landscape

## Next Steps

3 worktrees active: active-recall-system, discuss, retrospective. Continue worktree sessions.