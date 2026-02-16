# Operational Practices

Agent reliability patterns, artifact management, implementation practices, and known issues.

## .Artifact and Review Patterns

### When Placing Deliverable Artifacts

**Decision Date:** 2026-02-12

**Decision:** If artifact will be referenced in a followup session → `plans/`. If not → `tmp/`.

**Decision principle:** "Will this be referenced later?" — not "Is this type in a known list?"

### When Requiring Per-Artifact Vet Coverage

**Decision Date:** 2026-02-12

**Decision:** Each production artifact requires vet-fix-agent review before proceeding.

**Root cause:** Batch momentum — once first artifact skips review, switching cost increases for each subsequent one.

### When Launching Task Agents In Parallel

**Decision Date:** 2026-02-12

**Decision:** Batch all independent Task calls in single message.

**Wall-clock impact:** Sequential = sum(task_times), parallel = max(task_times).

### When Background Agents Crash

**Decision Date:** 2026-02-12

**Correct pattern:** Check output files and git diff — agents complete work before classifyHandoffIfNeeded error fires.

**Recovery:** Use `run_in_background=true` to avoid the error entirely.

### When Refactoring Agents Need Quality Directives

**Decision Date:** 2026-02-12

**Correct pattern:** Include explicit deslop and factorization directives in refactor prompts.

**Rationale:** Refactor agent focuses on warnings (line limits, complexity), doesn't proactively optimize for token efficiency.

## .Agent Reliability Patterns

### When Exploration Agents Report False Findings

**Decision Date:** 2026-02-12

**Correct pattern:** Verify file existence claims from quiet-explore agents (ls, git ls-tree).

### When Scrubbing Learnings Before Design Input

**Decision Date:** 2026-02-12

**Decision:** Validate learnings against current evidence before using as design constraints.

**Rationale:** Learnings are session-scoped observations, not verified invariants — can be stale or wrong.

## .Architectural Principles

### When Temporal Validation Required For Analysis

**Decision Date:** 2026-02-12

**Decision:** Correlate session timestamps with git history to validate feature availability before analysis.

**Git commands:** `git log --format="%ai" --follow <file>` for creation date, session mtime for analysis window.

### .When Behavioral Triggers Beat Passive Knowledge

**Decision Date:** 2026-02-12

**Decision:** `/when` (behavioral) and `/how` (procedural) only — these prescribe action, creating retrieval intention.

**Consequence:** If a learning can't be phrased as `/when` or `/how`, it's either a fragment (ambient) or lacks actionable content.

### .When Enforcement Cannot Fix Judgment

**Decision Date:** 2026-02-12

**Decision:** Enforcement works for structural/mechanical checks; judgment requires conversation-level intervention.

**Rationale:** Writing agent can satisfy any structural check with wrong content.

## .Git Workflow Patterns

### When No-Op Merge Orphans Branch

**Decision Date:** 2026-02-12

**Decision:** Always create merge commit when `git merge --no-commit` was initiated.

**Rationale:** Without merge commit, branch is unreachable from HEAD → `git branch -d` rejects.

### When Naming Tasks For Worktrees

**Decision Date:** 2026-02-12

**Decision:** Constrain task names to `[a-zA-Z0-9 ]` — slug derivation is near-identity.

### When Requiring Clean Git Tree

**Decision Date:** 2026-02-12

**Decision:** Require clean tree before merge/rebase operations. No `git stash` workarounds.

**Exception:** Session context files (session.md, jobs.md, learnings.md) auto-committed as pre-step.

**Rationale:** Stash is fragile (conflicts on pop, lost stashes). Clean tree forces explicit state management.

### When Failed Merge Leaves Debris

**Decision Date:** 2026-02-12

**Decision:** After merge abort, check for untracked files materialized during the attempt.

**Anti-pattern:** Assume aborted merge is clean — retry fails with "untracked files would be overwritten."

**Fix:** `git clean -fd -- <affected-dirs>` to remove debris, then retry.

### When Git Lock Error Occurs

**Decision Date:** 2026-02-12

**Decision:** Stop on unexpected git lock error, report to user, wait for guidance. Never delete lock files.

**Anti-pattern:** Agent removes `.git/index.lock` after git error suggests manual removal.

**Rationale:** Lock may indicate active process; removal bypasses "stop on unexpected results" rule.

## .Known Issues

### When ClassifyHandoffIfNeeded Bug Occurs

**Bug:** `ReferenceError: classifyHandoffIfNeeded is not defined` in Claude Code's SubagentStop processing.

**Affected:** v2.1.27+. NOT fixed.

**Scope:** Only `run_in_background=false` Task calls fail. `run_in_background=true` works.

**Workaround:** Use `run_in_background=true` for Task calls.

**GitHub issues:** #22087, #22544.

## .Sub-agent Limitations

### When Sub-Agents Cannot Spawn Sub-Agents

**Limitation:** Task tool is unavailable in sub-agents. All delegation must originate from main session.

**Also unavailable:** MCP tools (Context7), hooks.

**Available:** Read, Grep, Glob, Bash, Write, Edit (direct tool use only).

## .Python Patterns

### When Extracting Git Helper Functions

**Pattern:** Private `_git(*args, check=True, **kwargs) -> str` helper — 1 line per call, fits 88-char limit.

**Evidence:** 24 calls replaced, 477→336 lines (30% reduction) in worktree cli.py.

### When Fixture Shadowing Creates Dead Code

**Anti-pattern:** Defining local function with same name as pytest fixture — function is unreachable dead code.

**Detection:** Grep for function definitions that duplicate fixture names, check if test functions use fixture injection.

### When Test Corpus Defines Correct Behavior

**Anti-pattern:** Rewriting fixtures to avoid triggering known bugs.

**Correct pattern:** Fixtures define correct behavior — failing tests are the signal that code needs fixing.

## .Memory Index Patterns

### .When Index Keys Must Be Exact

**Decision:** Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery.

**Rationale:** Exact keys are deterministic and debuggable.

### When DP Matrix Has Zero-Ambiguity

**Decision:** Initialize DP matrix with -inf for impossible states, 0.0 only for base case.

**Evidence:** "when mock tests" scored 128.0 against candidate with no matching chars — positive score from nothing.

## .Runbook Validation Patterns

### When Phase Numbering Is Flexible

**Decision:** Detect starting phase number from first file, validate sequential from that base.

**Rationale:** Design decisions may use 0-based or 1-based numbering.

### When Checking Self-Referential Modification

**Anti-pattern:** Runbook step uses `find plans/` — includes the executing plan's own directory.

**Correct pattern:** Exclude plan's own directory or enumerate specific targets.

## .Naming Patterns

### When Avoiding CLI Skill Name Collision

**Decision:** Check CLI built-ins before naming skills.

**Scope:** /help, /plan, /review, /model, /clear, /compact, and other built-in commands.

### When Choosing Name

**Decision:** Prioritize human discovery and recall over thematic alignment or cleverness.

**Applies to:** Skill names (slash commands), agent names, command names — any user-facing identifier the human must remember or search for.

**Priority order:**
1. **Discoverability** — The word the user thinks of when they need the capability should match the handle. "I need to ground this" → `/ground`, not `/found`.
2. **Recall** — Short, common words beat etymologically precise ones. If a user can't remember the name after one use, it's wrong.
3. **Thematic alignment** — Nice to have (e.g., construction metaphors pairing with a plugin named "edify"), but never at the cost of discoverability.

**Anti-pattern:** Choosing `/found` (Latin *fundare*, pairs with "edify") over `/ground` (the word people actually use when describing the need).

**Test:** "What word would someone type if they needed this capability and didn't know the command existed?" That word is the name.
