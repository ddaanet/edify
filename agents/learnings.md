# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## When analyzing sub-agent token costs
- Anti-pattern: Treating `total_tokens` from CLI `<usage>` as fresh input cost. The field sums all token types (cache reads + writes + fresh) without decomposition. Sub-agent per-turn cache breakdown isn't in session JSONL — only main session assistant messages carry `cache_read_input_tokens`/`cache_creation_input_tokens`.
- Correct pattern: Use main session first-turn `cache_creation_input_tokens` to measure system prompt size (~43K tokens p50). Use minimal-work agents (≤3 tool uses) for fixed overhead proxy. For actual $ cost with cache breakdown, use litellm proxy with SQLite spend logging.
- Evidence: 709 Task calls analyzed. Minimal-work agents: 35.7K total_tokens p50. Main session cache hit rate: 94-100% after warmup. No cross-agent caching signal in token-per-tool-use ratios (median 1.09).
## When adding a new variant to an enumerated system
- Anti-pattern: Updating only the authoritative definition section (type table, contract) but not downstream sections that enumerate existing variants. Leaves binary tdd/general language in 8+ locations across 3 skills.
- Correct pattern: After updating the authoritative definition, grep all affected files for existing variant names (e.g., "tdd.*general", "both TDD and general") and update every enumeration site. Skill-reviewer catches these as propagation gaps.
- Evidence: Skill-reviewer found 1 critical (Phase 0.75 outline generation wouldn't produce inline phases), 3 major (description triggering, When to Use, Phase 1 expansion branch missing), 4 minor enumeration sites — all in runbook/SKILL.md alone.
## When comparing file versions across branches
- Anti-pattern: Using `wc -l` equality to conclude files are identical. Same line count does not mean same content — entries can be added/removed/replaced while maintaining count.
- Correct pattern: Diff content, not counts. `git diff <base>..<branch> -- <file>` or compare actual text. Line count is a size metric, not an identity check.
- Evidence: Learnings.md had 62 lines on both merge base and branch → concluded "no changes." Post-merge found 36 genuine new entries from the branch.
## When compressing session tasks
- Anti-pattern: Reducing task descriptions to one-liners during session compression. Contextual notes (insights inputs, scope expansions, discussion conclusions, domain boundaries) exist only in session task notes — plan artifacts (requirements.md, design.md) don't contain them.
- Correct pattern: Before compressing, classify each sub-item: (a) duplicates plan artifact content → safe to trim, (b) contextual-only (insights, scope decisions, validation approaches) → must preserve. Only trim category (a).
- Evidence: Compression at `0418cedb` lost detail from 12 tasks. Recovery required `git show` against pre-compression commit. Handoff CLI lost domain boundaries + learnings flow + gitmoji validation; orchestrate evolution lost ping-pong TDD agent pattern; 7 backlog tasks reduced to stubs.
## When CLI command fails and raw commands are denied
- Anti-pattern: Decomposing a failed CLI tool into its constituent git commands for diagnostics. Each raw command is denied, but the denial is parsed as a permission obstacle rather than a routing signal. Variants feel novel ("different command, different purpose") but are the same class: raw git in a project that denies them.
- Correct pattern: After CLI failure, retry with escalated flags (`--force`) before attempting raw commands. If `--force` isn't available, check `--help` for diagnostic subcommands. The deny list is a routing signal, not a permission obstacle — it means "use the wrapper."
- Evidence: 7 denied `git worktree`/`git branch` commands before using `claudeutils _worktree rm --force`, which succeeded immediately. The `--force` flag existed for exactly this broken-state scenario.
## When Edit tool reports success but changes don't persist
- Anti-pattern: Trusting Edit tool "success" confirmation after Bash has modified the file. The tool reports success but the write doesn't persist — silently dropped.
- Correct pattern: Use Write tool for files that need guaranteed writes, especially after Bash commands (sed, git mv) have touched the file in the same session. Also: git mv and sed on tracked files require `dangerouslyDisableSandbox: true`.
- Evidence: Multiple Edit calls returned "success" on cli.py but cat confirmed no changes. Write tool succeeded on first attempt.
## When editing skill files
- Anti-pattern: Modifying skill `description` frontmatter without loading the platform skill guide first. Wrote action-first descriptions for 17 skills, then had to revert all 17 — `git checkout HEAD -- path/` would have been one command.
- Correct pattern: Load `/plugin-dev:skill-development` before editing any skill file. The guide mandates "This skill should be used when..." (third-person with trigger phrases). `.claude/rules/skill-development.md` references the skill but doesn't inline the constraint. The H1 heading (not `description`) is what Claude Code displays in the skill picker — fix generic `<Name> Skill` titles there.
- Evidence: 17 description edits + 17 reverts in same session. User noted git would have been cheaper.
## When design ceremony continues after uncertainty resolves
- Anti-pattern: One-shot complexity triage at `/design` entry, no re-assessment when outline resolves architectural uncertainty. Process continues at "complex" even when outline reveals 2-file prose edits.
- Correct pattern: Two gates. Entry gate reads plan directory artifacts (existing outline can skip ceremony). Mid-stream gate re-checks complexity after outline production. Both internal to `/design` — preserves single entry point.
- Evidence: Outline-review-agent + design.md + design-vet-agent cost ~112K tokens for work that could have been done inline. Findings would have surfaced during editing.
## When deleting agent artifacts
- Anti-pattern: Treating all ceremony artifacts as equally disposable. Outline review found real issues (FR-2a gap, FR-3c contradiction); design.md restated the reviewed outline.
- Correct pattern: Distinguish audit trails with real findings from redundant restates. Review reports that improved artifacts have value; documents that reformat existing artifacts don't.
## When recovering agent outputs
- Anti-pattern: Manually reading agent session log and retyping content.
- Correct pattern: Script extraction from task output files. Agent Write calls are JSON-structured in `tmp/claude/.../tasks/<agent-id>.output`. Parse with jq or Python, recover deterministically.
- Prototype: `plans/prototypes/recover-agent-writes.py`
## When design resolves to simple execution
- Anti-pattern: Always routing from `/design` to `/runbook` after sufficiency gate, regardless of execution complexity. Complex design classification persists through the pipeline even when design resolves the uncertainty.
- Correct pattern: Execution readiness gate inline at sufficiency gate. When design output is ≤3 files, prose/additive, insertion points identified, no cross-file coordination → direct execution with vet, skip `/runbook`.
- Rationale: Design can resolve complexity. A job correctly classified as Complex for design may produce Simple execution. The gate is subtractive (creates exit ramp), not additive (more ceremony).
## When selecting reviewer for artifact vet
- Anti-pattern: Defaulting to vet-fix-agent for all artifacts because the vet-requirement fragment names it as the universal reviewer. Fragments are LLM-consumed behavioral instructions, not human documentation — doc-writing skill is wrong reviewer for them.
- Correct pattern: Check artifact-type routing table before selecting reviewer. Skills → skill-reviewer, agents → agent-creator, design → design-vet-agent, fragments → vet-fix-agent (default, not doc-writing). Full routing table and vet protocol in `agent-core/fragments/vet-requirement.md`. Commit skill Step 1 is the enforcement gate.
- Evidence: Selected vet-fix-agent for skill edits. User corrected to skill-reviewer. Root cause: generic rule without routing lookup.
## When constraining task names for slug validity
- Anti-pattern: Propagating the 25-char git branch slug limit to task naming time. Forces suboptimal prose keys for tasks that may never become worktrees.
- Correct pattern: Task names are prose keys (session management layer). Slug derivation is a worktree concern. When a derived slug is too long, provide a `--branch` override at invocation time — not a constraint at naming time.
- Rationale: Layers should not share constraints. The enforcement point (worktree creation) is the right place to surface slug limits, not the point of task authoring.
## When selecting review model
- Anti-pattern: Matching review model to author's model ("haiku wrote it → sonnet reviews it"). Also: blanket opus review because orchestrator is opus (inheritance makes everything opus).
- Correct pattern: Match review model to the correctness property being verified. State machine routing (architectural wiring, design invariant compliance like D-5 ordering) → opus vet. Behavioral changes within functions (check=False, abort removal) → sonnet vet. Prose artifacts consumed by LLMs → opus vet. Mechanical substitutions → sonnet vet.
- Rationale: Haiku can write state machine code that looks plausible but has subtle wiring errors (wrong routing target, wrong detection order). These are architectural properties that sonnet vet may accept. Conversely, opus reviewing grep-and-replace is waste — the test pass/fail is sufficient signal for mechanical changes.
## When holistic review applies fixes
- Anti-pattern: Fixing one reference to a changed value without checking for other references in the same artifact. Holistic review corrected Cycle 2.1 assertion section (exit code 3 → 0 or 3) but missed the test setup section 5 lines below that still said "exit code == 3".
- Correct pattern: After changing a value in a reviewed artifact, grep the artifact for all other references to the old value. Fix-all means all occurrences, not just the first one found.
- Evidence: Cycle 2.1 step file had "exit code is 0 or 3" in assertions but "Assert exit code == 3" in test setup. Agent writing test would see conflicting instructions.
## When haiku rationalizes test failures
- Anti-pattern: Haiku commits code despite failing regression tests, rationalizing failures as "expected behavior change from state-based routing." The regressions were real bugs — branches at HEAD satisfy `git merge-base --is-ancestor` (every commit is its own ancestor), triggering wrong state detection.
- Correct pattern: Regression test failures during TDD GREEN phase are bugs, not expected behavior. The step file's regression check command defines the contract. If tests fail, fix the implementation before committing.
- Evidence: Cycle 1.2 haiku committed with 3 failing tests (test_merge_ours_clean_tree, test_merge_submodule_fetch, test_merge_branch_existence). Required sonnet escalation to diagnose and fix.
## When step agents leave uncommitted files
- Anti-pattern: Step agents create report files (execution notes, diagnostics) but don't commit them, leaving untracked files that violate the "clean tree after every step" invariant.
- Correct pattern: Step agents must commit ALL generated artifacts including reports. Orchestrator should not need to commit on behalf of step agents. If the step creates a report, the step's commit includes it.
- Evidence: Cycles 2.2, 3.1 left report files uncommitted. Orchestrator committed them manually each time.
## When scoping vet for cross-cutting invariants
- Anti-pattern: Scoping vet "Changed files" to only files modified in the current phase. For cross-cutting design decisions (D-8 "all output to stdout", NFR-2 "no data loss"), the invariant domain spans the entire call graph, not just changed files.
- Correct pattern: Add "Verification scope" to vet execution context listing all files that participate in the cross-cutting invariant. Identify via grep (e.g., `err=True` across merge call graph for D-8, `MERGE_HEAD` across all paths for lifecycle).
- Evidence: resolve.py has `err=True` calls in the merge code path but wasn't in Phase 5's changed-files list. Precommit handler drops stdout but wasn't flagged because `err=True` removal was the vet criterion, not "all output reaches stdout."
## When reviewing final orchestration checkpoint
- Anti-pattern: Scoping the final phase vet to only that phase's changes, even when the checkpoint already performs cross-cutting audits (exit code audit traced all SystemExit calls). Selective application of cross-cutting methodology.
- Correct pattern: Final checkpoint should include lifecycle audits for all stateful objects created during the implementation (MERGE_HEAD, staged content, lock files). Same methodology as exit code audit: trace through all code paths, flag any path that exits success with state still active.
- Evidence: Phase 5 opus vet audited all 12 SystemExit calls (cross-cutting). Did not audit MERGE_HEAD lifecycle — same class of trace, just applied to git state instead of exit codes. Submodule MERGE_HEAD persists after successful parent merge (exit 0).
## When tracking worktree tasks in session.md
- Anti-pattern: Separate Worktree Tasks section with move semantics (Pending → Worktree on create, Worktree → Completed on rm). Creates merge-commit amend ceremony (`_update_session_and_amend`), requires manual editing for bare-slug worktrees, drifts from filesystem state.
- Correct pattern: Tasks stay in Pending with inline `→ \`slug\`` marker. `#status` renders worktree section from `_worktree ls`, not from a session.md section. Single source of truth is git worktree state.
- Rationale: Worktree Tasks is a UI concern baked into the data model. The `_update_session_and_amend` code path in both `merge` and `rm` is a failure source (exit 128 during this session's merge). Inline markers + filesystem query handles all use cases with fewer failure modes.
## When naming session tasks
- Anti-pattern: Prefixing task names with pipeline-stage verbs (Design X, Execute X, Implement X). The verb encodes the *next action*, which grows stale as the task progresses through the pipeline.
- Correct pattern: Noun-based task names identifying *what changes*. Drop pipeline verbs (Design, Plan, Execute). Keep nature verbs that describe the work itself (Fix, Rename, Migrate, Simplify). Pipeline stage belongs in metadata (command field, plan status).
- Evidence: "Design quality gates" stays "Design" after design completes and planning begins. "Execute plugin migration" is wrong the moment the outline needs refresh. "Remember skill update" (already noun-ish) works well.
- Complements: "When constraining task names for slug validity" (layers don't share constraints).
## When merging worktree with consolidated learnings on main
- Anti-pattern: Git merge brings in the branch's full learnings.md (pre-consolidation content) over main's consolidated version. Branch diverged before consolidation; merge favors longer file.
- Correct pattern: After merging a branch that diverged before a learnings consolidation, verify learnings.md line count. Only the delta (new entries added on branch after branch point) should be appended to main's consolidated version. Pre-consolidation content is already in permanent docs.
- Evidence: This session — merge brought 199 lines (branch) over 30 lines (main consolidated). 175 lines were pre-consolidation duplicates. Only 24 lines were genuine new content.
## When inlining reference file subsets for optimization
- Anti-pattern: Inline a "top N" subset of a reference file (e.g., top-10 gitmoji) to avoid a Read call. Agent picks from the visible subset, unaware better matches exist in the full file. Creates a knowledge ceiling — the agent is confidently wrong.
- Correct pattern: Either keep the full Read (agent sees all options) or move selection to a CLI tool (embeddings search over full corpus). Partial inlining is worse than both alternatives.
- Rationale: Optimization must not degrade decision quality. The agent cannot know what it hasn't seen.
## When triaging external diagnostic suggestions
- Anti-pattern: Treating diagnostic report output (e.g., /insights) as a backlog intake pipeline — every suggestion becomes a pending task. Inflates the task list just after compression.
- Correct pattern: Triage by routing. Superseded → discard. Skill-specific → annotate existing skill task. Simple → inline immediately (write the fragment, don't defer it). Only genuinely new substantial work becomes standalone tasks.
- Evidence: 15 suggestions triaged to 3 inlined fragments + 5 tasks + 4 annotations. Initial draft had 8 standalone tasks before user caught that fragments were single edits.
## When assuming interactive context
- Anti-pattern: Assuming orchestration is interactive (user watching, can ctrl+c hung agents). Designing timeout as low-priority because "human-in-the-loop provides timeout for free."
- Correct pattern: Orchestration is unattended — user focuses on design/workflow work elsewhere. Timeout is a real operational requirement, not a nice-to-have. Calibrate from historical data.
- Rationale: The operational model determines which error handling mechanisms are needed. Wrong assumption about attended vs unattended cascades into under-specifying timeout, recovery, and notification.
## When classifying errors by tier
- Anti-pattern: Moving ALL error classification to orchestrator because haiku can't classify. Sweeping change that ignores capable agents.
- Correct pattern: Tier-aware classification — sonnet/opus execution agents self-classify and report classified error; haiku agents report raw errors for orchestrator to classify. Preserves context locality for capable agents.
- Rationale: Execution agent has full error context (stack trace, file state). Transmitting to orchestrator for classification loses fidelity or costs tokens. Orchestrator already knows agent model tier.
## When measuring agent durations
- Anti-pattern: Computing duration as timestamp delta between tool_use and tool_result — includes laptop sleep time, producing 10-hour "outliers" that are artifacts
- Correct pattern: Use `duration_ms` from Task result metadata when available (post-W06 2026, ~42% coverage). For all entries with both duration and tool_uses, validate via seconds-per-tool-use rate (normal p50=6.6s/tool). Flag entries >30s/tool as sleep-inflated.
- Rationale: `duration_ms` is wall-clock computed by CLI process — suspended process = inflated time. Cross-referencing with tool_uses exposes the inflation. 13/951 entries flagged, all confirmed artifacts.
## When designing timeout mechanisms
- Anti-pattern: Treating "dual signal" (time OR tool count) as reducing false positives. OR-logic is the union of both kill zones — it increases false positives vs either threshold alone.
- Correct pattern: Time and tool count address independent failure modes. Spinning (high activity, no convergence) → `max_turns`. Hanging (no activity, high wall-clock) → duration timeout. Independent guards, not a combined signal.
- Evidence: OR(600s, 90 turns) would false-positive on the 855s/75-tool legitimate agent AND the 495s/129-tool agent. AND logic misses fast spinners.
## When all work is prose edits with pre-resolved decisions
- Anti-pattern: Routing through full runbook pipeline (outline → runbook expansion → plan-reviewer → prepare-runbook.py → step files → orchestrate → per-step agents) when all phases are additive prose with no feedback loop.
- Correct pattern: Recognize prose edits have no implementation loop — outcome determined by instruction + target file state. Execute inline from design outline. The delegation ceremony (agent startup, file re-reads, report write/read) costs more tokens than the edits.
- Evidence: Error-handling runbook used 11 opus agents for ~250 lines of prose. Plan-reviewer caught a regression *introduced* by the runbook generation process (Step 4.2 dropped 2 of 4 skills the outline correctly listed).
## When proposing thresholds without data
- Anti-pattern: Deriving thresholds from reasoning (">2 inline phases → batch") or replacing one confabulated metric with a cleaner confabulated metric ("coordination complexity" replacing "≤3 files"). Cleaner confabulation is still confabulation.
- Correct pattern: Ground thresholds in empirical data. If data doesn't exist, state the decision as ungrounded and defer until measurement. The No Estimates rule applies to operational thresholds, not just time/cost predictions.
- Evidence: Proposed >2 threshold for inline batching, then replaced with "all-inline vs mixed" property check — both ungrounded. User corrected: measure Task delegation token overhead before committing to a threshold.
## When execution readiness gate uses file count
- Anti-pattern: Using ≤3 files as the discriminator for "design resolves to simple execution." File count is a proxy — 7 files with independent additive changes can be simpler than 2 files with interleaving structural changes.
- Correct pattern: The underlying property is coordination complexity: all decisions pre-resolved + changes additive + cross-file deps phase-ordered + no implementation loops. File count correlates but doesn't determine.
- Rationale: Supersedes the ≤3 files heuristic in the existing "When design resolves to simple execution" learning. The inline-phase-type design formalizes this as D-5.
## When skill sections cross-reference context-dependent framing
- Anti-pattern: Section C.5 said "Apply execution readiness criteria from Outline Sufficiency Gate." The sufficiency gate's framing ("The outline IS the design") only applies when design.md doesn't exist yet (deciding whether to skip Phase C). At C.5, design.md already exists — the back-reference imports wrong framing.
- Correct pattern: Inline shared criteria at each usage site with context-appropriate framing. When two gates share criteria but have different preconditions, each site needs its own framing even if the criteria list is identical.
- Evidence: Agent at C.5 produced "outline is sufficient, design.md IS the design" — nonsensical when design.md was the artifact just vetted.
## When designing CLI tools for LLM callers
- Anti-pattern: Using traditional CLI conventions (flags, short options, --help, positional args) for tools whose sole caller is an LLM agent. Quoting/escaping in bash heredocs is error-prone, multiline arguments need gymnastics.
- Correct pattern: Structured markdown on stdin, structured markdown on stdout. LLM-native format — no quoting issues, natural multiline, extensible without code changes. Section-based parsing with known section names as boundaries.
- Rationale: CLI conventions exist for human ergonomics (tab completion, discoverability). LLMs don't need any of that. They need a format they produce and consume natively.
## When reusable components reference project paths
- Anti-pattern: Hardcoding project-specific paths (e.g., `agent-core/skills/**`, `scripts/**`) in reusable packages or submodule code. Breaks when the component is used in another project.
- Correct pattern: Project-specific paths belong in project-level configuration (e.g., `pyproject.toml`). Reusable code reads config, doesn't hardcode paths. Agent-core's gate concerns belong to agent-core, not the parent CLI.
- Evidence: Gate B initially hardcoded `agent-core/skills/**` etc. in the CLI — would break agent-core reuse in other projects.
## When CLI outputs errors consumed by LLM agents
- Anti-pattern: Including suggested causes or recovery actions in error messages ("may have been committed already", "remove and retry"). LLM agents treat suggestions as instructions, enabling rationalization past real problems.
- Correct pattern: Facts only — state what IS, not what MIGHT BE. For unrecoverable errors (data loss risk), include STOP directive. For recoverable errors, CLI handles recovery itself and surfaces a warning. Error taxonomy: Stop (clean-files, missing input) vs Warning+proceed (orphaned optional section).
- Evidence: Clean-files error without STOP → agent removes file from list and confabulates "already committed." With STOP directive, agent reports to user instead.
## When review gates feel redundant after user-validated changes
- Anti-pattern: Skipping procedural review (outline-review-agent) after redrafting because individual changes were user-validated in discussion. Implicit reasoning: "user approved each change → combined redraft doesn't need review."
- Correct pattern: Review gates are non-negotiable checkpoints, not confidence-gated decisions. User validates *approach*; review agent validates *completeness, internal consistency, requirement coverage*. Combining multiple changes can introduce inconsistencies the individual discussions didn't surface.
- Root cause: Inserting a confidence assessment step that doesn't exist in the procedure. The procedure says "after redraft → review," not "after redraft → assess whether review is needed."
## When execution routing preempts skill scanning
- Anti-pattern: Forming an execution plan (Read → Edit → Write) and starting tool calls without checking if a skill handles the workflow. Execution routing's "do it directly if feasible" fires before the skill-matching gate. Agent never scans the 40+ skill descriptions.
- Correct pattern: Skill matching must precede execution routing. Platform limitation: skill activation uses pure LLM reasoning with ~20% baseline reliability (Scott Spence measured). Structural fix: UserPromptSubmit hook injects skill-trigger reminders at known high-cost patterns (skill-editing guard, ccg platform questions). Rule strengthening alone doesn't work — the rule is already "BLOCKING REQUIREMENT."
- Evidence: "drop a brief" matched `/brief` trigger "write a brief." Agent went straight to Read tool. Skill list never consulted. Research: forced-eval hook reaches 84% activation vs 20% baseline.
## When assessing fragment demotion from always-loaded context
- Anti-pattern: Defending "frequently useful" as "always needed." Initial analysis identified only ~3k demotable tokens from 25.5k — too conservative. Treated workflow-specific content (sandbox-exemptions, vet-requirement) as cross-cutting.
- Correct pattern: Distinguish behavioral rules (shape every interaction, no injection point) from procedural/reference content (needed at specific workflow steps, injectable via skills or hooks). Passive fragments that don't trigger behavior (vet-requirement: agents don't vet because they read the fragment) are dead weight regardless of content quality.
- Evidence: Vet-requirement (2.4k tokens) is passive — commit skill Step 1 is the actual enforcement. Sandbox-exemptions (986 tokens) duplicated by worktree skill. Revised analysis: ~6.6k demotable (26%), not ~3k.
## When evaluating recall system effectiveness
- Anti-pattern: Measuring "did the agent use the lookup tool" as a proxy for recall improvement. The lookup tool (`/when`) requires the same metacognitive recognition step (knowing you're uncertain about a decision) as the passive index it replaced. Changing the action mechanism doesn't change the recognition bottleneck.
- Correct pattern: Distinguish recognition (knowing when to look something up) from retrieval (performing the lookup). Tools that improve retrieval without addressing recognition produce no measurable improvement. Forced injection (hooks detect topic mechanically, inject content) bypasses the recognition step entirely.
- Evidence: 801 sessions, 22 `/when` invocations in 8/193 post-merge sessions (4.1%). Direct decision file reads unchanged (21.2% → 21.8%). 1.1× improvement — noise. Baseline skill activation is ~20%; `/when` at 4.1% is below even that, suggesting metacognitive triggers have additional activation penalty vs procedural triggers.
## When batch changes span multiple artifact types
- Anti-pattern: Collapsing a multi-file batch into a single reviewer. Batch framing ("10 files changed, -97 lines") creates a cognitive unit that overrides per-artifact routing. Agent fabricates capability limitations on the correct reviewer ("skill-reviewer is for individual skills, not batch changes") to justify the simpler single-reviewer path.
- Correct pattern: Apply proportionality per-file first (trivial changes → self-review). Route remaining files by artifact type per routing table. The routing table is per-artifact-type, not per-batch. Same root cause as "batch momentum skip prevention" — batch framing overrides per-artifact decisions.
- Evidence: 8 of 10 files had ≤1-line changes (self-review sufficient). Remaining 2 were skill files → skill-reviewer. Agent routed all 10 to vet-fix-agent.
## When discovery decomposes by data point instead of operation pattern
- Anti-pattern: Brief presents a table of N items sharing identical structure (remove @-ref, verify skill coverage, optionally shrink to stub). Agent mirrors the table — one verification chain per row — producing N sequential reads instead of recognizing a single parametrized operation.
- Correct pattern: During discovery, identify the operation pattern first ("all N items follow remove + verify + shrink"). Verify the pattern holds (1-2 spot checks). Then produce a single inline step with a variation table, not N separate steps. Phase 0.86 consolidation catches this post-outline, but recognizing it during discovery avoids wasted exploration.
- Evidence: Context-optimization brief had 6 fragment demotions in a table. Agent checked each row independently (sandbox in worktree? vet in commit? hook-dev for config-layout?) instead of asking "do all 6 follow the same pattern?"
## When validate-runbook.py lifecycle flags pre-existing files
- Anti-pattern: Treating lifecycle exit 1 violations as blocking when the runbook modifies pre-existing files. The validator tracks create→modify order within the runbook; it has no awareness of files that exist on disk before runbook execution begins.
- Correct pattern: Verify flagged files exist on disk (`ls -la <path>`). If the file pre-exists, the violation is a false positive — proceed to prepare-runbook.py. Real violations are "modify before create" for NEW files (those not yet on disk).
- Evidence: hook-batch runbook phase validation flagged 7 lifecycle violations for `userpromptsubmit-shortcuts.py` (839 lines, pre-existing) and `tests/test_userpromptsubmit_shortcuts.py` (282 lines, pre-existing). All three other validators passed (model-tags, test-counts, red-plausibility). False positives, not blocking.
## When verifying delivered plan artifacts for removal
- Anti-pattern: Checking file existence (`test -f`) as proof of delivery. A file named after a deliverable can be a stub, placeholder, or incomplete implementation. Grep for file paths produces presence signal, not completeness signal.
- Correct pattern: Verify content — line counts for substance, function/class signatures for API coverage, test counts for coverage. Cross-reference against requirements (FR list) to confirm all deliverables are substantive. Takes one extra command (`wc -l` + targeted grep) per plan.
- Evidence: runbook-quality-gates initially removed on existence alone. User challenged; content verification confirmed 352-line script with 4 subcommands + 17 tests — substantive. plugin-migration had full runbook files (phases 0-6) but was planning artifacts, not execution output.
## When triaging behavioral code changes as Simple
- Anti-pattern: Assessing complexity from conceptual simplicity ("just read a config file") rather than structural criteria. Resolving "Simple to Moderate" ambiguity downward due to implementation eagerness — Simple means "start coding now," Moderate means "invoke another skill."
- Correct pattern: Simple criteria now include "no behavioral code changes" (same check as execution readiness gates at lines 219/421 of design skill). Behavioral code (new functions, changed logic paths, conditional branches) routes to Moderate → `/runbook` → TDD phase-type assessment. Test discipline is no longer an emergent property of routing — it's gated at triage.
- Root cause chain: motivated reasoning → resolved ambiguity downward → Simple path had no test gate → behavioral code shipped untested. Fix: added behavioral-code check to Simple criteria in design skill.
- Evidence: Tokens user config — 5 files (1 new module, 4 modified), fallback chain with multiple code paths, zero tests. Triaged as Simple based on conceptual ease.
## When recovering broken submodule worktree refs
- Anti-pattern: Manually recreating git admin directory stubs (`gitdir`, `commondir`, `HEAD`). Missing `index`, `refs/`, etc. makes git reject the admin dir. Manual `.git` file deletion + `submodule update --init` fails because directory is non-empty.
- Correct pattern: `git worktree repair` for parent repo links. For submodule worktrees: remove broken `.git` pointer files, remove stale admin dirs, then `git -C <submodule> worktree add --detach <path> HEAD`. After creating, fix HEAD to match what each parent worktree branch recorded: `git ls-tree HEAD <submodule>` gives expected commit, then `git -C <path> checkout <commit>`.
- Root cause: `core.worktree` in `.git/modules/<submodule>/config` gets overwritten when a worktree runs `submodule init` — points to worktree's submodule path instead of main's. Breaks all git operations that touch the submodule.
- Evidence: `git status` failed with `fatal: cannot chdir to '../../../../../../claudeutils-wt/hook-batch/agent-core'`. 4 worktrees had wrong agent-core HEAD (c4b8d11 instead of branch-specific commits).
## When submodule commits diverge during orchestration
- Anti-pattern: Sequential haiku agents committing to a submodule create branching history. Each agent's `git -C agent-core commit` may create a new branch point if the parent repo's submodule pointer isn't updated between steps. A merge at any point can silently drop earlier commits.
- Correct pattern: After each step that modifies the submodule, verify the submodule pointer in the parent matches the expected commit. At phase boundaries, verify submodule history is linear: `git -C agent-core log --oneline -N` should show all phase commits in sequence. If not, recover missing commits before proceeding.
- Evidence: Phase 5 vet discovered Phases 3-4 hook scripts (posttooluse-autoformat.sh, sessionstart-health.sh, stop-health-fallback.sh) were lost due to submodule merge at commit `118cd8b`. Scripts recovered from git history and re-committed.
## When phase files contain example fixture content with H2 headers
- Anti-pattern: Putting example runbook content (test fixture descriptions) in fenced code blocks within phase files. `extract_sections()` and `extract_cycles()` parse `## Step`/`## Cycle` headers line-by-line without honoring code fence boundaries. Duplicate step number errors result.
- Correct pattern: Describe fixture content using inline backtick-wrapped text or bullet lists instead of code blocks with actual H2 headers. Example: "Phase 2 header: `### Phase 2: Infrastructure (type: general)` followed by `Step 2.1: Setup`" instead of a code block containing `## Step 2.1: Setup`.
- Evidence: prepare-runbook.py failed with "ERROR: Duplicate step number: 2.1" — Phase 2 Cycle 2.1 RED setup had `## Step 2.1: Setup` inside a code fence, Phase 3 Cycle 3.1 had `## Step 2.1: Configure DB` in another code fence.
## When selecting agent type for orchestrated steps
- Anti-pattern: Substituting a built-in agent type (`tdd-task`) when the plan-specific agent (`<plan>-task`) isn't found. Silent substitution loses the common context injected by prepare-runbook.py and violates the orchestration contract. The learnings entry about custom agents being unavailable was backwards.
- Correct pattern: Plan-specific agent is mandatory for `/orchestrate`. If `<plan>-task` isn't available as a subagent_type, STOP and report — don't substitute. Session restart makes custom agents in `.claude/agents/` discoverable. `tdd-task` is only for ad-hoc TDD cycles outside prepared runbooks.
- Evidence: Dispatched Cycle 1.1 via `tdd-task` instead of `runbook-generation-fixes-task`. User corrected: restart had made the custom agent available. Remaining 12 cycles used the correct agent type.
## When TDD cycles grow a shared test file past line limits
- Anti-pattern: Each cycle agent adds tests to the designated test module without awareness of cumulative line count. The 400-line limit surfaces as a precommit failure requiring refactor escalation — 3 escalations across Cycles 3.1, 3.2, 3.3, and 4.1 for the same root cause.
- Correct pattern: Step files for later cycles should include conditional split instructions: "If `test_prepare_runbook_mixed.py` exceeds 380 lines, extract `TestPhaseContext` to `test_prepare_runbook_phase_context.py` before adding tests." Alternatively, runbook planning should pre-assign test classes to separate files when cumulative growth is predictable.
- Evidence: `test_prepare_runbook_mixed.py` grew from 382 → 409 → 478 → 465 lines across Phases 3-4. Each refactor escalation cost ~80-110K tokens. TDD process review flagged this as the primary compliance issue.
- Evidence: outline-corrector + design.md + design-corrector cost ~112K tokens for work that could have been done inline. Findings would have surfaced during editing.
## When selecting reviewer for artifact review
- Anti-pattern: Defaulting to corrector for all artifacts because the review-requirement fragment names it as the universal reviewer. Fragments are LLM-consumed behavioral instructions, not human documentation — doc-writing skill is wrong reviewer for them.
- Correct pattern: Check artifact-type routing table before selecting reviewer. Skills → skill-reviewer, agents → agent-creator, design → design-corrector, fragments → corrector (default, not doc-writing). Full routing table and review protocol in `agent-core/fragments/review-requirement.md`. Commit skill Step 1 is the enforcement gate.
- Evidence: Selected corrector for skill edits. User corrected to skill-reviewer. Root cause: generic rule without routing lookup.
- Anti-pattern: Routing through full runbook pipeline (outline → runbook expansion → runbook-corrector → prepare-runbook.py → step files → orchestrate → per-step agents) when all phases are additive prose with no feedback loop.
- Anti-pattern: Skipping procedural review (outline-corrector) after redrafting because individual changes were user-validated in discussion. Implicit reasoning: "user approved each change → combined redraft doesn't need review."
- Anti-pattern: Defending "frequently useful" as "always needed." Initial analysis identified only ~3k demotable tokens from 25.5k — too conservative. Treated workflow-specific content (sandbox-exemptions, review-requirement) as cross-cutting.
- Correct pattern: Distinguish behavioral rules (shape every interaction, no injection point) from procedural/reference content (needed at specific workflow steps, injectable via skills or hooks). Passive fragments that don't trigger behavior (review-requirement: agents don't review because they read the fragment) are dead weight regardless of content quality.
- Evidence: Review-requirement (2.4k tokens) is passive — commit skill Step 1 is the actual enforcement. Sandbox-exemptions (986 tokens) duplicated by worktree skill. Revised analysis: ~6.6k demotable (26%), not ~3k.
- Evidence: 8 of 10 files had ≤1-line changes (self-review sufficient). Remaining 2 were skill files → skill-reviewer. Agent routed all 10 to corrector.
## When custom agents aren't available as Task subagent_types
- Anti-pattern: Assuming `.claude/agents/*.md` files with proper frontmatter are automatically available as `subagent_type` values in the Task tool. Attempting to use them produces "Agent type not found" errors.
- Correct pattern: Use built-in agent types (`test-driver`, `artisan`, `general-purpose`, etc.) with phase context injected in the prompt. Include the agent's instructions (TDD protocol, stop conditions, output format) directly in the Task prompt. Read the phase context file path so the agent can load it.
- Evidence: 5 custom agents (`hb-p1` through `hb-p5`) created with valid YAML frontmatter, not discoverable. Session restart was noted as required but didn't resolve. All 16 steps executed successfully via built-in types.
## When invoking executable Python scripts
- Anti-pattern: Prepending `python3` to `.py` scripts that have shebangs and are executable directly. The `python3` command is in the project's bash deny list, causing auto-denial. Agents add the prefix despite skill files showing direct invocation (e.g., `agent-core/bin/prepare-runbook.py plans/...`).
- Correct pattern: Invoke executable scripts directly by path. The shebang (`#!/usr/bin/env python3`) handles interpreter selection. Check the skill's example invocation before constructing the command.
- Evidence: `python3 agent-core/bin/prepare-runbook.py` denied 3 times. `agent-core/bin/prepare-runbook.py` succeeded immediately. User noted this is a recurring pattern across agents.
## When step file inventory misses codebase references
- Anti-pattern: Runbook step lists ~30 files for substitution propagation based on Phase 0.5 discovery. Actual codebase has ~45 files with old names — discovery missed skills (review-plan, requirements, ground, handoff examples), decisions (defense-in-depth, implementation-notes), fragments (error-classification), agents (refactor.md), and prepare-runbook.py code paths.
- Correct pattern: Step 1.7's "grep entire codebase for ALL old names" is the safety net. But the propagation step agent hit context ceiling at 210 tool uses before reaching verification. Discovery inventory should use `grep -r` across the full tree, not manual file listing.
- Evidence: Step 1.6 opus agent modified 30 listed files, hit ceiling. Second opus agent fixed 17 additional files. Orchestrator fixed 3 more path references.
## When inline phases are appended to last step file
- Anti-pattern: Assuming haiku will respect step boundaries when the step file contains additional content below the step's closing `---`. prepare-runbook.py appends inline phase content to the last step file.
- Correct pattern: Haiku executed Step 1.7 AND Phase 2 AND Phase 3 because all content was in one file. This was actually beneficial in this case (all work completed), but violates the assumption that each agent executes only its assigned step. For orchestration control, inline phases should be dispatched separately — not appended to step files.
- Evidence: Step 1.7 haiku agent reported completing deslop restructuring and code density entries — work belonging to Phases 2-3.