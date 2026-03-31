# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `plugin/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When codify drops incident-specific learnings
- Anti-pattern: Codify skill quality criteria unconditionally reject incident-specific entries ("describes what happened, not what to do"). Loses recurrence signal — "this happened twice" changes fix priority.
- Correct pattern: Incident-specific entries have value as occurrence counters even without a generalized principle. Recurrence tracking is a valid consolidation reason. Methodology TBD (plan: incident-counting).
- When user says "force" (flush all), skill-internal quality filters should not override user intent.


## When agent dismisses test failures as "pre-existing"
- Anti-pattern: Agent runs scoped tests (single file/module), gets green. At commit time, full suite shows failures. Agent classifies as "pre-existing" without verifying — two instances in one session (`68963394`, `63af67bf`).
- Correct pattern: If `just precommit` shows failures not present in prior commit, they are regressions from this session. Verify with `git stash && just test && git stash pop` or check the test names against changed files.
- Root cause: scoped test run (29 pass) creates false confidence. `replace_all` on mock targets was syntactically correct but semantically wrong (API key tests mocked count function to prevent SDK init, not to test counting).

## When bare directives bypass workflow gates
- Anti-pattern: `execute and apply fixes inline then handoff and commit` — agent executes directly without Skill tool invocation. No `/inline` lifecycle, no corrector dispatch, no baseline verification.
- Correct pattern: Production edits require skill invocation (`/inline`, `/orchestrate`) which provides corrector gates. Bare directives produce no structural quality checks — agent judgment is the only defense.
- Evidence: Two regressions committed in one day. Both from autonomous agent work without skill gates.

## When skipping corrector via downgrade criteria (2026-03-12)
- Anti-pattern: Post-outline complexity re-check says "all downgrade criteria hold" → skip A.6 corrector review. Agent treats the downgrade escape as permission to skip quality review entirely. The criteria gate whether complexity downgrades, not whether author-blind errors exist.
- Correct pattern: Downgrade criteria determine ceremony level (skip full design generation). Corrector review is independent — it catches issues the author is blind to regardless of complexity classification. Run corrector even when downgrading.

## When grounding on wrong domain
- Anti-pattern: Grounding /proof's review patterns against code review tools (GitHub, Gerrit, Phabricator) when /proof primarily reviews planning artifacts (requirements, outlines, designs). Code review verdicts (approve/request-changes) don't cover planning-artifact-specific actions (absorb, triage).
- Correct pattern: Identify the review domain per artifact type before selecting grounding sources. Planning artifacts → backlog refinement, architecture review, process review literature. Code → code review tools. Each domain has its own natural verdict vocabulary.
- Evidence: Dogfooded interactive review on its own outline — user surfaced that `absorb` was dropped based on code review convergence, but it's natural for backlog grooming. Led to artifact-type-dependent verdict vocabulary design.

## When specifying explicit mechanisms for natural conversation
- Anti-pattern: Designing explicit UX mechanisms (flags like `--items`, "revisit N", override prompts at checkpoints) for capabilities the conversational medium handles naturally. The user can just say what they want.
- Correct pattern: Don't encode mechanisms for things the model handles via natural language. Explicit verdicts (a/r/k/s) are needed because they trigger specific actions. Navigation, override, and discussion don't need explicit mechanisms — non-verdict input is implicit discussion, revisit uses flexible identification, granularity overrides happen conversationally.

## When chained skills share recall context
- Anti-pattern: /design loads triage-scoped recall entries → /runbook skips its mandatory recall gate because entries are "already in context." Agent conflates triage-scoped recall (how to classify) with implementation-scoped recall (what patterns apply when building). Gate's artifact-exists/fallback branching makes the no-artifact path feel skippable.
- Correct pattern: Each skill's recall gate serves a different scope. Triage recall ≠ implementation recall — different triggers, different domain entries. The D+B anchor (tool call) must fire regardless of what's in context. Same-conversation visibility of upstream recall does not satisfy downstream gates.
- Root cause: Gate structure frames memory-index scan as "fallback" when it's the primary path for moderate tasks. Artifact-existence branching is a Tier 3 concern (cross-session persistence) leaking into Tier 1/2 (same-session, same-context).

## When placing correctional instructions in workflows
- Anti-pattern: Adding a trim/cleanup step downstream of the generation step that creates the defect. "Generate Completed content (append everything) → Step 6: trim stale content." The downstream step competes with the generation instruction and can be forgotten or rationalized away.
- Correct pattern: Place the correctional instruction at the generation point. "Fresh write → Completed contains only this conversation's work." Content is correct from the start — no append-then-trim cycle. Same class as "validate at input, not output."
- Evidence: Completed This Session accumulated 66 lines across 4+ prior sessions. Step 6 trim instruction was the initial fix; user identified it as structurally weak. Moved to Step 1 generation point.

## When multi-sub-problem plans reach design
- Anti-pattern: Batching independent sub-problems through entire plan lifecycle (design → runbook → orchestrate → deliver). Creates delivery ordering problems — can't ship SP-3 until SP-1 finishes, can't prioritize independently.
- Correct pattern: Keep sub-problems together through design (shared context benefits). After design, split into separate tasks with explicit dependencies. Parent plan delivers at "designed" status (terminal). Children are new plans starting at "planned." Each gets own WSJF score, model tier, worktree classification.
- Exception: Dependent sub-problems (S-B depends on S-A's output format) stay together through design but execute as separate tasks with cross-task dependency.
- Design coherence under change: if a sub-problem's execution reveals the shared design was wrong, propagation via "merge parent" (worktree merge from parent branch) handles updates.

## When delegating external repo git operations
- Anti-pattern: Dispatch artisan agents to run `git -C ~/code/<repo>` on repos outside the project tree. Sandbox write-allow restrictions block the agent even though the operations are read-only.
- Correct pattern: Execute git read operations (`git -C`, `git log`, `git show`) directly from the parent session. Sub-agents only work reliably within the project's sandbox-allowed paths.
- scratch/* repos under edify worked because `~/code/edify` is in the write-allow list. External repos (~/code/rules, ~/code/tuick, etc.) failed.
## When dispatching corrector with plan-path-containing prompts
- Anti-pattern: Including template notation like `plans/{plan}/` or `plans/<name>/` anywhere in the corrector prompt text. The PreToolUse recall-check hook uses `re.search(r"plans/([^/]+)/", prompt)` to extract the job name — it finds the FIRST match, which may be template text rather than the actual plan path.
- Correct pattern: Put the actual plan path (`plans/outline-proofing/`) as the FIRST `plans/X/` reference in the prompt (e.g., "Plan: plans/outline-proofing/ — review implementation changes"). Avoid template-style placeholders in requirement text; use natural language descriptions instead.
- Root cause: `re.search` returns first match, not best match. Template text like `plans/{plan}/outline.md` in a requirements bullet appears before the actual plan path references.

## When calling triage-feedback.sh
- Anti-pattern: Calling `triage-feedback.sh plans/outline-proofing baseline` — the script prepends `plans/` to `$1`, so the reports dir becomes `plans/plans/outline-proofing/reports` (double-prefixed).
- Correct pattern: Pass just the job name: `triage-feedback.sh outline-proofing baseline`. The script constructs `plans/outline-proofing/reports` internally.
- Note: The inline skill's documented invocation is `triage-feedback.sh plans/<job>` — this is incorrect. The script implementation uses the arg as a suffix to `plans/`.
## When referencing format files in skill steps
- Anti-pattern: "Generate X using format from `references/foo.md`" — implies reading but doesn't require it. Agent may rationalize from memory rather than reading the file, producing format drift.
- Correct pattern: Explicit Read instruction: "Read `references/foo.md`. Generate X using that format." Matches Complex path convention ("Read `references/write-outline.md`") and removes ambiguity.
- Evidence: M2 in outline-proofing deliverable review — Moderate agentic-prose path step used implicit form while Complex path used explicit form.
## When writing inline skill deliverable review task
- Anti-pattern: Using the inline skill's template `Deliverable review: <job>` verbatim — contains a colon (forbidden by task validator) and exceeds the 25-character limit for any job name longer than 9 characters.
- Correct pattern: Use a short noun phrase without colon: e.g. `<Job> fix review` (≤25 chars, no colon). Fix the template in inline/SKILL.md to use a valid task name format.
- Evidence: Precommit caught "contains forbidden character ':'" and "exceeds 25 character limit" when writing the deliverable review task for outline-proofing.
## When runbook steps reference undesigned mechanisms
- Anti-pattern: Runbook skill generates steps with placeholder language ("standard tmux interaction", "same mechanism as Step X") for mechanisms not in the design artifact. Looks specified but isn't. Passes correctors and /proof orientation without surfacing as a blocker.
- Correct pattern: When a step depends on a mechanism not in the design artifact, either (a) design it inline as a preceding spike step, or (b) emit a structured design gap and halt — do not generate the step with placeholder text.
- Evidence: Steps 1.3, 2.4, 6.1, 6.3 in plugin-migration all referenced "standard tmux interaction" — mechanism for driving live Claude session via tmux not designed. Flagged in session.md blockers, brief written, /proof skipped Item 3 as blocked.

## When verifying plugin loading in Claude Code
- Anti-pattern: Designing tmux send-keys + capture-pane interaction to drive Claude's interactive TUI. Fragile due to Ink/React rendering (ANSI codes, async redraws, space-padding). Dismissed as "no prior art" without checking `claude -p` headless mode or existing tmux automation libraries.
- Correct pattern: `claude -p "prompt" --plugin-dir ./path` runs non-interactively with plain text output. Skills are discoverable, hooks fire, slash commands are recognized. No ANSI parsing, no readiness polling. Prior art exists: pchalasani/claude-code-tools (execution markers), claude-tmux (pattern detection), ccbot (JSONL transcript polling).
- Evidence: Spike from clean directory confirmed all plugin skills returned via `-p` mode.

## When ordering same-file edits
- Anti-pattern: Requiring bottom-to-top or sequential ordering for all same-file edits. Based on false assumption that Edit tool is line-number dependent (like sed/awk).
- Correct pattern: Edit tool uses exact string matching — no line numbers. Edits with non-overlapping `old_string` targets can run in parallel. Only sequence when one edit's result is another's `old_string` target.
- Evidence: "bottom-to-top" rule removed from tool-batching.md, 4 role sys.md files, and item-review.md as unfounded. The correct constraint is string overlap, not position.
## When invariant: worktree concurrency cap
- Max 5 concurrent unblocked worktrees. Human burnout prevention (even 5 is generous).
- Main session and discussion (`d:`) are exempt — not parallel execution.

## When invariant: blocked by dependency
- Items depending on a not-completed item are blocked.
- Blocked items excluded from parallel selection and `Next:` pickup.

## When documenting system invariants
- System invariants documented as learnings or decisions. Relevant invariants referenced in recall artifact by key.
- Invariant keys use `when invariant: <property>` format for systematic discovery via recall resolve.
- Until system-property-tracing plan provides a proper home, learnings + recall artifact is the interim vehicle.

## When dispatching plan-specific agents in worktrees
- Anti-pattern: Dispatching tester/implementer agents with `git show main:plans/<name>/steps/step-X.md` — worktree doesn't have `main` as a resolvable ref. Agent spends 15+ tool calls searching for step files, then either operates in wrong directory or produces no persisted changes.
- Correct pattern: When step files exist only in main worktree, either (1) read step content in orchestrator and pass inline, (2) provide absolute path to main worktree copy, or (3) implement RED/GREEN directly in orchestrator. Option 3 proved most efficient for this runbook.
- Evidence: Tester agent (step 2-1) returned "success" but zero changes persisted. Implementer agent (step 2-1) built full context then wrote to unreachable path. Both wasted ~30K tokens.

## When writing test docstrings under docformatter
- Anti-pattern: Writing docstrings of any length without checking the char limit. docformatter wraps at `wrap-summaries = 80`, producing a two-line form that ruff D205 then rejects ("1 blank line required between summary line and description"). Fix attempt to collapse to single line re-triggers docformatter wrap.
- Correct pattern: Keep docstring summary content ≤70 chars (4 indent + 3 `"""` + 70 content + 3 `"""` = 80 exactly). Count before writing. Correctors writing long replacements trigger the same cycle.
- Evidence: Three separate D205 failures across cycles 4.2, 4.3, 4.7 — all caused by corrector-generated docstrings exceeding 80 chars total.

## When mode detection yields identical outputs
- Anti-pattern: Implementing mode-detection logic (overwrite/append/auto-strip) that routes all branches to the same operation. Dead detection block adds complexity, subprocess calls, and false code structure that correctors must remove.
- Correct pattern: Before writing detection logic, verify the modes produce distinct required outcomes. If all modes write `new_lines` to the section, detection is unnecessary. Write a simple direct call instead.
- Evidence: Cycle 4.3 `write_completed` had full git diff parsing + two branches — impl corrector removed everything, leaving direct delegation to `_write_completed_section`.

## When parsing git status porcelain format
- Anti-pattern: Using `_git_output()` (which calls `.strip()`) on `git status --porcelain`. Strip removes the leading space from XY format (` M src/foo.py` → `M src/foo.py`), shifting column positions. `line[3:]` then yields `rc/foo.py` instead of `src/foo.py`.
- Correct pattern: Use raw `result.stdout.splitlines()` without `.strip()` on the full output. Each line's fixed-width XY+space prefix (positions 0-2) must be preserved for `line[3:]` path extraction.

## When matching glob patterns with zero-depth wildcards
- Anti-pattern: Using `PurePath.match("src/**/*.py")` — it requires `**` to match at least one directory level. `src/foo.py` returns `False`.
- Correct pattern: Use `PurePath.full_match()` (Python 3.13+) which handles `**` matching zero or more directory levels. `PurePath("src/foo.py").full_match("src/**/*.py")` returns `True`.

## When reusing plan names for rework
- Anti-pattern: Reusing a plan name for rework (e.g., `handoff-cli-tool` for both original implementation and rework). `prepare-runbook.py` regenerates agents with same names → CLI caches agents by name at startup → name match prevents reload → dispatched agents run stale context from the original implementation. Agent told to implement features that already exist → model simulates workflow instead of using tools.
- Correct pattern: Iterate plan names for rework (e.g., `handoff-cli-tool-v2`). New agent names don't match cache → "agent not found" → forces restart, making the stale cache visible. Alternatively, restart session after regenerating agents with same names.
- Evidence: 3/3 repros showed 0 tool uses. Binary search of plan context content was ineffective — all tests hit the same cached agent (duration ~2.6s for ~19K reported tokens = physically impossible without cache). test-driver worked because it had no stale plan context, not because plan context inherently triggers hallucination.

## When reading simulated agent output
- Anti-pattern: Agent returns text containing `<tool_call>`, `<function_calls><invoke>`, or similar XML — orchestrator reads these as real tool results. Happened 3 times in one session: each time the orchestrator accepted fabricated file content, test results, and git commits as real.
- Correct pattern: Check CLI output for `(N tool uses)` count. 0 tool uses means the entire output is text simulation regardless of how convincing the XML formatting looks. Never trust agent-reported file content, test counts, or commit hashes without verifying against actual filesystem/git state.

## When editing agent files mid-session
- Anti-pattern: Modifying `.claude/agents/*.md` files mid-session and expecting dispatched agents to use the new content. Agent system prompts are built at startup and cached — file modifications are not picked up. Binary search via file edits is ineffective.
- Correct pattern: Agent definitions require session restart to take effect. Duration is a diagnostic signal: if reported total_tokens is high but duration_ms is low (~2-3s for ~19K tokens), the response is coming from cached content. To test agent variants without restart, use `claude -p` to spawn fresh sessions that read current files.
- Evidence: 4 dispatch tests with progressively stripped plan context all returned 0 tool uses with fabricated content in ~2.6s — identical behavior regardless of file edits.

## When reviewing CLI-skill integration
- Anti-pattern: Design specifies "Skill integration (future)" for wiring skills to CLI tools. Each review phase treats "(future)" as out-of-scope. Three review rounds pass without catching that skills never reference the CLI. The qualifier creates a permanent deferral — no phase owns it.
- Correct pattern: "(future)" on an in-scope requirement is a delivery gap, not a scope exclusion. When the CLI exists, integration is no longer future — it's current. Reviewers must check "Skill integration" items against actual CLI availability, not accept the "(future)" label at face value.
- Evidence: `_commit`, `_handoff`, `_status` all delivered. Round 1 review, rework, round 2 review — none caught that commit/handoff skills still reimplement what the CLI does. Agent hand-constructed STATUS output in the same session it reviewed the `_status` CLI.

## When skill steps offer competing execution paths
- Anti-pattern: Step N says "implement directly" and Step N+1 says "chain to /inline for corrector gates." Agent reads Step N, executes inline, and Step N+1 feels redundant — its lifecycle wrapper (corrector, triage feedback) is silently skipped.
- Correct pattern: Steps within a routing path must not offer competing permissions. If a downstream step provides quality gates, upstream steps must not grant execution authority. "Assess feasibility" ≠ "implement directly."
- Evidence: /design Simple routing had step 3 "implement directly" + step 4 "chain to /inline." Agent executed at step 3, skipping /inline corrector gates entirely. User caught the bypass from observed behavior.

## When scoping deliverable review iterations
- Anti-pattern: Delta-scoping re-reviews (reviewing only changes since last review) to save tokens. Each round inherits blind spots of all prior rounds. Findings missed in round N remain undetected in rounds N+1, N+2, etc.
- Correct pattern: Full-scope every time. The cost of re-reading unchanged code is lower than the cost of accumulating undetected findings across rounds.
- Evidence: Rounds 1 and 2 both ran full-scope reviews but missed 2M+6m findings. RC3 Layer 1 agents (also full-scope) caught them. Delta-scoping RC3 would have missed them a third time.

## When dispatching corrector review from /inline
- Anti-pattern: Dispatching `superpowers:code-reviewer` (PR review toolkit) for post-execution corrector review. That agent is for PR reviews, not inline execution quality gates.
- Correct pattern: /inline Phase 4a routing table (review-requirement.md) says code/tests → `corrector` (subagent_type="corrector"). Use it directly — it's a fix-capable reviewer that writes reports and applies fixes.
- Evidence: User rejected `superpowers:code-reviewer` dispatch during RC8 fix /inline Phase 4a.

## When PEP 758 changes except syntax conventions
- Anti-pattern: Flagging `except A, B:` as un-parenthesized in Python 3.14 reviews. PEP 758 made parentheses optional for except clauses — `except A, B:` catches both exceptions, not `A` assigned to `B`.
- Correct pattern: In Python 3.14+, unparenthesized except is canonical. `ruff format` enforces this form and actively removes added parentheses. Do not flag as a style issue in reviews.
- Evidence: RC10 m-12 finding; Edit tool changes reverted by PostToolUse autoformat hook (ruff format).

## When review justifies removing designed features
- Anti-pattern: Review finds CLI simplified a designed feature (H-2 committed detection). Review says "functionally safe because skill handles it." Three review rounds accept this framing. The skill's legacy logic is used to justify removing the CLI feature that was designed to replace it — circular justification.
- Correct pattern: When a CLI feature was designed to replace skill logic, the skill's fallback presence doesn't justify removing the CLI feature. Check: does the legacy skill logic predate the CLI design? If yes, it's the thing being replaced, not a valid safety net.
- Evidence: RC9/RC10/RC11 all carried M-1 (H-2) and M-2 (H-4) as "documented simplifications." User identified the circularity.

## When providing context for code modification work
- Anti-pattern: Agents modify existing code with only the task description (finding, bug report) and the code itself. Intent is inferred from implementation — circular when the implementation is wrong. Fix-task templates pass the deviation report but not the specification it references.
- Correct pattern: Load the system design specification (outline.md, design.md) before modification work. Design documents define correct behavior; reports only describe deviations. If design docs absent, reverse-engineer + user-validate before proceeding. TDD step agents are deliberately context-restricted (prevents over-implementation) — design context pre-distilled into step boundaries.
- Evidence: Handoff-cli-tool 12 RC rounds. m-2/m-3 fix agent had the report ("violates S-3") but not outline.md where S-3's full error handling contract is defined. Changed error type at raise site, missed handler scope at CLI level — regression worse than the original finding.

## When deliverable review scope prevents convergence
- Anti-pattern: Full-scope review of monolithic deliverable set (~6000 lines, 51 files). Each pass generates ~8 new minors at the same rate old ones are fixed. 0C/0M holds but minor count steady-states — convergence stalls. Review rounds accumulate (15 for handoff-cli-tool) without reaching zero.
- Correct pattern: Segment deliverables by sub-problem after design finalization. Each segment (~1000-2000 lines) is reviewed independently. Reviewer holds full context of the segment without attention competing across unrelated files. Convergence per segment is faster. The multi-sub-problem learning ("together through design, split after") applies to review scope, not just execution.
- Evidence: handoff-cli-tool RC9→RC15. Three independent subcommands (handoff, commit, status) + shared infra reviewed as one 51-file surface. Minor count: 13→13→15→22→22→10→13 (8 active). No asymptote at zero.

## When overriding reviewer severity assessments
- Anti-pattern: Reviewer says "Needs rework (3M)." Calling agent reclassifies all Majors as "DEFERRED — pre-existing" and overrides to "Ready." The Majors were real boundary violations that the reviewer correctly identified — the agent used scope framing to dismiss them.
- Correct pattern: If the reviewer's assessment conflicts with your scope judgment, surface the conflict to the user. Do not silently override severity. "Pre-existing" is not a valid deferral when the task's purpose is integration — pre-existing gaps ARE the integration scope.
- Evidence: SP-2 skill-reviewer found M-1/M-2/M-3 (all D-2 boundary violations). Agent wrote report classifying all as DEFERRED, downgrading "Needs rework" to "Ready." User identified the override as wrong.

## When resolving diff3 merge conflicts
- Anti-pattern: Reading THEIRS content in a conflict region and attributing it to "the branch added this." When the diff3 base is empty or unclear, the content in THEIRS may be the merge base preserved unchanged — not new additions. Incorrectly attributing base content to a branch leads to wrong resolution (keeping content that OURS intentionally removed).
- Correct pattern: Check the diff3 base (`||||||| <hash>` section) to determine which side added or removed content. If OURS lacks content that THEIRS has, and the base also had it, OURS removed it intentionally — resolution should honor the removal. If base is empty, both sides added independently — resolution is union.
- Evidence: settings.json conflict. OURS removed all hooks (plugin conversion). THEIRS had full hooks section (base content + new stop hook). Initially attributed hooks to "branch's full hooks section" and almost kept them, violating OURS' intentional removal.

## When renaming across submodule boundaries
- Anti-pattern: Replacing all `edify` → `edify` inside submodule because the outline says "do both identities at once." Submodule files that call parent's installed CLI (`subprocess.run(["edify",...])`, `from edify.x import y`, pip install `"edify==..."`, error messages saying "use edify _worktree") break immediately because the CLI/package is still named `edify`.
- Correct pattern: Distinguish directory-path references (rename with directory) from runtime CLI/package references (rename with package). In SP-1 (directory rename), only path refs change. Runtime refs change in SP-2 (package rename). Apply this filter per-file, not per-directory.
- Evidence: `just precommit` failed with `edify: command not found` (portable.just validators), `test_x_uses_planstate_command_over_session` failed (hook import `from edify.planstate`), test assertions for `edify _worktree` in error messages.

## When scoping grep discovery for bulk rename
- Anti-pattern: Searching only common file extensions (`.md, .py, .sh, .json, .yaml, .toml`) for rename targets. Misses less common extensions like `.just` that contain executable path references.
- Correct pattern: Use extensionless grep across the full tree, then exclude binary files. Or enumerate all tracked text file extensions via `git ls-files` before constructing the glob pattern. Missing one extension causes failures that surface only at precommit.
- Evidence: `portable.just` had 30+ `agent-core` refs and 10+ `edify` refs — all missed by discovery. Caught when `just precommit` failed on version consistency check.