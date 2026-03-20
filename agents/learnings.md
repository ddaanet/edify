# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When codify drops incident-specific learnings
- Anti-pattern: Codify skill quality criteria unconditionally reject incident-specific entries ("describes what happened, not what to do"). Loses recurrence signal — "this happened twice" changes fix priority.
- Correct pattern: Incident-specific entries have value as occurrence counters even without a generalized principle. Recurrence tracking is a valid consolidation reason. Methodology TBD (plan: incident-counting).
- When user says "force" (flush all), skill-internal quality filters should not override user intent.

## When detecting prior uncommitted handoff
- Anti-pattern: `git diff --name-only HEAD -- agents/session.md` non-empty → assume prior handoff → merge incrementally. Conflates current-session task edits (slug markers, task additions) with prior-session uncommitted handoffs.
- Correct pattern: Inspect diff content. Only treat as prior handoff if `## Completed This Session` was modified. Task-only changes (current session edits) → fresh write.
- Agent had conversation context proving it made the edits itself but followed the heuristic mechanically.

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
