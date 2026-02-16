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