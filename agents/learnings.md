# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## When visible primitives enable decomposition
- Anti-pattern: Loading all justfile recipes into agent context via @-reference — primitives (wt-rm, wt-merge) visible alongside skills that wrap them
- Correct pattern: Curate in-context recipe list to essential commands only. Primitives exist as fallback but aren't in agent's active context
- Rationale: Agent reads skill, understands internals, selects "simpler" primitive that lacks side effects (session.md updates). Rule additions fail (4 instances same pattern) because rules compete for attention. Structural fix: reduce primitive visibility
- Fix: CLAUDE.md @.cache/just-help*.txt → inline 5-recipe list; removed cache infrastructure entirely
## When shortcuts bypass upstream steps
- Anti-pattern: Pre-evaluating whether a shortcut's chain has work to do (e.g., `hc` → check git status → clean → skip handoff entirely)
- Correct pattern: Invoke the expansion directly. Each step in the chain creates preconditions for the next. Checking downstream preconditions before running upstream steps aborts chains that would have succeeded.
- Same class as "execute directly" deviation — premature termination of multi-step chains based on downstream precondition evaluation
- Fix: execute-rule.md Tier 1 shortcuts section: "Shortcuts are mechanical expansions — invoke directly. Do not pre-evaluate."
## When execute directly skips safety
- Anti-pattern: Design skill triage → "Simple → execute directly" → skip skill checks, recipe checks, cwd rules
- Correct pattern: "Execute directly" means skip design ceremony, not skip operational rules. Skill-check-first and recipe-check-first still apply.
- Root cause: "Simple" classification creates execution mode that optimizes throughput by rationalizing away ALL friction, not just design-level ceremony
- Fix: Design skill Simple path updated to say "Check for applicable skills and project recipes first, then execute directly"
## When orchestrator handles review delegation
- Anti-pattern: Expecting execution agents to delegate review (to any reviewer, not just plugin-dev)
- Correct pattern: Orchestrator delegates ALL reviews after execution agents commit
- Rationale: (1) Sub-agents lack Task and Skill tools — cannot delegate to any reviewer. (2) All reviews must be delegated to prevent implementer bias — implementer never reviews own work. Domain-specific routing: vet-fix-agent (code), skill-reviewer (skills), agent-creator (agents), plan-reviewer (planning), vet-fix-agent + doc-writing skill (human docs). See artifact review routing table in pipeline-contracts.md.
## When deliverable review catches drift
- Anti-pattern: Relying solely on per-step vet reviews for quality assurance
- Correct pattern: Post-orchestration deliverable review catches inter-file consistency gaps (stale copies, broken references, missing cross-references) that per-step vet misses
- Evidence: memory-index skill drifted during execution (3 entries missing); workflows-terminology.md referenced non-existent agent; runbook skill missing general-patterns.md reference
- These were invisible to per-step vet because each step's artifacts were internally consistent
## When writing methodology
- Anti-pattern: Producing scoring frameworks, evaluation axes, or "best practice" documents from internal reasoning alone — yields confabulated methodologies with subjective weights and ungrounded criteria
- Correct pattern: Invoke `/ground` skill. Diverge-converge with parallel branches: internal (brainstorm for project-specific dimensions) + external (web search for established frameworks). Synthesize by mapping internal dimensions onto external skeleton.
- Evidence: First prioritization attempt produced subjective weights ("Highest/High/Medium") and 0-3 scores without defined criteria. After grounding in WSJF research, methodology used Fibonacci scoring with observable evidence sources.
## When research deliverables misplaced
- Anti-pattern: Writing research synthesis documents to tmp/ — they're ephemeral and won't survive across sessions
- Correct pattern: Research deliverables that inform future work go to plans/reports/ (persistent, tracked). Only scratch computation goes to tmp/.
- Rationale: tmp/ is gitignored. Research synthesis is a reusable artifact referenced by skill creation and future prioritization runs.
## When relaunching similar task
- Anti-pattern: Launching a fresh agent with the same prompt after a stopped/killed agent, losing prior context
- Correct pattern: Use Task tool's `resume` parameter with the prior agent's ID. The agent retains full prior context (files read, reasoning done) and continues from where it stopped.
- Rationale: Stopped agents may have completed expensive operations (file reads, web searches). Resuming preserves that work; relaunching repeats it.
## When naming triggers
- Anti-pattern: Naming `/when` triggers after the anti-pattern, outcome, or self-assessment ("When synthesizing ungrounded methodology", "When deliverable review catches drift", "When resuming killed agents")
- Correct pattern: Name triggers after the **activity at the decision point** — what the agent is doing when it needs the knowledge. Use the broadest verb that still triggers correctly. No self-assessment terms (agent can't evaluate what it doesn't know).
- Examples: "When writing methodology" not "When synthesizing ungrounded methodology". "When relaunching similar task" not "When resuming killed agents".
- Same principle as `/when choosing name`: discovery and recall over precision.
## When reviewing skill structure
- Anti-pattern: Delegating deliverable review to Task agent — agent lacks cross-project context (other skills' allowed-tools, fragment conventions, memory index patterns)
- Correct pattern: Interactive review with full context (CLAUDE.md fragments, learnings, memory index loaded). The reviewer needs to compare against project-wide patterns, not just the artifact's internal consistency.
- Evidence: Task agent found 5 minor issues but missed the major finding (Write missing from allowed-tools). Only detectable by comparing against 18 other skills' allowed-tools fields.
## When writing CLI output
- Anti-pattern: CLI suggesting destructive commands in output (e.g., `"use: git branch -D <slug>"`). LLM agents treat CLI output as instructions and execute the suggested command.
- Correct pattern: Report the problem without prescribing destructive workarounds. Let the calling agent or user decide the action. CLI should refuse destructive operations, not suggest them.
- Evidence: `_worktree rm` suggested `git branch -D` for unmerged branch. Agent followed the instruction, permanently deleting the only copy of unmerged parent repo changes.
## When analyzing task insertion patterns
- Anti-pattern: Assuming all single-task insertions share the same urgency profile. Overall data (n=65) showed 61.5% prepend, suggesting "always prepend" is natural behavior.
- Correct pattern: Segment by origin. `p:` directives (n=29) distribute evenly (34.5% prepend). Workflow continuations dominate the prepend signal. Different insertion policies needed per origin type.
- Evidence: Session scraping + git correlation across 337 sessions, 506 commits. Handoff skill says "append" but agents correctly override for both populations.
- Implication: Handoff skill should say "insert at estimated priority position" not "append" — agents already exercise good judgment.
## When running multi-reviewer diagnostics
- Anti-pattern: Running a single reviewer and trusting all findings. Exploration agents produce false positives from over-reading (e.g., "line number wrong" when insertion point was correct); opus reviewers miss implementation-level issues (e.g., helper function return value semantics).
- Correct pattern: Run 3+ independent reviewers in parallel (opus review, exploration, inline RCA against source code). Cross-reference findings — real issues appear in multiple or survive verification against source. False positives get filtered by disagreement.
- Evidence: 3-way review of runbook-phase-1.md found 8 real issues (each reviewer found unique ones) and filtered 2 false positives. Exploration flagged "critical" line number issue that was correct; opus missed `_git()` return value issue only caught by reading source code directly.
## When performing root cause analysis
- Anti-pattern: Finding first cause and jumping to solution (e.g., "expansion has defects → add more review rounds")
- Correct pattern: Multi-layer RCA with explicit stops between layers. L1: what are the symptoms? L2: what caused them? STOP. L3: why was that cause allowed? STOP. Only then does the fix address the cause, not the symptoms.
- Evidence: Merge data loss RCA — L1: bugs in code. L2: haiku generated safety-critical code. L3: delegation model assigns by type not risk + no review gate covers behavioral safety. Fix: model floor for Tier 1 steps AND safety criteria in vet.
## When building custom pipeline infrastructure
- Anti-pattern: Building custom review/workflow infrastructure without checking what the platform already ships
- Correct pattern: Inventory platform-provided plugins and features first. Build custom only for gaps. Anthropic ships 28 official plugins including code-review, feature-dev, security-guidance, commit-commands, claude-md-management.
- Rationale: Custom infrastructure diverges from platform evolution. Official plugins get maintained, updated, and integrated. Reinvention wastes effort and creates maintenance burden.
## When searching adjacent domains
- Anti-pattern: Narrowing search to one domain after user feedback (e.g., "not security?" → drop all security searches). Interpreting correction as exclusion rather than asking for clarification.
- Correct pattern: When user questions missing coverage ("not X?"), they may mean "why no X?" not "exclude X." Safety and security are adjacent — both warrant research even when the triggering incident is one or the other.
- Evidence: User said "not security?" meaning "why aren't you searching for security too?" — interpreted as "this isn't about security" and dropped security entirely.
## When git operation fails
- Anti-pattern: Attributing git failure to a plausible-sounding restriction without reading the error message. Confabulated "git refuses to merge with active worktree" (false). Actual cause: untracked session.md on main would be overwritten by merge. Built reasoning chain on false premise, deleted test coverage to work around the non-existent limitation.
- Correct pattern: Read actual error output. Reproduce with a minimal case before restructuring. Test failures that seem like infrastructure problems may reveal real production bugs — the test was correctly detecting that `new --session` leaves session.md untracked on main.
- Deeper pattern: Confabulation served as license to stop investigating. A "can't be fixed" explanation converts a solvable problem into an unsolvable one, justifying coverage-reducing workarounds.
## When selecting model for TDD execution
- Anti-pattern: Assigning model by task type (execution = haiku) without considering reasoning complexity. Haiku over-implemented step 1-2, building guard logic meant for 6 subsequent steps.
- Correct pattern: Assign model by complexity type: pattern complexity (regexp, wiring, flags) → haiku fine; state machine complexity (git ancestry, merge state) → sonnet minimum; synthesis complexity (trade-offs, architecture) → opus. Classification happens during /runbook expansion, not at orchestration time.
- Related: TDD granularity doesn't help haiku — each step is "simple" but haiku can't stay within scope. Batching code+tests per phase at sonnet produces fewer, better tests with opus review.
## When precommit fails
- Anti-pattern: Rationalizing past precommit failure ("lint issues are pre-existing", "my changes are clean"). Deeper: `just precommit` was broken for 9 days (~845 commits) due to non-existent `claudeutils validate` command. No agent noticed because failure was rationalized or bypassed each time.
- Correct pattern: Precommit is a gate. If it fails, fix before committing. A broken gate is worse than no gate — creates false confidence across all subsequent commits.
- Systemic: No health check verifies gates themselves are functional. Pipeline assumes `just precommit` works. Silent breakage accumulates unverified commits.
## When test setup steps fail
- Anti-pattern: Using `subprocess.run(..., check=True, capture_output=True)` in test setup — CalledProcessError shows command and exit code but stderr is swallowed. Opaque failures invite confabulation.
- Correct pattern: Test setup should produce self-diagnosing failures. Either use `check=False` + explicit assertion with stderr, or use a helper that surfaces stderr on failure.
- Evidence: `git merge` failed with "untracked working tree files would be overwritten" but test only showed `CalledProcessError: exit status 1`.
## When choosing model for edits
- Anti-pattern: Assigning sonnet/haiku to prose edits on skills, fragments, and agent definitions based on "edit complexity" rather than artifact type
- Correct pattern: Apply design-decisions.md directive: "Workflow/skill/agent edits: opus required." Prose instructions consumed by LLMs require nuanced understanding — wording directly determines downstream agent behavior
- Evidence: Tier 2 plan assigned sonnet to skill/fragment edits, haiku to agent audit. User corrected: all were prose edits to architectural artifacts requiring opus
## When placing quality gates
- Anti-pattern: Ambient rules in always-loaded fragments (vet-requirement.md) telling agents to review artifacts. Unenforceable — agents rationalize skipping under momentum. Sub-agents don't see CLAUDE.md fragments at all.
- Correct pattern: Gate at the chokepoint (commit). Scripted check (file classification + report existence) blocks mechanically. No judgment needed at the gate. Orchestrator handles mid-pipeline vet delegation separately.
- Rationale: Ambient rules without enforcement are aspirational. Gating at commit captures all work. ~100 lines of always-loaded context eliminated for no behavioral loss.
## When reviewing runbooks after expansion
- Anti-pattern: Relying on text-based review (plan-reviewer) to catch all runbook defects. Text review validates TDD discipline, prescriptive code, vacuity — but misses execution-time concerns.
- Correct pattern: Add structural validation after text review: (1) file lifecycle graph (create→modify ordering), (2) RED plausibility (expected failures valid given prior GREEN), (3) test count reconciliation (checkpoint numbers match test functions). File lifecycle and test count are deterministic (scriptable). RED plausibility may need LLM judgment.
- Evidence: Holistic review caught formatting/metadata issues and one dependency ordering bug, but would not have caught an "already-passing RED" from cycle consolidation.
## When batching runbook cycles
- Anti-pattern: Planning 4 identical-pattern cycles separately (e.g., 4 status levels each adding one artifact check to the same function), then optimizing post-hoc.
- Correct pattern: Detect identical patterns during Phase 1 expansion and consolidate upfront. Indicators: same function modified, same test structure, only the fixture data differs. Parametrized cycle with table of inputs replaces N separate RED/GREEN rounds.
- Evidence: Workwoods P1 cycles 1.2-1.5, P5 cycles 5.5-5.7, P4 cycles 4.3-4.6 all exhibited this pattern. Post-hoc optimization saved 12 items but required 5 parallel agents + holistic re-review.
## When choosing consolidation timing
- Anti-pattern: Consolidating after expensive expansion (Phase 1.5 on expanded phase files). Wastes expansion cost on items that will be merged.
- Correct pattern: Consolidate at the earliest pipeline point where patterns are detectable. Identical patterns (same function, varying fixture data) are visible from outline titles — expanded RED/GREEN detail not needed for detection.
- Evidence: Workwoods patterns ("add artifact detection for status A/B/C/D") detectable from outline one-liners. Moving consolidation from Phase 1.5 to outline level (after Phase 0.85) saves expansion cost for ~12 items.
## When splitting validation into mechanical and semantic
- Anti-pattern: Bundling deterministic checks (file path → model mapping) with judgment-based checks (task complexity assessment) in a single agent pass.
- Correct pattern: Script handles deterministic checks (Phase 3.5 subcommand, blocking). Agent enriches existing review for semantic checks (plan-reviewer criteria, advisory). Different enforcement layers for different failure modes — defense-in-depth.
- Evidence: FR-2 model review split. File path matching (agent-core/skills/ → opus) is scriptable with zero false positives. Semantic complexity ("is this synthesis?") requires plan-reviewer judgment during existing Phase 1 per-phase review.
## When resolving session.md conflicts during merge
- Anti-pattern: Using `git checkout main -- agents/session.md` to resolve conflicts — discards all branch-side session data (new tasks, metadata) without verification
- Correct pattern: After any session.md conflict resolution, read the full file and compare against known task list. Verify no tasks were dropped. Branch session.md may contain tasks added during worktree work that don't exist on main.
- Evidence: "Simplify when-resolve CLI" task existed only in worktree-merge-errors branch session.md. `checkout main --` silently dropped it. Caught only because user requested explicit content verification.
## When tests simulate merge workflows
- Anti-pattern: Creating worktree branch at the merge commit (same SHA as HEAD) instead of as a merged parent. After `git commit --amend`, the branch points to the old (orphaned) commit — `git branch -d` correctly refuses.
- Correct pattern: Test should make the worktree branch the one that gets merged. Its tip becomes a parent of the merge commit, preserved through amend (amend keeps parents, only rewrites tree content).
- Evidence: `test_rm_amends_merge_commit_when_session_modified` created "test-feature" at HEAD, not as the merged branch. `-d` failed post-amend. Real workflow: branch is merged parent, always reachable.
## When safety checks fail in tests
- Anti-pattern: Weakening a safety check (`-d` to `-D`) to make tests pass. If `git branch -d` correctly identifies unreachable commits, the problem is upstream (test scenario or code ordering), not in the check itself.
- Correct pattern: Understand why the safety check fires. If the test scenario is unrealistic, fix the test. If code creates the problem (e.g., amend before delete), fix the ordering. Safety checks that detect merge parent loss are critical — suppressing them masks data loss.
## When removing worktrees with submodules
- Anti-pattern: `wt rm` removes worktree directory but leaves `.git/modules/agent-core/config` `core.worktree` pointing to the deleted directory. Also doesn't check if submodule branch has unmerged commits (parent repo branch merged but submodule branch diverged).
- Correct pattern: `wt rm` must (1) restore submodule's `core.worktree` to main checkout path, (2) check submodule branch merge status before deletion. Both are data-loss vectors — stale config breaks all submodule operations, unmerged submodule branch loses commits.
- Evidence: `git -C agent-core` failed with "cannot chdir to removed directory" after `wt rm runbook-skill-fixes`. Agent-core branch had 3 files of real diffs silently orphaned.
## When importing artifacts from worktrees
- Transport: `git show <branch>:<path>` from main — no cross-tree sandbox access needed. All worktrees share the git object store.
- Scope: Only design.md and requirements.md are import candidates (small, authored). Runbooks (phase files, steps, orchestrator plans) are bulky, generated, implementation-oriented — require explicit intent, not casual import.
- Ownership check: Before importing, verify no active worktree owns the target plan directory (`git worktree list` + check branch names). Importing into a worktree-owned plan creates merge conflicts when that worktree merges back.
- Supersedes: "When worktree agents need cross-tree access" learning (additionalDirectories unnecessary for transport).
## When hitting file line limits
- Anti-pattern: Compressing user-facing output strings or splitting to new files to pass line-count checks. Both responses degrade quality (output clarity, module cohesion) without addressing the underlying problem.
- Correct pattern: Look for code quality improvements first — redundant calls, dead code, extraction candidates, helper functions that encode repeated kwargs. Black expansion of 5+ line call sites signals too many parameters for inline use — extract a helper.
- Evidence: worktree/cli.py 401→400 via output compression (reverted). Actual fix: dedup redundant `rev-parse --show-toplevel` call (401→399). Grounding: `plans/reports/code-density-grounding.md`.
## When lint rule requires code change
- Anti-pattern: Circumventing lint with mechanical transformations that satisfy the checker without improving the code. Example: `msg = "..."; raise ValueError(msg)` to dodge "no hardcoded exception messages" — the real problem is using `ValueError` for domain errors.
- Correct pattern: Fix the underlying design problem the lint rule is pointing at. "No hardcoded exception messages" → create a custom exception class. "Function too long" → extract helpers, not compress strings.
- Rationale: Lint rules surface design problems. Mechanical circumvention preserves the design problem while removing the signal.
## When workaround requires creating dependencies
- Anti-pattern: Escalating workarounds for a tool limitation — each fix creates a new problem requiring another fix. Pre-resolving merge conflict → import error → recreating entire module tree from branch. Each step locally rational, trajectory absurd.
- Correct pattern: If a workaround requires more than 2 steps or introduces new dependencies, stop and report the tool limitation. "Pre-resolve conflict" is bounded: edit the conflicting regions of files that ALREADY EXIST on both sides. Creating new files, new modules, or new dependency chains means you've left "pre-resolution" and entered "manual reimplementation."
- Deeper pattern: Sunk cost momentum — each workaround invests more context, making "just one more fix" feel cheaper than stopping. The "stop on unexpected results" rule doesn't fire because each step is rationalized as part of the documented workaround path.
- Evidence: 6-step escalation chain during design-workwoods merge. Two commits on main, partially-created planstate module, still not merged.
## When running git merge in sandbox
- Anti-pattern: Running `git merge` without `dangerouslyDisableSandbox: true`. Git's ort strategy partially checks out files from the incoming branch into the working tree BEFORE completing the merge. If it hits a sandbox restriction mid-checkout, the merge fails but the partially-checked-out files remain as untracked debris. Subsequent merge attempts fail because "untracked working tree files would be overwritten."
- Correct pattern: Never run `git merge` directly — use `claudeutils _worktree merge` which handles sandbox bypass. If the tool can't handle the merge, STOP and report. Don't fall back to raw git operations.
- Deeper pattern: "Tool fails → I become the tool" — seamlessly replacing tool operations with manual commands, losing the tool's invariants (atomicity, sandbox handling, session.md updates, precommit validation). Each manual step is locally correct but collectively bypasses the pipeline's safety guarantees.
## When resuming interrupted orchestration
- Anti-pattern: Using `just precommit` as state assessment after ceiling crash → chasing cascading failures reactively → bypassing recipes under accumulated momentum (used `uv run ruff check` instead of `just check`)
- Correct pattern: Resume from last runbook checkpoint. Run checkpoint verification commands (designed as diagnostic inventory). Systematically fix remaining items. Verify with project recipes.
- Root cause chain: No ceiling recovery protocol → debugging-as-assessment → reactive fix mode → recipe bypass under urgency
- Fix: Added ceiling recovery scenario to orchestrate skill (chokepoint enforcement, not ambient rule)
## When vet flags unused code
- Anti-pattern: Flagging code as "dead" based on production callers only. `_task_summary` had 4 test callers and was designed infrastructure for future wiring — vet recommended deletion.
- Correct pattern: Check both production AND test callers before recommending removal. If tested, it's likely infrastructure awaiting integration. Verify the design intent (was it planned for future wiring?) before classifying as dead code.
- Evidence: Delegated agent followed vet recommendation and deleted the function + tests. Required manual revert.
## When delegating with corrections to prior analysis
- Anti-pattern: Including "don't do X" alongside "do Y and Z" in delegation prompts. Agent read the vet report (which recommended X), saw it in changed files, and followed the report's recommendation despite the prompt saying otherwise.
- Correct pattern: Exclude the wrong item entirely from delegation scope. Don't delegate "3 fixes but actually only do 2" — delegate 2 fixes. Remove conflicting signals by not mentioning the excluded item.
- Rationale: Delegated agents receive context from both the prompt AND the files they read. When prompt contradicts file content, file content often wins because the agent encounters it during execution with recency bias.
## When ordering post-orchestration tasks
- Anti-pattern: Jumping to pipeline improvements (design runbook evolution) before fixing deliverable findings from the current orchestration
- Correct pattern: Diagnostic/process review first, deliverable fixes second, pipeline improvements last. Current deliverable must be whole before improving the process that produced it.
- Rationale: Unfixed deliverable findings accumulate as tech debt. Pipeline improvements don't retroactively fix the current deliverable. Fixing deliverables also validates the diagnostic — the fix confirms the finding was real.
## When querying project state
- Anti-pattern: Writing ad-hoc `python3 -c "..."` scripts to call library functions, guessing at attribute names across multiple attempts
- Correct pattern: Use the project's CLI commands (`claudeutils _worktree ls` for plan/tree status). The CLI wraps library functions with formatting. Check existing CLI commands before writing ad-hoc Python.
- Deeper pattern: Procedural instructions in fragments suppress cross-cutting operational rules. When a procedure says "call X()" the agent follows it literally, skipping the project-tooling check ("does a CLI/recipe already exist?"). Specific instructions must not suppress general operational rules — the check-for-existing-tools rule applies even when a procedure names a specific function.
- Evidence: execute-rule.md said "Call `list_plans()`" → agent wrote ad-hoc Python → 3 failed attempts guessing attributes → 6-turn guided diagnostic from user. CLI existed the whole time.
## When testing CLI tools
- Anti-pattern: Testing CLI via subprocess invocation or calling `main()` with SystemExit catching. Fragile, slow, conflates process-level concerns with behavior testing.
- Correct pattern: Use Click test harness (`click.testing.CliRunner`). Invokes CLI in-process, captures output and exit code, supports isolated filesystem. Tests run faster and assertions are cleaner.
- Applies to: Any CLI built with Click (or adaptable for argparse via similar test runner patterns).
## When editing runbook step or agent files
- Anti-pattern: Editing `.claude/agents/<plan>-task.md` directly — it's a generated file assembled by prepare-runbook.py from tdd-task.md baseline + Common Context from phase-1 + phase content
- Correct pattern: Edit the source (phase files in `plans/<job>/`), then re-run prepare-runbook.py to regenerate the agent file and step files. Common Context lives in runbook-phase-1.md only — phases 2–5 don't have their own copy.
- Evidence: Edit rejected 3 times because target was the generated output, not the source.
## When concluding reviews
- Anti-pattern: Review classifies findings as Major, then adds "doesn't block merge, follow-up work" — reviewer making merge-readiness judgment and converting findings into aspirational prose nobody tracks
- Correct pattern: Review reports severity counts. Creates one pending task referencing the report → `/design`. No merge-readiness language. User reads severity counts, user decides.
- Root cause: Sycophancy in artifact form — reviewer softens its own classification to avoid blocking the pipeline. "Documented, non-blocking" is the pipeline equivalent of "great question!"
## When routing implementation findings
- Anti-pattern: Conditional dispatch based on fix size or "architectural" judgment (e.g., "small fix → direct, design gap → /requirements"). Reintroduces judgment at a stage that should be mechanical.
- Correct pattern: Unconditional `/design` for all findings. `/design` triage handles proportionality — simple fixes execute directly, complex ones get full treatment. No routing judgment at review time.
- Related: `/design` should include Phase 0 requirements-clarity gate (well-specified → triage, underspecified → `/requirements` first). Eliminates recurring "requirements or design?" routing question.
## When invoking CLI tools directly
- Anti-pattern: Using the bare/simple invocation form of a CLI when a richer form exists that automates side effects. Example: `_worktree new <slug>` instead of `_worktree new --task "Task Name"` — then manually editing session.md to compensate.
- Correct pattern: Before invoking a CLI command, check its `--help` or known options. Use the form that includes automation (session.md updates, focused sessions, validation). Manual side effects are worse, error-prone, and miss features (focused session wasn't created).
- Same class as: "When visible primitives enable decomposition", "When querying project state". Root: familiarity with the primitive suppresses discovery of the full-featured form. The simple form's visible output (worktree created) masks the missing side effects.
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