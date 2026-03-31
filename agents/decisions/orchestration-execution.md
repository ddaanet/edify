# Orchestration Execution Patterns

Patterns for delegation, orchestration protocol, model selection, and execution-time practices.

## .Delegation Execution

### When Delegation Requires Commit Instruction

**Decision Date:** 2026-02-12

**Anti-pattern:** Agent writes artifact, returns filepath, leaves tree dirty.

**Correct pattern:** Include explicit "commit your output before returning" in every delegation prompt.

**Root cause:** Agents optimize for the stated task; cleanup is not implied. Corrector especially frequent offender.

### When Limiting Agent Scope

**Decision Date:** 2026-02-12

**Anti-pattern:** Full context + "Execute ONLY this step" prose → agents violate.

**Correct pattern:** Give executing agent step + design + outline only. Scope enforced structurally by context absence.

**Rationale:** Executing agents don't get other step files — can't scope-creep. Phase context injected only at feedback points (corrector) for alignment checking.

### When Deduplicating Delegation Prompts

**Decision Date:** 2026-02-12

**Decision:** Write shared content to a file, reference path in prompts.

**Anti-pattern:** Repeating boilerplate in each parallel agent prompt — bloats orchestrator context.

**Benefit:** Orchestrator context doesn't grow N× for N parallel dispatches.

### When Managing Orchestration Context

**Decision Date:** 2026-02-12

**Decision:** Handoff is NOT delegatable — it requires current agent's session context. Commit is mechanical, can delegate.

**Correct pattern:** Plan for restart boundary: planning → restart → execution (different sessions, different model tiers).

### When Partitioning Work For Parallel Agents

**Decision Date:** 2026-02-12

**Anti-pattern:** Launch agent, then try to adjust scope mid-flight via resume.

**Correct pattern:** Partition scope completely before launch — no mid-flight messaging available.

**Consequence:** Over-scoped agents waste work, under-scoped agents miss context — partitioning is one-shot.

### When Task Agents Skip Submodule Pointer

**Decision Date:** 2026-02-15

**Decision:** Orchestrator checks git status after every step, including parent repo submodule pointer updates.

**Anti-pattern:** Trusting task agents to commit submodule pointer changes in parent repo.

**Rationale:** Task agents focus on assigned work within submodule; parent repo pointer updates are outside their scope.

### When Commit Precedes Review Delegation

**Decision Date:** 2026-02-15

**Decision:** Commit artifacts before delegating to review agents (outline-corrector, runbook-corrector, corrector).

**Anti-pattern:** Delegating to review agent while work is uncommitted.

**Rationale:** Review agents operate on filesystem state; uncommitted work may be stale or inconsistent.

### When Step Agents Leave Uncommitted Files

**Decision Date:** 2026-02-19

**Anti-pattern:** Step agents create report files (execution notes, diagnostics) but don't commit them, leaving untracked files that violate the "clean tree after every step" invariant.

**Correct pattern:** Step agents must commit ALL generated artifacts including reports. If the step creates a report, the step's commit includes it.

**Evidence:** Cycles 2.2, 3.1 left report files uncommitted. Orchestrator committed them manually each time.

## .Orchestration Protocol

### When Running Post-Step Verification

**Decision Date:** 2026-02-12

**Decision:** After each step: git status → if dirty, resume agent or vet-fix to commit → grep UNFIXABLE in vet reports.

**Anti-pattern:** Trust agent completion report without verification.

**Rationale:** Clean tree is hard requirement, no exceptions.

### When Planning Is Parallelizable

**Decision Date:** 2026-02-12

**Decision:** Planning phases decompose into independent delegations. Phase expansions are fully parallel — all read same inputs (design + outline), write different files.

**Evidence:** 8 concurrent sonnet agents produced correct output; git handled concurrent commits.

**Constraint:** Per-phase review needs full outline context. Holistic review runs once after all phases complete.

### When Assuming Interactive Context

**Decision Date:** 2026-02-19

**Anti-pattern:** Assuming orchestration is interactive (user watching, can ctrl+c hung agents). Designing timeout as low-priority because "human-in-the-loop provides timeout for free."

**Correct pattern:** Orchestration is unattended — user focuses elsewhere. Timeout is a real operational requirement, not a nice-to-have. Calibrate from historical data.

### When Designing Timeout Mechanisms

**Decision Date:** 2026-02-19

**Anti-pattern:** Treating "dual signal" (time OR tool count) as reducing false positives. OR-logic is the union of both kill zones — it increases false positives vs either threshold alone.

**Correct pattern:** Time and tool count address independent failure modes. Spinning (high activity, no convergence) → `max_turns`. Hanging (no activity, high wall-clock) → duration timeout. Independent guards, not a combined signal.

## .Execution Escalation

Three escalation tiers for handling failures during runbook execution, ordered by scope of recovery.

### When Item-Level Escalation Blocks Execution

**Decision Date:** 2026-02-15

**Trigger:** Single item classified UNFIXABLE by corrector — execution blocked by missing design decision, ambiguous requirement, or external dependency.

**Response:** Orchestrator stops, surfaces UNFIXABLE item to user with investigation summary and subcategory (U-REQ, U-ARCH, U-DESIGN). User provides decision, execution resumes.

**Existing protocol:** `review-requirement.md` UNFIXABLE Detection Protocol (grep-based, mechanical).

### When Local Recovery Suffices

**Decision Date:** 2026-02-15

**Trigger:** Implementation needs restructuring within the same design — refactoring, reorganization, or alternative approach that doesn't invalidate design assumptions.

**Response:** Delegate to `refactor` agent (`plugin/agents/refactor.md`) within current phase. Design and runbook remain valid; only the implementation path changes.

**Distinction from item-level:** Problem is solvable without user input. Distinction from global: design assumptions still hold.

### When Global Replanning Is Needed

**Decision Date:** 2026-02-15

**Trigger:** Execution reveals a design flaw requiring return to the planning phase. Symptoms:

- **Design assumptions invalidated** — implementation discovers a capability doesn't exist, an API doesn't support the required operation, or a dependency behaves differently than designed for
- **Scope creep accumulation** — multiple UNFIXABLE items of the same type, indicating a missing phase or underspecified area rather than isolated gaps
- **Runbook structure broken** — dependency cycles between steps, blocked items accumulating across phases, execution order no longer viable
- **Test plan inadequate** — coverage gaps discovered during implementation that require rethinking the test strategy, not just adding cases

**Response:** Stop execution, return to planning phase. Current runbook is abandoned or revised; design may need amendment.

**Distinction from local:** The design itself is flawed, not just the implementation approach. Local restructuring cannot resolve the problem.

### .Implementation Deferral

FR-17 documents the three-tier escalation requirement. Concrete detection mechanisms, escalation protocols, and replanning handoff procedures are deferred to `wt/error-handling` worktree.

**Grounding:** When-recall incident — test plan required redesign mid-execution; sonnet orchestrator patched ad-hoc rather than escalating to replanning. Planner-executor research distinguishes local replanning (revise subtask) from global replanning (escalate when issues exceed local scope).

## .Model Selection Patterns

### When Stabilizing Orchestrator Model

**Decision Date:** 2026-02-12

**Decision:** Stabilize with sonnet orchestrator, optimize to haiku once patterns are proven and failure modes understood.

**Anti-pattern:** Default to haiku for cost savings before patterns validated.

**Key insight:** Model tier is a configurable knob, not an architectural constraint.

### When Using Opus For RCA Delegation

**Decision Date:** 2026-02-12

**Decision:** Use opus for RCA Task agents. Opus first-pass ≈ sonnet + one deepening round.

**Key delta:** Opus reads actual artifacts where sonnet trusts summarized descriptions.

**Cost:** ~30% more tokens per agent, but eliminates orchestrator deepening round.

### When Sonnet Inadequate For Synthesis

**Decision Date:** 2026-02-12

**Decision:** Use opus for extracting/synthesizing requirements from nuanced multi-turn discussions.

**Rationale:** Sonnet misses implicit requirements in moderately complex conversations.

### When No Model Tier Introspection Available

**Decision Date:** 2026-02-12

**Decision:** Don't guess model tier. Ask, stay silent about it, or rely on external signal (hook).

**Rationale:** No introspection API; agent consistently misidentifies as sonnet when running as opus.

### When Haiku Rationalizes Test Failures

**Decision Date:** 2026-02-19

**Anti-pattern:** Haiku commits code despite failing regression tests, rationalizing failures as "expected behavior change." The regressions were real bugs — branches at HEAD satisfy `git merge-base --is-ancestor`, triggering wrong state detection.

**Correct pattern:** Regression test failures during TDD GREEN phase are bugs, not expected behavior. The step file's regression check command defines the contract.

**Evidence:** Cycle 1.2 haiku committed with 3 failing tests. Required sonnet escalation to diagnose and fix.

### When Haiku GREEN Phase Skips Lint

**Decision Date:** 2026-02-23

**Anti-pattern:** Step file specifies `just test` or `pytest` for GREEN verification. Haiku runs tests (pass), commits — but lint errors exist. Separate fix commit required before REFACTOR.

**Correct pattern:** GREEN verification command must be `just check && just test` (or `just lint && just test`). Runbook template TDD cycle GREEN section must list lint as a required gate before commit, not just test pass.

**Evidence:** Cycle 1.1 GREEN commit had F821 (undefined `Never`) and PLC0415 (local imports). TDD audit flagged as primary compliance violation.

### When Classifying Errors By Tier

**Decision Date:** 2026-02-19

**Anti-pattern:** Moving ALL error classification to orchestrator because haiku can't classify. Sweeping change that ignores capable agents.

**Correct pattern:** Tier-aware classification — sonnet/opus execution agents self-classify and report classified error; haiku agents report raw errors for orchestrator to classify.

**Rationale:** Execution agent has full error context (stack trace, file state). Transmitting to orchestrator for classification loses fidelity or costs tokens.

## .Orchestration Recovery Patterns

### When Resuming Interrupted Orchestration

**Decision Date:** 2026-02-18

**Anti-pattern:** Using `just precommit` as state assessment after context ceiling crash → chasing cascading failures reactively → bypassing project recipes under accumulated momentum.

**Correct pattern:** Resume from last runbook checkpoint. Run the checkpoint verification commands (designed as diagnostic inventory). Systematically fix remaining items. Verify with project recipes.

**Root cause chain:** No ceiling recovery protocol → debugging-as-assessment → reactive fix mode → recipe bypass under urgency.

**Enforcement:** Ceiling recovery scenario added to orchestrate skill (chokepoint enforcement, not ambient rule).

### When Vet Flags Unused Code

**Decision Date:** 2026-02-18

**Anti-pattern:** Flagging code as "dead" based on production callers only. Reviewer recommended deleting `_task_summary` which had 4 test callers and was designed infrastructure for future wiring.

**Correct pattern:** Check both production AND test callers before recommending removal. If tested, it's likely infrastructure awaiting integration. Verify design intent (was it planned for future wiring?) before classifying as dead code.

**Evidence:** Delegated agent followed vet recommendation and deleted the function + tests. Required manual revert.

### When Delegating With Corrections To Prior Analysis

**Decision Date:** 2026-02-18

**Anti-pattern:** Including "don't do X" alongside "do Y and Z" in delegation prompts. Agent read the review report (which recommended X), saw it in changed files, and followed the report's recommendation despite the prompt saying otherwise.

**Correct pattern:** Exclude the wrong item entirely from delegation scope. Don't delegate "3 fixes but actually only do 2" — delegate 2 fixes. Remove conflicting signals by not mentioning the excluded item.

**Rationale:** Delegated agents receive context from both the prompt AND the files they read. When prompt contradicts file content, file content often wins because the agent encounters it during execution with recency bias.

### When Ordering Post-Orchestration Tasks

**Decision Date:** 2026-02-18

**Anti-pattern:** Jumping to pipeline improvements before fixing deliverable findings from the current orchestration.

**Correct pattern:** Diagnostic/process review first, deliverable fixes second, pipeline improvements last. Current deliverable must be whole before improving the process that produced it.

**Rationale:** Unfixed deliverable findings accumulate as tech debt. Pipeline improvements don't retroactively fix the current deliverable. Fixing deliverables also validates the diagnostic — the fix confirms the finding was real.

## .TDD Quality Patterns

### When Assessing RED Pass Blast Radius

**Decision Date:** 2026-02-12

**Decision:** When unexpected RED pass occurs, run blast radius across all remaining phase cycles.

**Classification:** over-implementation (commit test, skip GREEN), test flaw (rewrite assertions), correct (proceed).

**Critical finding:** Test flaws are deliverable defects — feature silently skipped when test passes for wrong reason.

### When Shared Code Is Bifurcated

**Decision Date:** 2026-02-12

**Decision:** When >50% of code is shared and gaps trace to a bifurcation itself, unify first.

**Rationale:** Patches add complexity to maintain; unification removes root cause.

## .Agent Context Patterns

### When Agent Context Has Conflicting Signals

**Decision Date:** 2026-02-12

**Decision:** Common context must be phase-neutral (project conventions, package structure). Phase-specific paths belong in cycle step files only.

**Rationale:** Persistent common context is stronger signal than one-time step file input. At haiku capability, persistent signal wins.

### When Capturing Requirements From Conversation

**Decision Date:** 2026-02-12

**Decision:** Primary mode is conversation-to-artifact capture; elicitation is secondary mode for cold-start.

**Rationale:** User's actual need was "formalize what we just discussed" not "guide me through questions".

### When Submodule Commits Diverge During Orchestration

**Decision Date:** 2026-02-21

**Anti-pattern:** Sequential agents committing to a submodule create branching history. Each agent's commit may create a new branch point if parent repo's submodule pointer isn't updated between steps. A merge can silently drop earlier commits.

**Correct pattern:** After each step that modifies the submodule, verify the submodule pointer in parent matches expected commit. At phase boundaries, verify submodule history is linear: `git -C <submodule> log --oneline -N` should show all phase commits in sequence.

**Evidence:** Phases 3-4 hook scripts lost due to submodule merge at commit `118cd8b`. Recovered from git history.

### When Selecting Agent Type For Orchestrated Steps

**Decision Date:** 2026-02-23

**Anti-pattern:** Substituting a built-in agent type (`tdd-task`) when the plan-specific agent (`<plan>-task`) isn't found. Silent substitution loses common context injected by prepare-runbook.py.

**Correct pattern:** Plan-specific agent is mandatory for `/orchestrate`. If `<plan>-task` isn't available as a subagent_type, STOP and report. Session restart makes custom agents in `.claude/agents/` discoverable. `tdd-task` is only for ad-hoc TDD cycles outside prepared runbooks.

**Evidence:** Dispatched Cycle 1.1 via `tdd-task` instead of `runbook-generation-fixes-task`. Remaining 12 cycles used correct agent after restart.

### When Selecting Model For Discovery And Audit

**Decision Date:** 2026-02-25

**Anti-pattern:** Using haiku scouts to audit prose quality or detect structural anti-patterns in skills, agents, or fragments. Haiku grades generously, misses dominant failure patterns, produces false positives requiring opus validation — double work.

**Correct pattern:** Sonnet minimum for any discovery/audit touching skills, agents, or fragments. These are architectural prose artifacts — assessing their quality requires the same judgment tier as editing them.

**Evidence:** Haiku graded 0 skills at C (sonnet found 3), missed description anti-pattern as dominant issue (18/30), produced 15 gate findings vs sonnet's 12 (3 false positives).

### When Reviewing Batch Skill Edits

**Decision Date:** 2026-02-25

**Anti-pattern:** Single reviewer agent for all modified skills. Context fills with 28 skill reads before review begins. Quality degrades as context grows.

**Correct pattern:** Parallel reviewers split by relatedness. Separate behavior invariance agent for conditional-branch skills. All read-only, no file conflicts.

### When Scoping Corrector On TDD Deliverables

**Decision Date:** 2026-02-27

**Anti-pattern:** Scoping corrector to only the files modified in the most recent TDD cycle.

**Correct pattern:** Scope corrector to ALL files changed on the branch vs main (`git diff --name-only main...HEAD`). The deliverable is the full branch, not the last cycle. Test-driven specification doesn't replace review — it narrows what the review needs to check.

### When Delegating TDD Cycles To Test-Driver

**Decision Date:** 2026-02-27

**Anti-pattern:** Sending all N cycles in a single prompt. Agent loses focus on later cycles, context overloaded.

**Correct pattern:** Piecemeal — one cycle per invocation. Resume the same agent for subsequent cycles (preserves accumulated context). Fresh agent if context nears 150k.

**Context priming:** Sub-agents don't share parent context. Each NEW agent must self-prime by running `edify _recall resolve` on relevant recall-artifact entries. Resumed agents already have this context.

**Prompt composition anti-pattern:** Passing the full runbook (or multiple cycles) to the test-driver. Visible future cycles cause GREEN phases to over-implement, breaking minimal-passing-implementation discipline.

**Correct pattern:** Executing session extracts the current cycle and composes the test-driver prompt from cycle spec + Common Context + recall entries. Test-driver receives only its cycle's scope. Enforcement is structural — context absence, not prose instruction (see "When Limiting Agent Scope"). Persistent context is stronger signal than per-step instruction at haiku capability (see "When Agent Context Has Conflicting Signals").

### When Implementation Modifies Pipeline Skills

**Decision Date:** 2026-02-27

**Anti-pattern:** Using the full runbook pipeline when the planned work modifies pipeline skills (/design, /runbook) or pipeline contracts. Self-modification coupling: a runbook step that edits the runbook skill creates stale-instruction risk for subsequent steps.

**Correct pattern:** Structure as inline task sequence orchestrated through session pending tasks. Each task executes with fresh CLAUDE.md loads, sidestepping stale instructions. TDD discipline preserved — executing session dispatches test-driver via Task tool per cycle.

**Also applies when:** No parallelization benefit (strict dependency chain), overhead/value mismatch (pipeline coordination cost > error-recovery value for ~10 sequential work units).
