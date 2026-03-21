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

## When delegating external repo git operations
- Anti-pattern: Dispatch artisan agents to run `git -C ~/code/<repo>` on repos outside the project tree. Sandbox write-allow restrictions block the agent even though the operations are read-only.
- Correct pattern: Execute git read operations (`git -C`, `git log`, `git show`) directly from the parent session. Sub-agents only work reliably within the project's sandbox-allowed paths.
- scratch/* repos under claudeutils worked because `~/code/claudeutils` is in the write-allow list. External repos (~/code/rules, ~/code/tuick, etc.) failed.
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