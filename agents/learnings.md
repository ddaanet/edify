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
## When assuming interactive context
- Anti-pattern: Assuming orchestration is interactive (user watching, can ctrl+c hung agents). Designing timeout as low-priority because "human-in-the-loop provides timeout for free."
- Correct pattern: Orchestration is unattended — user focuses on design/workflow work elsewhere. Timeout is a real operational requirement, not a nice-to-have. Calibrate from historical data.
- Rationale: The operational model determines which error handling mechanisms are needed. Wrong assumption about attended vs unattended cascades into under-specifying timeout, recovery, and notification.
## When classifying errors by tier
- Anti-pattern: Moving ALL error classification to orchestrator because haiku can't classify. Sweeping change that ignores capable agents.
- Correct pattern: Tier-aware classification — sonnet/opus execution agents self-classify and report classified error; haiku agents report raw errors for orchestrator to classify. Preserves context locality for capable agents.
- Rationale: Execution agent has full error context (stack trace, file state). Transmitting to orchestrator for classification loses fidelity or costs tokens. Orchestrator already knows agent model tier.
## When analyzing task insertion patterns
- Anti-pattern: Assuming all single-task insertions share the same urgency profile. Overall data (n=65) showed 61.5% prepend, suggesting "always prepend" is natural behavior.
- Correct pattern: Segment by origin. `p:` directives (n=29) distribute evenly (34.5% prepend). Workflow continuations dominate the prepend signal. Different insertion policies needed per origin type.
- Evidence: Session scraping + git correlation across 337 sessions, 506 commits. Handoff skill says "append" but agents correctly override for both populations.
- Implication: Handoff skill should say "insert at estimated priority position" not "append" — agents already exercise good judgment.
## When measuring agent durations
- Anti-pattern: Computing duration as timestamp delta between tool_use and tool_result — includes laptop sleep time, producing 10-hour "outliers" that are artifacts
- Correct pattern: Use `duration_ms` from Task result metadata when available (post-W06 2026, ~42% coverage). For all entries with both duration and tool_uses, validate via seconds-per-tool-use rate (normal p50=6.6s/tool). Flag entries >30s/tool as sleep-inflated.
- Rationale: `duration_ms` is wall-clock computed by CLI process — suspended process = inflated time. Cross-referencing with tool_uses exposes the inflation. 13/951 entries flagged, all confirmed artifacts.
## When designing timeout mechanisms
- Anti-pattern: Treating "dual signal" (time OR tool count) as reducing false positives. OR-logic is the union of both kill zones — it increases false positives vs either threshold alone.
- Correct pattern: Time and tool count address independent failure modes. Spinning (high activity, no convergence) → `max_turns`. Hanging (no activity, high wall-clock) → duration timeout. Independent guards, not a combined signal.
- Evidence: OR(600s, 90 turns) would false-positive on the 855s/75-tool legitimate agent AND the 495s/129-tool agent. AND logic misses fast spinners.