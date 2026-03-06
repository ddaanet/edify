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
