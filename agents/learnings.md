# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)
## Deliverables go to plans/
- Repeated: 2026-02-06, 2026-02-08
- Anti-pattern: Writing actionable artifacts to tmp/ which is gitignored
- Correct pattern: If artifact will be referenced in a followup session → `plans/`. If not → `tmp/`
- Decision principle: "Will this be referenced later?" — not "Is this type in a known list?"
- Recurrence cause: Category-matching heuristic ("this isn't a report/design/audit") defeats the principle. New artifact types (feature request bodies, issue drafts) bypass enumerated categories
- Contributing: `tmp-directory.md` fragment says "ad-hoc work: use tmp/" without distinguishing tracked vs untracked output
- Rationale: Commits are sync points — session.md references must resolve in the same commit
## Lightweight TDD tier assessment
- Anti-pattern: Using full runbook (Tier 3) for straightforward fixture creation with repetitive pattern
- Correct pattern: Tier 2 (lightweight TDD) for ~15-20 cycles with same pattern — plan cycle descriptions, delegate individually, checkpoint every 3-5 cycles
- Rationale: Full runbook overhead (phase files, prepare-runbook.py, orchestrator) not justified for simple repetitive work
- Example: Markdown test corpus — 16 fixtures following same pattern (input/expected pairs), completed via lightweight TDD
- Tier boundaries: Tier 1 (1-3 cycles), Tier 2 (4-10 cycles OR 10-20 repetitive), Tier 3 (>20 cycles with complexity)
## Corpus defines correct behavior
- Anti-pattern: Rewriting fixtures to avoid triggering known bugs (makes tests pass by hiding defects)
- Correct pattern: Fixtures define correct behavior — failing tests are the signal that code needs fixing
- Rationale: Test corpus purpose is detecting changes required to process corpus correctly
## excludedCommands sandbox bypass unreliable
- Anti-pattern: Relying on `excludedCommands` in settings.json for filesystem/network sandbox bypass
- Correct pattern: Use `dangerouslyDisableSandbox: true` per-call + `permissions.allow` for prompt skip
- Evidence: npm added to excludedCommands, still got EPERM on `~/.npm/_cacache/` writes
- Known issues: #10767 (git SSH), #14162 (DNS), #19135 (logic conflict)
## Pipeline idempotency over exact match
- Anti-pattern: Pipeline test asserting remark output matches preprocessor expected fixtures
- Correct pattern: Assert full pipeline idempotency — `(preprocessor → remark)²` produces same result
- Rationale: Remark legitimately reformats (table padding, blank lines) — exact match conflates preprocessor correctness with formatter style
## Temporal validation for empirical analysis
- Anti-pattern: Running analysis on session history without checking if feature existed during those sessions
- Correct pattern: Correlate session timestamps with git history to validate feature availability
- Rationale: Sessions before feature creation yield expected-zero results, invalidating analysis
- Example: Memory index created Feb 1, sessions analyzed Feb 5-8 → valid (all had access)
- Git commands: `git log --format="%ai" --follow <file>` for creation date, session mtime for analysis window
- Strengthens findings: 0% recall validated across 200 sessions, all post-creation and post-stability
## Namespace collision in prefix design
- Anti-pattern: Reusing a symbol for new semantics without checking existing conventions
- Correct pattern: Check existing notation conventions before introducing new prefix semantics
- Rationale: `.` prefix on headers means "structural section" (validated by precommit). Reusing `.` in a different namespace (command syntax like `/when .section`) is safe because contexts don't overlap
- Resolution: `/when .section` and `/when ..file` use `.`/`..` as command mode switches (not heading prefixes), avoiding collision
## Prompt caching not file caching
- Anti-pattern: Assuming Claude Code deduplicates file reads or maintains a file cache (re-reading = free)
- Correct pattern: Each Read appends a new content block to conversation; "caching" = prompt prefix matching at API level (92% reuse, 10% cost)
- Rationale: No application-level dedup. 20-block lookback window limits cache hits when many tool calls intervene
- @-references (system prompt) are more cache-efficient than Read (messages) for always-needed content
## Behavioral triggers beat passive knowledge
- Anti-pattern: `/what` and `/why` operators for definitional/rationale knowledge — LLMs don't proactively seek context
- Correct pattern: `/when` (behavioral) and `/how` (procedural) only — these prescribe action, creating retrieval intention
- Rationale: LLMs use what's in context or ignore it; they don't probe for definitions unless specifically instructed
- Consequence: If a learning can't be phrased as `/when` or `/how`, it's either a fragment (ambient) or lacks actionable content
## Fuzzy bridge: density and clarity
- Anti-pattern: Index triggers must exactly match decision file headings (forces verbose triggers or cryptic headings)
- Correct pattern: Index triggers fuzzy-compressed for density, headings stay as readable prose, fuzzy engine bridges the gap
- Rationale: "how encode path" fuzzy-matches "How to encode paths" — index saves tokens, headings stay clear
- Validator uses same fuzzy engine: each trigger must uniquely expand to one heading, each heading reachable by exactly one trigger
## Design skill lacks resume logic
- Anti-pattern: Invoking `/design` when design is mid-flight — restarts from Phase A instead of resuming
- Correct pattern: When design is in progress, manually continue from current phase (read outline, proceed to Phase B/C)
- Rationale: `/design` is linear A→B→C with no "load existing artifacts" step
- Impact: For `/when` design, outline was updated directly this session, bypassing `/design` skill
## wt-merge empty submodule failure
- Anti-pattern: `git commit` in `set -e` script with nothing staged → exits 1, kills script before next step
- Correct pattern: Guard with `git diff --quiet --cached || git commit ...`
- Broader pattern: Recipe success ≠ task success — verify git state after recipe (unmerged commits, stale branches)
- Fix: justfile line 133 guarded, 4 stale worktrees recovered
## Agent scope creep in orchestration
- Anti-pattern: Prompt says "execute step N" without scope constraint — agent reads ahead and executes step N+1
- Correct pattern: Prompt must include "Execute ONLY this step. Do NOT read or execute other step files."
- Secondary: Orchestrator must verify agent return describes only the assigned step, not additional work
- Related: Checkpoint delegations must include explicit "commit all changes before returning"
- Anti-pattern: Receive user feedback, immediately apply changes, present result
- Correct pattern: Receive feedback → rephrase understanding → ask for validation → apply
- Rationale: Misinterpreting feedback in /design leads to wrong architectural decisions; rephrase catches misunderstandings early
- Scope: Especially important in /design, but generally applicable
## Sub-agent rules file injection limitation
- Anti-pattern: Assuming vet-fix-agent (sub-agent via Task) receives rules file context injection
- Correct pattern: Rules files fire in main session only; sub-agents don't receive injection
- Consequence: Domain context must be carried explicitly — planner writes it into runbook, orchestrator passes through task prompt
- Related: Hooks also don't fire in sub-agents (documented in claude-config-layout.md)
## Planning-time domain detection principle
- Anti-pattern: Expecting weak orchestrator (haiku) to detect domain and route to specialist agents
- Correct pattern: Planner (opus/sonnet) detects domain, encodes domain skill references in runbook vet steps
- Rationale: Weak orchestrator executes mechanically; domain detection requires intelligence; Dunning-Kruger prevents runtime self-assessment of knowledge gaps
- Pattern: "encode concerns at planning time, not orchestration time"
## Structured criteria manage overload
- Anti-pattern: Splitting review across multiple agents (quality + alignment + domain = 3 invocations)
- Correct pattern: Single vet-fix-agent with domain skill file providing explicit checklists and good/bad examples
- Rationale: One agent per concern is expensive; structured skill files provide bounded criteria (not unbounded reasoning)
- Trade-off: Cost over theoretical fidelity; skill file quality determines review quality
## No auto-stash, require clean tree
- Anti-pattern: Using `git stash` to work around dirty tree before merge/rebase operations
- Correct pattern: Require clean tree to assert process integrity. Exception: session context files (session.md, jobs.md, learnings.md) auto-committed as pre-step
- Rationale: Stash is fragile (conflicts on pop, lost stashes). Clean tree forces explicit state management
- Related: wt-merge skill design — clean tree gate with session context exception
## Always script non-cognitive solutions
- Anti-pattern: Using agent judgment for deterministic operations (conflict resolution with known pattern, session file updates)
- Correct pattern: If solution is non-cognitive (deterministic, pattern-based), script it. Always auto-fix when possible.
- Examples: Session context merge conflicts (keep both sides), worktree task removal from session.md, gitmoji → no judgment needed
- Corollary: Reserve agent invocations for cognitive work (design, review, ambiguous decisions)
## Plugin-dev skill fallback
- When plugin-dev guidance is incomplete or inconsistent, fallback to claude-code-guide agent
- Example: hooks.json format conflict — plugin-dev:hook-development said wrapper format for hooks.json, claude-code-guide clarified direct format is correct
- Pattern: plugin-dev skills are curated snapshots, claude-code-guide has live docs access
## Per-artifact vet coverage required
- Anti-pattern: Create/expand multiple runbook phases in sequence → commit all without individual vet reviews
- Correct pattern: Each phase file is a production artifact → each requires vet-fix-agent review before proceeding
- Root cause: Batch momentum — once first artifact skips review, switching cost increases for each subsequent one
- Rationalization escalation: "Phase 0 was the hard one" → each subsequent phase rationalized as lower risk
- Phase 0 vet found 13 issues in file that "followed the design" — proof that template-following ≠ correctness
- Gate B structural gap: Boolean presence check (any report?), not coverage ratio (artifacts:reports 1:1)
- "Proceed" scope: Activates execution mode which optimizes throughput, rationalizing away friction (vet checkpoints)
## Sequential Task launch breaks parallelism
- Anti-pattern: Launch Task agents one at a time (Phase 1 → wait → Phase 2 → wait...) when all inputs ready and no dependencies
- Correct pattern: Batch all independent Task calls in single message (6 vet reviews → 6 Task calls in one message)
- Root cause: Tool batching rule doesn't explicitly cover Task tool — extension principle not documented
- Wall-clock impact: Sequential = sum(task_times), parallel = max(task_times) — wastes ~14 min for 6 reviews
- Fix needed: Add Task tool section to tool-batching.md with explicit examples
## Failed merge leaves untracked debris
- Anti-pattern: Assume aborted merge is clean — retry merge, get "untracked files would be overwritten"
- Correct pattern: After merge abort, check for new untracked files materialized during merge attempt
- Rationale: Git materializes new files from source branch during merge, aborts without cleaning them up
- Fix: `git clean -fd -- <affected-dirs>` to remove debris, then retry merge
- Diagnostic: File count (untracked vs files added by source branch) and birth timestamps match merge attempt time
## Never agent-initiate lock file removal
- Anti-pattern: Agent removes .git/index.lock after git error suggests "remove the file manually"
- Correct pattern: Stop on unexpected git lock error, report to user, wait for guidance
- Rationale: Lock may indicate active git process; removal by agent bypasses "stop on unexpected results" rule
- Scope: All git operations (merge, commit, rebase) — wait 2s and retry, never delete lock files
- Contributing factor: Project directives scoped lock handling to commit only, agent over-generalized
## Vet-fix-agent context-blind validation
- Anti-pattern: Trust vet-fix-agent output without validation, no execution context provided in delegation
- Vet validates against current filesystem not execution-time state — Phase 6 error: "fixed" edify-plugin → agent-core
- UNFIXABLE issues in reports don't trigger escalation (manual detection required)
- Correct pattern: Provide execution context (IN/OUT scope, changed files, requirements), grep UNFIXABLE after return
- Fix: vet-requirement.md updated with execution context template + UNFIXABLE detection protocol; vet-fix-agent.md updated with execution context section in review protocol
- UNFIXABLE grep is mechanical (consistent with weak orchestrator) — not a judgment call
## Delegation vs execution routing
- Anti-pattern: Single fragment covering both interactive routing and orchestration delegation — conflicting signals
- Correct pattern: Split into execution-routing.md (interactive: understand first, do directly) and delegation.md (orchestration: dispatch to agents)
- Rationale: "Delegate everything" is correct for runbook orchestration, wrong for interactive work
- Fix: delegation.md 131→44 lines (orchestration only), execution-routing.md 25 lines (interactive routing)
## Submodule commit orphan recovery
- Anti-pattern: Reset dev branch to match main — loses submodule commits that only existed on dev
- Correct pattern: Before branch reset, check for submodule commits not on target branch (`git merge-base --is-ancestor`)
- Diagnostic: `git ls-tree <parent-commit> -- agent-core` to extract submodule pointer, then check ancestry
- Recovery: `git -C agent-core merge <orphaned-commit>` if commit still exists as loose object
- Example: focus-session.py (ff056c7) orphaned when dev reset to main, recovered via parent repo history
## E2E over mocked subprocess
- Anti-pattern: Dual test suite — e2e for behavior + mocked subprocess for speed
- Correct pattern: E2E only with real git repos (tmp_path fixtures), mocking only for error injection
- Rationale: Git with tmp_path is fast (milliseconds), subprocess mocks are implementation-coupled (command strings not outcomes), interesting bugs are state transitions that mocks can't catch
- Exception: Mock subprocess for error injection only (lock files, permission errors)
## Flexible phase numbering support
- Anti-pattern: Hardcoding phase validation to expect 1-based numbering (phases 1-N)
- Correct pattern: Detect starting phase number from first file, validate sequential from that base
- Rationale: Design decisions may use 0-based (Phase 0 = foundational step) or 1-based numbering
- Implementation: `start_num = phase_nums[0]`, validate against `range(start_num, start_num + len)`
- Also supports general vs TDD detection: Step headers = general, Cycle headers = TDD
- Fix: agent-core/bin/prepare-runbook.py lines 410-445
## Self-referential runbook modification
- Anti-pattern: Runbook step uses `find plans/` or `sed -i` on `plans/` directory — includes `plans/<plan-name>/` itself
- Correct pattern: Exclude plan's own directory (`-not -path 'plans/<plan-name>/*'`) or enumerate specific target directories
- Detection: Check if any step's file-mutating command scope overlaps `plans/<plan-name>/` (excluding `reports/`)
- Root cause: Blanket directory operations look correct but scope includes the executing runbook
- Fix: Added `-not -path` exclusion to Phase 0 step 12; vet criterion added to main repo
## Worktree merge loses pending tasks
- Anti-pattern: `git checkout --ours agents/session.md` during worktree merge — discards worktree-side pending tasks
- Correct pattern: Extract new pending tasks from worktree session.md before resolving conflict, append to main
- Algorithm: Parse both sides' Pending Tasks by task name regex, diff, append new worktree-side tasks to main
- Example: "Execute plugin migration" task created in worktree, lost by blind --ours resolution
- Fix: Outlined in `plans/worktree-skill/outline.md` Session File Conflict Resolution section
## Planning as orchestratable DAG
- /plan-tdd phases (intake, outline, expansion, review, assembly) decompose into independent delegations
- Phase expansions are fully parallel: all read same inputs (design + outline), write different files
- 8 concurrent sonnet agents produced correct output; git handled concurrent commits (different files)
- Per-phase review needs full outline context (scope alignment), not just the phase file
- Holistic review (cross-phase consistency) runs once after all phases complete
## Post-step verify-remediate-RCA pattern
- Anti-pattern: Trust agent completion, proceed without verification
- Correct pattern: After each agent: git status + precommit → delegate remediation if dirty → add pending RCA task to fix causing skill
- This is a general orchestration pattern, not session-specific — incorporate into orchestration plan templates
- Remediation is mechanical (commit/fix), RCA is cognitive (why did the skill produce dirty state?)
## Delegation requires commit instruction
- Anti-pattern: Agent writes artifact, returns filepath, leaves tree dirty
- Correct pattern: Include explicit "commit your output before returning" in every delegation prompt
- Root cause: Agents optimize for the stated task; cleanup is not implied
- Fix: Prompt template includes `git add <file> && git commit -m "<message>"` instruction
## Consolidation gate catches phase overengineering
- Anti-pattern: 8 phases where 5-6 suffice (Phase 0 trivial at 3 cycles, Phase 5 coupled with Phase 4)
- Correct pattern: Outline review should flag trivial phases (≤3 cycles, Low) for merge with adjacent
- Root cause: Outline generation agent maximized phase count for modularity without consolidation judgment
- Detection: Phase with ≤3 cycles + Low complexity + same files as adjacent phase = merge candidate
## Delegation prompt deduplication
- Anti-pattern: Repeating boilerplate in each parallel agent prompt — bloats orchestrator context
- Correct pattern: Write shared content to a file, reference path in prompts
- Benefit: Orchestrator optimization — agents still read full content from file, but orchestrator context doesn't grow N× for N parallel dispatches
- Agent input unchanged: agents read the referenced file, getting same context as inline would provide
## Orchestration context bloat mitigation
- Anti-pattern: Complex reasoning at end of 50+ message orchestration session
- Correct pattern: Handoff is NOT delegatable — it requires current agent's session context (what happened, what's pending, state transitions)
- Handoff: do inline (structured update, not complex). Commit: mechanical, can delegate or invoke skill
- Plan for restart boundary: planning → restart → execution (different sessions, different model tiers)
## classifyHandoffIfNeeded foreground-only bug
- Bug: `ReferenceError: classifyHandoffIfNeeded is not defined` in Claude Code's SubagentStop processing
- Affected: v2.1.27 through v2.1.38 (current), NOT fixed
- Scope: Only `run_in_background=false` Task calls fail. `run_in_background=true` calls succeed (100% correlation across 26 sessions, 238 failures)
- Severity: Low (cosmetic) — agents complete all work, only status reporting is wrong
- Workaround: Use `run_in_background=true` for Task calls to avoid the broken code path
- Prior learning was wrong: "crashes code-backgrounded agents too" — actually the opposite
- GitHub issues: #22087, #22544 (open, multiple duplicates)
## No post-dispatch agent communication
- Anti-pattern: Launch agent, then try to adjust scope mid-flight via resume
- Correct pattern: Partition scope completely before launch — no mid-flight messaging available
- Limitation: Task tool resume requires agent completion; no channel for scope adjustments to running agents
- Consequence: Over-scoped agents waste work, under-scoped agents miss context — partitioning is one-shot
- Design input for orchestrate-evolution: agent communication model is fire-and-forget
## Weak orchestration is premature optimization
- Anti-pattern: Default to haiku orchestrator for cost savings before workflow patterns are validated
- Correct pattern: Stabilize with sonnet orchestrator, optimize to haiku once patterns are proven and failure modes understood
- Rationale: Weak agents fail at recovery — dirty tree, failed steps, unexpected state all require reasoning
- Many orchestration learnings are band-aids compensating for haiku limitations, not workflow fixes
- Model tier is a configurable knob, not an architectural constraint
## Context-as-scope-boundary replaces prose constraints
- Anti-pattern: Give agent full context + "Execute ONLY this step" prose instruction → agents violate
- Correct pattern: Give executing agent step + design + outline only → scope enforced structurally by context absence
- Executing agents don't get other step files → can't scope-creep to step N+1
- Phase context injected only at feedback points (vet-fix-agent) for alignment checking
- Eliminates need for: scope creep instructions, return verification, execute-only constraints
## UNFIXABLE detection stays mechanical
- Anti-pattern: Because orchestrator is now sonnet, have it read and reason about vet reports
- Correct pattern: Script the UNFIXABLE grep, orchestrator passes reports to recovery agents without reading content
- Rationale: Sonnet CAN reason doesn't mean it SHOULD — keep mechanical checks mechanical
- Orchestrator manages state and dispatch; content interpretation belongs to specialized agents
## Scrub learnings before design input
- Anti-pattern: Using learnings.md entries as-is when designing orchestration or other systems
- Correct pattern: Validate learnings against current evidence before using as design constraints
- Example: "code-backgrounded agents work fine" was a learning that this session disproved
- Rationale: Learnings are session-scoped observations, not verified invariants — they can be stale or wrong
- Scope: Especially important for orchestrate-evolution (learnings ARE the primary input)
- Implementation: Precommit validator should check test summary and fail if any tests skipped
## Orchestration post-step protocol
- Anti-pattern: Trust agent completion report without verification
- Correct pattern: After each step: git status check → if dirty, resume agent or vet-fix to commit → grep UNFIXABLE in vet reports
- Rationale: Agents may complete work but leave uncommitted changes (especially after crashes)
- Protocol: Step 3.3 in orchestrate skill - clean tree is hard requirement, no exceptions
## Background agent crash recovery
- Anti-pattern: Assume "failed" agent work is lost
- Correct pattern: Check output files and git diff — agents complete work before classifyHandoffIfNeeded error fires
- Recovery: Read report for UNFIXABLE, check git diff for changes, commit if work complete
- Better fix: Use `run_in_background=true` to avoid the error entirely
## Refactor agent needs quality directives
- Anti-pattern: Delegate refactoring without quality criteria (deslop, factorization)
- Correct pattern: Include explicit directives in refactor prompt (deslop principles, factorization requirements)
- Rationale: Refactor agent focuses on fixing warnings (line limits, complexity), doesn't proactively optimize for token efficiency or duplication
- Example: Add "Apply deslop principles" and "Factorize duplicated code" to refactor prompts
- Impact: Without directives, agent splits files mechanically without reducing verbosity or extracting helpers
- Evidence: Two agents (adf9068, ae87151) crashed this session after completing work successfully
## Script-validated metadata must be script-generated
- Anti-pattern: Script validates for metadata presence but expects expansion agents (cognitive) to generate it
- Correct pattern: If metadata is deterministic and standard, script injects it during assembly
- Example: prepare-runbook.py validated "stop/error conditions" per cycle, but neither expansion agents nor Common Context provided it. Fix: script injects DEFAULT_TDD_COMMON_CONTEXT during phase file assembly
- Principle: Follows "always script non-cognitive solutions" — deterministic metadata injection beats relying on agent compliance
## Sub-agents cannot spawn sub-agents
- Anti-pattern: Assuming delegated agents can use Task tool to spawn their own sub-agents
- Correct pattern: Task tool is unavailable in sub-agents. All delegation must originate from main session.
- Also unavailable: MCP tools (Context7), hooks
- Available: Read, Grep, Glob, Bash, Write, Edit (direct tool use only)
- Confirmed: claude-code-guide agent, GitHub issue #4182
- Impact: Planning orchestration impractical — design generation needs exploration sub-agents + MCP
## Submodule worktree over --reference clone
- Anti-pattern: `git submodule update --init --reference` creates independent clone with alternates — commits in worktree submodule invisible to main
- Correct pattern: `git -C agent-core worktree add <path> <branch>` shares single object store, bidirectional commit visibility
- Worktree removal order: submodule worktree first, then parent (git refuses parent removal while submodule worktree exists)
- wt-merge fetch becomes no-op: objects already shared, guard with `cat-file -e` before fetching
- Supersedes: "Git worktree submodule gotchas" learning (--reference approach)
## git branch -m .git/config write
- Anti-pattern: Running `git branch -m` in sandbox — fails writing `[branch "X"]` tracking section to .git/config
- Correct pattern: `git branch -m` requires `dangerouslyDisableSandbox: true` (writes to .git/config even when no tracking section exists)
- Partial failure mode: ref renamed successfully but config write fails — retry sees "branch not found"
- Scope: Most git commands only read .git/config; `branch -m` is an exception
## Worktree sibling isolation for CLAUDE.md
- Anti-pattern: Worktrees inside repo (`wt/<slug>`) — Claude CLI loads CLAUDE.md from all parent directories
- Correct pattern: Worktrees in sibling directory (`../<repo>-wt/<slug>`) — no parent CLAUDE.md inheritance
- Container detection: If parent dir ends in `-wt`, already in container (siblings); otherwise create `<repo>-wt/`
- Sandbox: Register container in `.permissions.additionalDirectories` in both main and worktree settings.local.json
## Generic headers break index
- Anti-pattern: `## Definition` as header — becomes useless index key, no discovery value
- Correct pattern: Include the domain noun in the header — `## Deliverable Definition` not `## Definition`
- Rationale: Index keys are exact lowercase match of header text; generic words match nothing useful
- Scope: Any semantic (non-dot-prefixed) header in `agents/decisions/` files
## Memory consolidation worktree conflict
- Anti-pattern: Running `/remember` (learnings consolidation) in a worktree — creates merge conflicts in `agents/learnings.md` and documentation files when merging back to main
- Correct pattern: Only consolidate memory in main repo or in a dedicated consolidation worktree that will be merged independently
- Rationale: Consolidation modifies shared documentation (`agents/learnings.md`, `agents/decisions/*.md`, fragments, skills) — parallel modifications in feature worktrees cause conflicts
- Detection: Check if in worktree via `git rev-parse --show-toplevel` vs `git worktree list` before consolidation
## User @ injects content too
- Anti-pattern: Read a file the user referenced with `@` in their message — content already injected
- Correct pattern: Work directly from loaded content, no Read needed
- Difference: CLAUDE.md `@` is recursive (loads transitive refs), user-message `@` is single file (no recursion)
- Root cause: Template thinking ("apply X" → Read X → edit target) bypasses checking whether content already loaded
- Fix: execution-routing.md updated to explicitly cover both injection sources
## Vet agents over-escalate alignment issues
- Anti-pattern: Labeling straightforward pattern-matching tasks as "UNFIXABLE" requiring design decisions or user input
- Correct pattern: Check existing patterns, apply consistent choice, execute alignment (e.g., find-replace test file references)
- Rationale: Test file naming alignment, variable naming consistency, format standardization are pattern-matching, not design
- Example: Phase 2 vet flagged test file mismatch as "unfixable design decision" when solution was: check existing files, consolidate to test_worktree_cli.py, replace references
- Root cause: Agents treat uncertainty as escalation trigger rather than scanning existing patterns for guidance
- Impact: Creates false blocking issues, delays execution on mechanical fixes
## Sonnet inadequate for conversation synthesis
- Anti-pattern: Defaulting to sonnet for requirements extraction from complex conversations
- Correct pattern: Use opus for extracting/synthesizing requirements from nuanced multi-turn discussions
- Rationale: Sonnet misses implicit requirements in moderately complex conversations; user reports having to repeat intent
- Scope: Applies to any task requiring synthesis of scattered discussion points across long conversations
## Capture-not-interview for requirements
- Anti-pattern: Designing requirements skill as conversational elicitation guide (structured interview)
- Correct pattern: Primary mode is conversation-to-artifact capture; elicitation is secondary mode for cold-start
- Rationale: User's actual need was "formalize what we just discussed" not "guide me through questions"
- Design lesson: Rephrase understanding before building — first outline missed the core concept entirely
## No model tier introspection
- Anti-pattern: Assuming current model tier (e.g., "we're on sonnet, need to restart for opus")
- Correct pattern: Don't guess model tier. Ask, stay silent about it, or rely on external signal (hook)
- Rationale: No introspection API; agent consistently misidentifies as sonnet when running as opus
- Fix: Pending hook to inject model tier into context
## Enforcement cannot fix judgment errors
- Anti-pattern: Adding precommit validation for judgment calls (model selection, task completeness)
- Correct pattern: Enforcement works for structural/mechanical checks; judgment requires conversation-level intervention
- Rationale: Writing agent can satisfy any structural check with wrong content (write `| sonnet` to pass model-required validation)
## Research before outline in design
- Anti-pattern: Skipping external research (Phase A.3-4) and proceeding directly to outline based on internal knowledge
- Correct pattern: Ground in research/best practices BEFORE producing outline — research findings should inform approach selection
- Rationale: Internal reasoning + learnings are necessary but insufficient for behavioral/conversational design problems. External research validates or invalidates assumptions before they become design decisions
- Scope: Especially important when the design problem has published prior art (sycophancy mitigation, prompt engineering patterns)
- Example: Model tier on pending tasks — agent defaults to sonnet, precommit can verify field exists but not correctness## Task agents leave submodule pointer uncommitted
- Anti-pattern: Trusting task agents to commit all changes including parent repo submodule pointer updates
- Correct pattern: Orchestrator checks git status after every step, escalates dirty tree to sonnet for mechanical fix, or adds explicit submodule commit instruction to agent prompts
- Rationale: Task agents focus on their assigned work (changes within submodule) and don't automatically update parent repo pointers. Orchestrator must verify clean tree as hard requirement.
- Occurred: Phase 1 checkpoint and Cycle 2.4 in pushback execution
- Fix: Sonnet escalation for mechanical submodule pointer commit (2 instances)
- Better: Automate in orchestrator post-step verification with explicit instruction or git status check
## Reasoning pushback ≠ conclusion pushback
- Anti-pattern: Counting "your reasoning is wrong but your conclusion is right" as substantive pushback for agreement momentum detection
- Correct pattern: Track conclusion-level agreement separately; reasoning corrections that end in agreement are not pushback
- Evidence: Sycophantic agreement and reasoning engagement are mechanistically distinct (arXiv 2509.21305); LLMs accept user framing in 90% of responses (ELEPHANT study)
- Observed: Agent passed all discussion mode structural checks (assumptions, failure conditions, alternatives) while agreeing with every conclusion — ritual compliance, not genuine evaluation
- Research: `plans/pushback/reports/pushback-improvement-research.md`
## Compression removes redundancy
- Correct pattern: Remove duplicate semantics between name and description; keep all information
- Tolerated redundancy: Item name and its one-line description (Python object + docstring first line, CLI option + help text)
- Generalizes beyond code: hook messages, index entries, section headers — anywhere name + description coexist
- Example: `[DIRECTIVE: DISCUSS] Discussion mode — evaluate critically` → `[DISCUSS] Evaluate critically` (DIRECTIVE+DISCUSS+Discussion = 3× same concept)
