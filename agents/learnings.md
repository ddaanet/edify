# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When codify triggers on a feature branch
- Do not codify on feature branches. Decision file changes create merge conflicts with main's decisions/. Defer codification to main.
- The soft-limit age calculation should account for branch context — learnings on feature branches are younger in main-branch terms.
- Pending: Codify branch awareness task (sonnet, no restart).
## When pending tasks lack recovery context
- Anti-pattern: Task entry has description but no backtick command. Next session's `x` has nothing to invoke. Worse: discussion conclusions (d: mode decisions, agreed refinements, identified reuse paths) exist only in conversation context — lost on session boundary.
- Correct pattern: Every pending task gets a backtick command in the entry. Discussion conclusions that produce pending work get captured as task notes in session.md, recoverable via `task-context.sh`. The handoff IS the recovery mechanism — if it's not in session.md, it doesn't survive.
- Evidence: Codify branch awareness task had no command. Lint-gated recall refinement (tuick reuse, per-error-type gating) existed only in conversation until manually captured.
## When "worktree-tasks-only" appears to block maintenance skills
- The "main is worktree-tasks-only" rule scopes to task classification (pending tasks in session.md), not interactive skill execution. Maintenance skills (`/codify`, `/commit`, `/handoff`) run on main regardless.
- Anti-pattern: Proposing workaround branches for codify because "main doesn't allow work." The rule governs where pending tasks live, not what skills can execute.
- Correct pattern: Run `/codify` on main directly. Dispatch worktrees for implementation tasks after. Sequential, not parallel — worktrees benefit from updated decisions/ anyway.
- The codify-in-a-branch proposal fails on merge ordering: codify touches decisions/, fragments/, memory-index.md — shared infrastructure with no deterministic merge-first guarantee.
## When skill description triggering appears important
- Anti-pattern: Investing in skill description optimization (eval loops, train/test splits) when the workflow is fully structured — all skill invocations are explicit (shortcuts, backtick commands, chaining, frontmatter injection).
- Correct pattern: Skill description optimization matters only when automatic triggering operates — i.e., unstructured user input where Claude autonomously decides which skill to invoke. In structured workflows with explicit invocation rails, descriptions serve as documentation only.
- Evidence: 32 project skills, zero relying on automatic triggering. Entry points (`d:` directive, `/requirements`) are both explicit. Skill-creator eval infrastructure exists for marketplace plugins where auto-triggering does matter.
## When parsing Claude Code JSONL message content
- Anti-pattern: Assuming `type: "user"` entries with interrupt text (`[Request interrupted by user]`) always use string content format. In practice, interrupt messages appear as list content `[{"type": "text", "text": "[Request interrupted by user]"}]`.
- Correct pattern: Extract text from both string and list formats before checking for content markers (interrupts, system-reminders, command tags). The content format is not predictable from the entry type — both formats occur for the same semantic content.
- Evidence: Parser missed all interrupt entries in real sessions until list-format branch was fixed.
## When Edit tool fails repeatedly
- Anti-pattern: Switching to `sed -i` after Edit tool errors. sed presents opaque commands in permission prompts — user sees syntax, not content diff. Degrades the human review gate that Edit provides (old/new content visible).
- Correct pattern: Stop and report the Edit failure after the second identical error. The stop-on-unexpected rule exists precisely for this case. Edit's permission UX is part of human oversight design — bypassing it with sed is not a neutral tool substitution.
- Evidence: 6 identical `replace_all` type errors without diagnosis, escaped to sed, user rejected an opaque sed command they couldn't verify.
## When choosing storage for persistent caches
- Anti-pattern: Using JSON file as a key-value store because the codebase has an existing JSON cache (models_cache.json). The existing cache is a special case (bounded, ~50 entries, refreshed on TTL). Extending the pattern to unbounded append-heavy caches cargo-cults the storage choice.
- Correct pattern: sqlite via sqlalchemy for persistent caches. stdlib sqlite3 handles concurrent access (parallel worktrees), sqlalchemy mapped classes match project's Pydantic-model convention, growth path for future caches without hand-written SQL proliferation.
- The "JSON is fine at this scale" argument is technically correct but sets a convention. Each future cache copies the pattern, and nobody will detect when aggregate load matters.
## When designing hierarchical index structures
- Anti-pattern: Mixed indices containing both entries and child references. Creates discoverability imbalance — inline entries are immediately visible and individually selectable, while child-referenced entries require an extra navigation step. The split is a capacity decision but has an unintended discoverability side effect.
- Correct pattern: Clean separation — branch indices (index-of-indices only) vs leaf indices (entries only). Uniform discovery paths: root → branch(es) → leaf → entry. Simplifies parser (no mixed-mode detection).
## When outlines conflate decomposition with sequencing
- Anti-pattern: Design outlines that use "phases" to mean both "logical sub-problems" and "execution order." This forces premature ordering and defers design-time activities (grounding, research) into execution phases.
- Evidence: Active recall outline placed grounding (Phase 5) after metadata model commitment (Phase 4). The outline acknowledged the risk but accepted it — weak mitigation hiding a structural flaw.
- Correct pattern: Decomposition (breaking into sub-problems with dependency graph) is a separate activity from sequencing (ordering for implementation). Sub-problems get tagged with design readiness — some are ready for runbook, others need more design. Sequencing happens at runbook time, not decomposition time.
- Design inputs (grounding, research) belong in the design process, not as execution phases.
## When output-style plugins conflict with prose rules
- Anti-pattern: Following `★ Insight` decorative block instructions injected by SessionStart hooks (explanatory-output-style, learning-output-style plugins) when CLAUDE.md prose rules say "no framing, let results speak."
- Root cause: System-reminder injection carries high perceived authority + specific template + "always" keyword. General prose quality rules lose the salience competition. The directive appeared twice (both plugins enabled simultaneously), reinforcing compliance.
- Correct pattern: Project CLAUDE.md prose rules govern output style. Disable output-style plugins that conflict (`explanatory-output-style`, `learning-output-style` in settings.json `enabledPlugins`). If educational output is wanted, it should be encoded in CLAUDE.md, not injected via competing system-reminders.