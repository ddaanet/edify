# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When a proximal requirement reveals lifecycle gaps
- Triage feedback (Gap 7) required a post-execution comparison point. Investigation: /commit too generic (fires all sessions), /handoff wrong scope (session state not execution assessment). Root cause: inline execution (Tier 1, /design direct execution) has no lifecycle skill. The pipeline state machine goes /requirements → /design → /runbook → /orchestrate → /deliverable-review → /commit, but work classified as execution-ready exits through an unstructured gap between /design and /handoff.
- Correct pattern: the proximal requirement points at the structural gap. Fix the gap (inline execution skill covering pre-work + execute + post-work), and the proximal requirement becomes one FR among many.
- Corollary: conditional gates ("skip Read if no /design ran") reintroduce prose-gate failure modes. The D+B principle applies: unconditional Read, file absence is the negative path. A Read returning file-not-found is cheaper than the risk of a missed comparison.
## When implementation modifies pipeline skills
- Anti-pattern: Using the full runbook pipeline (prepare-runbook.py → orchestrator → step files) when the planned work modifies pipeline skills (/design, /runbook) or pipeline contracts. Self-modification coupling: a runbook step that edits the runbook skill creates stale-instruction risk for subsequent steps.
- Correct pattern: Structure as inline task sequence orchestrated through session pending tasks. Each task executes with fresh CLAUDE.md loads, sidestepping stale instructions. TDD discipline preserved — executing session dispatches test-driver via Task tool per cycle. Corrector dispatch per task replaces checkpoint gates.
- Also applies when: no parallelization benefit (strict dependency chain negates Tier 3's parallel step execution), overhead/value mismatch (pipeline coordination cost > error-recovery value for ~10 sequential work units).
## When delegating TDD cycles to test-driver
- Anti-pattern: Sending all N cycles in a single prompt. Agent loses focus on later cycles, context overloaded with spec it hasn't reached yet. Also: full prompt may trigger hooks on path patterns in test fixture descriptions.
- Correct pattern: Piecemeal — one cycle per invocation. Resume the same agent for subsequent cycles (preserves accumulated file reads + implementation context). Continue until agent context nears 150k. Fresh agent if context exhausted.
- Context priming: Sub-agents don't share parent context. Each NEW agent must self-prime by running `claudeutils _recall resolve` on relevant recall-artifact entries. Include instruction: "Read plans/X/recall-artifact.md, then batch-resolve relevant entries via `claudeutils _recall resolve`." Resumed agents already have this context.
## When assessing just precommit cost
- `just precommit` is fast when the test suite is green, thanks to test sentinel. Not a heavy operation in the common case — valid as both entry gate and exit gate without redundant overhead concern.
## When editing skill files
- The `description` field is dual-purpose: CLI picker display AND agent triggering (no separate field — #28934). Lead with action verb (user display), then trigger phrases (agent matching). H1 title is body content only. Fallback: first paragraph if `description` omitted.
- Extraction safety: every content block moved to references/ must leave trigger condition + Read instruction in SKILL.md body.
- Control flow verification: after restructuring conditional branches, enumerate all paths, verify user-visible output on each.
- D+B gate additions: must not change gate decision outcome on existing paths.
- Entry point naming: named entry points (`execute`) not `--flag` conventions. Skills parse prose args, not CLI flags.
- Prose quality: `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework.
- Triggers: editing skills, skill surgery, deslop, extraction, progressive disclosure, restructuring conditional branches
- Pending: consolidate into `/skill-dev` skill (front-loads plugin-dev:skill-development via continuation passing)
## When writing recall artifacts for sub-agents
- Two distinct artifact models: pipeline recall (grouped entries with relevance notes, selective resolution by consuming skill) vs sub-agent injection (flat trigger list, resolve-all, no selection judgment). Sub-agents have no parent context — they can't judge which entries are relevant, making selective resolution circular.
- Anti-pattern: Using pipeline-model artifacts (grouped, relevance notes) when the consumer is a delegated agent. The grouping invites selective resolution which the agent can't perform.
- Correct pattern: Flat list for sub-agent injection. Delegation prompt says "resolve ALL entries." Pipeline model for skills/orchestrators that have topic context for selection.
## When loaded decisions miss error context
- Decisions loaded via `/recall broad` early in session aren't functionally present when errors fire later (context rotation). The agent processes lint error against immediate context (error message, rule description), not against decisions loaded 50k+ tokens earlier.
- Anti-pattern: Adding another recall pass as prose instruction ("recall after lint failure") — this is a prose gate, same failure mode as the original recall.
- Correct pattern: Structural injection — PostToolUse hook injects memory-index content on first lint/precommit red after green (state-transition gated). Separate PreToolUse recall gate forces index scanning before fix attempt. Two layers: injection (availability) + gate (application).
## When handling deliverable review findings
- Codified to `agents/decisions/deliverable-review.md` — "When Resolving Deliverable Review Findings"
- Key addition from 2nd occurrence RCA: severity-as-priority-filter rationalization. Agent treated Minor severity as skip permission during fix task execution. Root cause was ambiguous "deferral" language in review skill (fixed: replaced with "pending task"). Learning alone didn't prevent recurrence — codified to decisions/ for `claudeutils _recall resolve` discoverability.
## When routing Moderate classification to runbook
- Requirements can be behaviorally complete (every FR has testable acceptance criteria) but structurally incomplete (no module layout, function decomposition, wiring decisions). The /design Moderate route skips design entirely — "Route to /runbook." The /runbook Tier 3 has Phase 0.75 (runbook outline) but that's runbook structure, not implementation approach.
- Anti-pattern: Letting structural decisions (package layout, shared components, error patterns, test organization) get made implicitly during runbook cycle planning or ad-hoc by the executing agent.
- Correct pattern: When requirements lack structural decisions, generate a lightweight outline before /runbook. The outline materializes "how" decisions (module structure, component boundaries, wiring) alongside the "what" (behavioral spec). Skip only when requirements are functionally complete — behavioral + structural.
- Single data point: recall-cli-integration. Trigger condition needs sharper criteria before modifying /design skill.
## When orchestrating multi-step delegated execution
- Anti-pattern: Splitting post-step verification into separate tool calls. First check (git status) returns clean → exit momentum suppresses second check (just lint). The sub-agent "already linted" rationalization makes the skip feel safe.
- Correct pattern: Single compound command (`git status --porcelain && just lint`). Compound commands can't be partially executed — both run or neither. Same principle as `_fail` consolidating display+exit.
- Also applies: `execute` entry point in session.md. `execute` is a same-turn chaining flag (skill → skill within one conversation). session.md always crosses a context boundary — `execute` there bypasses Phase 2 recall (D+B anchor). Precommit lint catches this mechanically.
## When writing multiline strings in indented code
- Anti-pattern: Triple-quoted strings flush-left or with inconsistent indentation to avoid unwanted whitespace in the value. Breaks visual code structure.
- Correct pattern: `from textwrap import dedent`, then `dedent("""\n    indented content\n    """)`. Keeps the string visually aligned with surrounding code while stripping common leading whitespace at runtime.
- Scope: non-docstring multiline strings (test fixtures, template content, heredoc-style text). Docstrings have their own `inspect.cleandoc` handling.
## When reading validation command output
- Anti-pattern: `just precommit 2>&1 | tail -N` or similar truncation. Validation output is a diagnostic signal — truncation hides the pass/fail/xfail summary that distinguishes real failures from expected noise. Agent then draws wrong conclusions from incomplete data.
- Correct pattern: Show full output from `just precommit`, `just test`, `just lint`. If output is too long, fix the recipe (add `--quiet`, `--tb=no`), not the consumption site.
- Evidence: xfail traceback from `pytest-markdown-report` was visually identical to real failure. Agent tailed output, missed summary counts, ran `git stash` diagnostic cycle, still drew wrong conclusion. Full output would have shown "30 passed, 1 xfailed" immediately.
## When a test fails only in suite
- Anti-pattern: Treating test ordering dependence as "flaky" and retrying or ignoring. A test that fails only when run after other tests has shared mutable state — that's a bug, not noise.
- Correct pattern: Diagnose the pollution. Run `pytest --lf` to confirm, then bisect with `pytest -x` subsets. Fix the shared state (fixture cleanup, monkeypatch teardown, global mutation). The test or its predecessor is wrong.
- Rationale: "Passes in isolation" is a diagnostic signal, not a resolution. Merging with a known ordering-dependent failure means the suite is unreliable — future failures get dismissed as "that flaky test."
## When doing TDD after full codebase exploration
- Anti-pattern: Writing all tests in one batch after reading the implementation target, then implementing everything at once. The RED phase shows only ImportError (function doesn't exist), not behavioral failures. Tests cannot guide discovery because the implementation is pre-formed from the exploration phase.
- Correct pattern: When task decomposition marks a task as TDD and the current session loaded implementation context during design/exploration, delegate to test-driver agent in a fresh context. The design session and the TDD session must be different contexts — TDD requires implementation to be unknown for tests to guide discovery.
- Evidence: 15 tests written at once, all 15 passed on first implementation attempt. No test ever failed on a behavioral assertion. This is test-after development with TDD ceremony.
## When hook messages conflict with behavioral rules
- Anti-pattern: Hook blocks a dangerous action (correct) but gives misleading guidance that conflicts with behavioral rules. "Retry the git command" caused the agent to retry rm with a different path instead of stopping — the hook's "retry" directive competed with the "stop on unexpected results" rule.
- Correct pattern: Hook messages must align with the behavioral rules they enforce. For lock contention: "Retry your git command — do not delete lock files" (not "STOP" which triggers halt-and-wait behavior, and not ambiguous "retry" without specifying what to retry). The agent retries the original git operation after natural model latency provides sufficient backoff.
- Evidence: Agent retried rm twice following hook's "retry" advice. Lock was from concurrent worktree session, not stale — transient contention that self-resolves.
## When d: mode validates a proposed change
- Anti-pattern: `d:` evaluation concludes with affirmative verdict ("agree, this should be done"), then stops. The validated change exists only in conversation context. No pending task created, no brief written. Change is lost on context rotation.
- Correct pattern: When `d:` verdict is "agree, this change should be made" (or equivalent), chain to `p:` evaluation — task name, model tier, restart flag. Create brief if discussion produced design context worth preserving. Three consecutive misses in one session (wt-rm-dirty review, 2026-03-01) confirm this is systematic, not incidental.
- Scope: applies when the discussion conclusion implies future work. Pure analysis ("is X true?") or rejected proposals ("disagree") don't trigger the chain.
## When classifying composite tasks
- Anti-pattern: Batch-classifying a task containing multiple discrete work items (deliverable review findings, PR comments, multi-FR list). Group reasoning averages heterogeneous items — a behavioral code change gets masked by non-behavioral siblings.
- Correct pattern: Decompose before classifying. If the input artifact contains N discrete work items, produce a per-item behavioral code check. Any item that adds conditional branches, functions, or logic paths elevates that item to Moderate minimum.
- Distinct from companion tasks (explicit user bundling in session notes). Composite tasks are implicitly bundled by the task's nature — decomposition requires reading the input artifact.
- Evidence: M-1 (precondition guard adding conditional branch) batch-classified as Simple alongside M-2 (comment) and M-3 (assertion tightening). Third instance of "behavioral code as Simple" pattern.
## When classifying pending task model tier
- Anti-pattern: Defaulting to sonnet for tasks involving agentic prose (skill expansions, directive definitions, architectural documents). The "prose edits to architectural artifacts require opus" rule exists but isn't applied during p: classification.
- Correct pattern: Before stating model tier, check artifact type. Agentic prose (behavioral directives, skill content, fragment edits) → opus. Code implementation → model by complexity. The decision "when selecting model for prose artifact edits" (pipeline-contracts.md) applies to p: classification, not just runbook planning.
- Evidence: `w` command classified as sonnet 3×, `agent-core lint coverage` classified as sonnet 1×, both corrected to opus. Same rule available in context via topic injection but not applied.
## When directives outgrow text expansions
- Anti-pattern: Keeping complex multi-step protocols as UPS text expansions (Tier 2 directives). The d: directive has ground→assess→stress-test→verdict sequence, but text expansions are instructions with no structural enforcement. Steps get skipped under momentum.
- Correct pattern: When a directive develops a protocol with ordered steps where skipping a step produces observable failure, promote to a skill with tool gates. D+B gates (Read, recall resolve) make steps non-skippable. Text expansions remain appropriate for simple behavioral framing (b:, q:, learn:).
- Evidence: d: grounding step skipped 2× in one session, p: model classification wrong 3× in one session. Both have loaded rules that weren't applied — the prose-gate failure mode.
## When reclassifying tasks after structural changes
- Anti-pattern: Shipping a new classification model (two-section In-tree/Worktree Tasks) without reclassifying existing tasks. Handoff perpetuates defaults — all 60+ tasks stayed In-tree despite D-9 heuristic qualifying most for Worktree Tasks. On main (parent of worktrees), this left the Worktree Tasks section empty, making `wt` unable to dispatch.
- Correct pattern: Structural changes to task organization require a bulk reclassification pass on existing data. Classification heuristics apply retroactively, not just to new tasks.
- Compounding factor: Stale decision entry in `workflow-advanced.md` (2026-02-20, single-section model) contradicts the superseding entry in `operational-tooling.md` (2026-02-28, two-section model). Stale entry never cleaned up on delivery — the "Delivery supercession" task exists for exactly this gap.
## When merge fails on main
- Anti-pattern: Resolving conflicts and precommit failures on main after `_worktree merge`. The main session lacks branch context — it resolves conflicts by reading diff markers, not understanding intent. Precommit failures leave a broken merge commit on main requiring amend.
- Correct pattern: Rollback main on failure (`git merge --abort`). The branch merges main into itself first (existing plan: `worktree-merge-from-main`), resolves conflicts in its own context where the developer/agent has full change knowledge, passes precommit, then main retries. Main-side merge becomes trivially clean.
- Implication: `worktree-merge-from-main` becomes a prerequisite for merge resilience, not an independent task. The sequence: build `merge --from-main` (branch self-updates) → modify `_worktree merge` to rollback-and-report → skill workflow guides user to update branch then retry.
- Session.md/learnings.md auto-resolve (`remerge_session_md`, `remerge_learnings_md`) may still run on main — these are mechanical, context-free. Rollback applies to source conflicts and precommit failures where main lacks resolution context.
## When starting work on a task
- Anti-pattern: Jumping to `/design` because the task description seems clear enough. Session.md task entries are scope (name + one-liner), not specification. The gap between task description and behavioral FRs is where design sessions waste time discovering what they're building.
- Correct pattern: Always start from `/requirements` unless a requirement-equivalent document already exists. Requirement-equivalent: existing requirements.md, design.md with behavioral FRs, deliverable review report (findings = acceptance criteria for rework). Brief.md is NOT equivalent — transfers context but lacks testable acceptance criteria.
- Rationale: `/requirements` includes a recall step that grounds extraction against existing infrastructure. Skipping to `/design` produces naive requirements (workflow-advanced.md). The `/design` Phase 0 requirements-clarity gate fires at 2.6% rate (1/38 sessions) — too late and too rare to compensate.
- For well-discussed tasks (`d:` → `p:` chain): `/requirements` primary mode is conversation-to-artifact capture, not elicitation. Fast when requirements are pre-resolved — extract, write, done. The artifact persists across context boundaries; discussion conclusions don't survive `/clear`.
## How to wrap a discussion session
- `w` (wrap) is a Tier 1 command (standalone, no colon, no user content). Sequence: findings → takeaways → submit.
- **Findings:** Summarize what the investigation/discussion discovered (factual, not narrative).
- **Takeaways:** Extract learnings (append to learnings.md), create pending tasks (`p:` evaluation for each validated change), write briefs if discussion produced design context worth preserving.
- **Submit:** `/handoff --commit` (or `hc`).
- Trigger: user says `wrap` or `w` at any point during or after discussion. The command crystallizes conversation context into persistent artifacts before context rotates out.
- Pending: absorbed into directive-skill-promotion task. This learning bridges the gap until the UPS expansion is implemented.
## When converting external documentation to recall entries
- Two trigger classes have different automation profiles: `how` entries (task-descriptive: "how to encode URL in Python") can be extracted mechanically from documentation headings — sonnet automation with corrector pass. `when` entries (situational: "when classifying composite tasks") require operational experience to author — hand-curation from incidents and failures.
- Anti-pattern: Treating all trigger extraction as equivalent quality risk. Applying corrector-heavy workflows to `how` entries (unnecessary) or batch-automating `when` entries (insufficient).
- Correct pattern: Batch-automate `how` extraction from reference documentation. Reserve `when` for experiential curation. Corrector validates trigger specificity and dedup against existing index.
- Structural insight: training provides reasoning capability; recall provides authoritative inputs. For operational methodology, explicit recall entries override ambiguous training-data patterns. Interaction structure (skills, tool gates, PreToolUse hooks) enforces application at the right moment — sidesteps the "skill recall baseline" problem (context displacement over long sessions).
## When displaying Next task in STATUS
- Anti-pattern: Showing a worktree task's execution command (e.g., `/requirements plans/X/brief.md`) as the "Next" action. Worktree tasks can't be executed directly — `x` doesn't pick them up. The displayed command is unreachable without `wt` setup first.
- Correct pattern: When all in-tree tasks are blocked and the first actionable work is a worktree task, "Next" should point to worktree setup: `wt <task-name>` or `wt` for parallel group. The execution command belongs inside the worktree session, not in main's STATUS.
- Rationale: STATUS guides the user's next action. An unreachable command creates a false affordance — user tries `x`, gets nothing because worktree tasks are excluded from execute pickup.
## When filtering observable state from status output
- Anti-pattern: Reporting "clean" when `git status --porcelain` shows modified files, rationalizing known-dirty files (`.claude/settings.json`) as "always dirty" and therefore ignorable.
- Correct pattern: `git status --porcelain` non-empty means dirty. Report it as dirty. The user decides what's ignorable — the agent reports observable state without filtering.
- Rationale: Filtering "expected" dirty files is a judgment call that suppresses signal. The user may want to know about the dirty file, or the file may be dirty for a different reason than assumed.
## When merge precommit fails on main
- Anti-pattern: Debugging and fixing on main after `_worktree merge` fails precommit. Main lacks branch context — fixes are guesswork. Amending the merge commit bakes in potentially wrong fixes.
- Correct pattern: `git merge --abort`, fix in the branch worktree (where the developer/agent has full change knowledge), pass precommit there, re-merge. Main-side merge should be trivially clean.
- Also: never `--force` remove a worktree without first listing the uncommitted files. Two uncommitted files lost permanently — could have been unreplicated work.
## When infrastructure pre-dates its capability
- Plan status `ready` reflects structural completeness (files exist, agents generated), not functional completeness relative to the plan's goals. Artifacts generated by the pre-improvement pipeline lack the capability being built.
- Evidence: orchestrate-evolution runbook `ready` with 14 step files + 4 crew agents, but generated by pipeline without recall embedding (D-2). Recall artifact (20 entries) disconnected from all execution artifacts. The plan builds recall embedding, but its own execution infrastructure doesn't have it.
- Correct check: does the pipeline that generated these artifacts support the capabilities the plan requires for quality execution?
## When grounding verifies structure instead of semantics
- Anti-pattern: Confirming artifacts exist (files present, status `ready`, agents generated) without checking functional adequacy (recall connected, decisions embedded, context injected). Structural verification produces false confidence in functional completeness.
- Correct pattern: Targeted factual probes ("does X handle Y?") over theoretical counter-arguments during stress-testing. When an evaluation hinges on existing infrastructure, probe capabilities not just presence.
- Same failure class as structural tests vs behavioral tests — checking that things exist rather than checking that they work correctly.
- Evidence: Read orchestrator plan, step file list, crew agent header — concluded "infrastructure exists → marginal cost near zero." Single factual probe ("does the runbook handle recall?") flipped the verdict.
## When sunk-cost framing enters evaluation
- "Already built," "marginal cost near zero," "would go unused" are sunk-cost signals that bias toward using existing artifacts by framing alternatives as waste rather than evaluating fitness.
- Anti-pattern: "What does switching lose?" (frames alternative as loss). Correct framing: "Does this infrastructure meet execution requirements?" (evaluates fitness).
- Inadequate infrastructure has zero value regardless of preparation cost. Adequate infrastructure has value regardless of whether an alternative exists. Sunk cost is never an advantage — the artifact is either useful or it isn't.
## When codify triggers on a feature branch
- Do not codify on feature branches. Decision file changes create merge conflicts with main's decisions/. Defer codification to main.
- The soft-limit age calculation should account for branch context — learnings on feature branches are younger in main-branch terms.
- Pending: Codify branch awareness task (sonnet, no restart).
## When lint-gated recall needs error categorization
- Tuick (user's project, `~/code/tuick/`) has reusable errorformat parsing: `ErrorformatEntry` (filename, lnum, text, type), `tool_registry.py` (tool detection, custom patterns for ruff/pytest/mypy), `group_entries_by_location`, `group_pytest_entries`. Direct code reuse — not a dependency.
- For lint-gated recall hook: parse `just precommit` output → structured error entries → extract error codes/categories from `text` field → map to recall domain keywords → inject matching memory-index entries.
- Only new piece: error category → recall keyword mapping table. Parsing infrastructure already solved.
- Per-error-type gating (not just first-red-after-green): each novel error category triggers fresh recall injection. Hook tracks seen categories, fires on new ones.
## When pending tasks lack recovery context
- Anti-pattern: Task entry has description but no backtick command. Next session's `x` has nothing to invoke. Worse: discussion conclusions (d: mode decisions, agreed refinements, identified reuse paths) exist only in conversation context — lost on session boundary.
- Correct pattern: Every pending task gets a backtick command in the entry. Discussion conclusions that produce pending work get captured as task notes in session.md, recoverable via `task-context.sh`. The handoff IS the recovery mechanism — if it's not in session.md, it doesn't survive.
- Evidence: Codify branch awareness task had no command. Lint-gated recall refinement (tuick reuse, per-error-type gating) existed only in conversation until manually captured.
## When "worktree-tasks-only" appears to block maintenance skills
- The "main is worktree-tasks-only" rule scopes to task classification (pending tasks in session.md), not interactive skill execution. Maintenance skills (`/codify`, `/commit`, `/handoff`) run on main regardless.
- Anti-pattern: Proposing workaround branches for codify because "main doesn't allow work." The rule governs where pending tasks live, not what skills can execute.
- Correct pattern: Run `/codify` on main directly. Dispatch worktrees for implementation tasks after. Sequential, not parallel — worktrees benefit from updated decisions/ anyway.
- The codify-in-a-branch proposal fails on merge ordering: codify touches decisions/, fragments/, memory-index.md — shared infrastructure with no deterministic merge-first guarantee.