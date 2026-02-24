# Task Classification Outline

Two features:
1. **`/prime` skill** — load plan artifacts + chain-call `/recall` for ad-hoc plan work outside workflow skills
2. **Task classification** — replace single "Pending Tasks" section with "In-tree Tasks" + "Worktree Tasks" (planning signal, not tracking)

---

## Approach

**Feature 1: `/prime` Skill**

New skill for ad-hoc plan work that doesn't go through workflow skills (design, runbook, orchestrate). Workflow skills have built-in discovery gates — `/prime` fills the gap for tasks like fixing a blocker, revising an outline, patching a runbook-outline, or debugging plan infrastructure.

**Invocation:** `/prime plans/foo/`

**Behavior:**
1. Read all existing plan artifacts in the directory: `requirements.md`, `outline.md`, `design.md`, `runbook-outline.md`
2. Chain-call `/recall` (no explicit topic) — plan artifacts now in conversation give `/recall` rich signal for entry selection

Not limited to frozen artifacts. No @ref injection, no session.md format changes, no scripted gates, no workflow skill modifications. Content enters conversation via Read calls.

**Placement in task commands:** Handoff writes `/prime plans/foo/` into task commands for non-workflow tasks. Example:
```
- [ ] **Fix prepare-runbook.py bugs** — `/prime plans/prepare-runbook-fixes/` | sonnet
```
The `&&` chaining syntax is not applicable to skill invocations. `/prime` loads context and chain-calls `/recall`, then the agent proceeds with the task work. The task command is the skill invocation; subsequent work follows from conversation context.

**Relationship to workflow skills:** `/prime` does NOT replace workflow skill discovery. Workflow skills (design A.1, runbook Phase 0.5, orchestrate context load) keep their existing gates unchanged. `/prime` is for work that bypasses those skills entirely.

**Feature 2: Task Classification**

Replace "Pending Tasks" with two sections:
- `## In-tree Tasks` — work done directly on current branch (quick, mechanical, no isolation needed)
- `## Worktree Tasks` — tasks pre-classified as needing isolation (has plan dir + behavioral changes, or restart required, or explicitly parallel)

Classification is **static** — set at task creation by handoff or `p:` directive. No move semantics. Eliminates the `move_task_to_worktree()` amend ceremony (identified failure mode in `operational-tooling.md`).

Active worktrees: `_worktree new` adds `→ \`slug\`` marker inline; `_worktree rm` removes it. Task stays in "Worktree Tasks" throughout — no section moves.

**Bare-slug worktrees:** `_worktree new <slug>` (no `--task`) creates a worktree without session.md integration. No marker added, no task reference. This is unchanged — bare-slug worktrees are an escape hatch, not a managed path.

**Filesystem drift:** `#status` annotates worktree tasks with `→ slug` from `_worktree ls` output (live git worktree state), not from session.md markers. Session.md markers are convenience for handoff/focus; `#status` rendering uses filesystem as source of truth.

---

## Key Decisions

**D-1: `/prime` is for ad-hoc plan work, not workflow optimization.** Workflow skills have built-in discovery. `/prime` covers the gap: tasks that work on plan artifacts without invoking a workflow skill. Not a replacement, not a supplement — a different use case.

**D-2: No frozen artifact restriction.** The frozen rule was specific to @ref injection (stale system-prompt content contradicting fresh Reads). `/prime` uses Read calls — content is in conversation, not system prompt. No stale-expansion concern.

**D-3: Chain-call `/recall`.** `/prime` loads plan artifacts, then tail-calls `/recall`. Plan content in conversation gives `/recall` rich signal for topic selection. No recall logic duplicated in `/prime`. `/recall`'s cumulative tracking preserved (later `/recall` calls skip already-loaded entries).

**D-3a: `/prime` skill D+B compliance.** Skill steps must open with concrete tool calls (Read/Bash/Glob per `implementation-notes.md` "How to Prevent Skill Steps From Being Skipped"). Step 1 (Read artifacts) naturally anchors with Read calls. Step 2 (chain-call `/recall`) is a skill invocation, not a prose gate — acceptable.

**D-4: Worktree Tasks semantics** — planning signal, not tracking. Tasks are *intended* for worktree execution regardless of whether one exists. Supersedes the prior "correct pattern" (inline `→ slug` in Pending) from `operational-tooling.md` "When Tracking Worktree Tasks In Session.md" — that pattern was designed but not fully implemented. This approach avoids all three identified failure modes: (a) no move semantics eliminates `_update_session_and_amend` ceremony, (b) bare-slug worktrees are orthogonal (no session integration expected), (c) `#status` renders from `_worktree ls` (filesystem state), not session.md section content. The `operational-tooling.md` decision entry needs updating on implementation to reflect the new pattern.

**D-5: No backward migration** — handoff rewrites session.md on invocation. Old "Pending Tasks" tasks classified into correct section on first post-impl handoff.

**D-6: focus_session() search scope** — reads from "Worktree Tasks" section. Tasks in "In-tree Tasks" not dispatchable as worktrees without explicit override.

**D-7: Status display** — In-tree Tasks first, then Worktree Tasks. Active worktrees (from `_worktree ls`) annotate with `→ slug`.

**D-8: #execute pickup** — `x` starts first in-tree task. Worktree tasks require `wt` setup. Routing signal explicit in execution.

**D-9: Classification heuristic** — In-tree: no plan directory, mechanical edits, no restart. Worktree: plan directory + behavioral changes, opus model tier, restart flag, or explicitly parallel scope.

---

## Scope

**IN (Feature 1 — `/prime` skill):**
- New skill: `agent-core/skills/prime/SKILL.md`
- Reads plan artifacts, chain-calls `/recall`
- Task command integration (handoff writes `/prime` into non-workflow task commands)

**IN (Feature 2 — task classification):**
- `session.py`: `extract_task_blocks()` handles "In-tree Tasks" / "Worktree Tasks"; `add_slug_marker()` replaces `move_task_to_worktree()` (no move); `remove_slug_marker()` replaces `remove_worktree_task()`
- `resolve.py`: merge autostrategy updated for new section names (currently hardcodes "Pending Tasks" / "Worktree Tasks")
- `session_structure.py`: validation rules updated — "Worktree Tasks" format check, cross-section dedup check, new section names
- `aggregation.py`: `extract_task_blocks(content, section="Pending Tasks")` call updated for new section name(s)
- `handoff` skill: two-section task list, classification heuristic
- `execute-rule.md`: `#status` display for two sections, `#execute` pickup rule update
- `operational-tooling.md`: update "When Tracking Worktree Tasks In Session.md" decision to reflect new pattern

**OUT:**
- Workflow skill modifications (discovery gates unchanged)
- @ref injection / session.md Preload section (dropped)
- Scripted context-check gate (dropped)
- `_worktree merge` session autostrategy (separate task)
- Classification of in-flight tasks (manual on first post-impl handoff)

---

## Open Questions

1. **`wt` scan scope:** Should `wt` (mode B parallel group) exclusively scan "Worktree Tasks", or still analyze all pending for independence? Pre-classification makes mode B trivial (Worktree Tasks without active slug = candidates), but removes independence analysis as safety check. Recommendation: `wt` scans "Worktree Tasks" for candidates, applies independence analysis as validation (not discovery). This aligns with D-8 (`x` picks in-tree, `wt` picks worktree) while retaining the safety check.
2. **Handoff classification approach:** Prescriptive rules in skill, or advisory (agent judgment per task)? `p:` directives pre-classify at creation; heuristic (D-9) only for tasks surfaced from conversation. Recommendation: D-9 heuristic is prescriptive for clear cases (restart flag, plan dir + behavioral changes), advisory for ambiguous cases (agent judgment, defaulting to in-tree when uncertain).

---

## Discussion Log

Key conclusions from iterative discussion (8 rounds):

- @ref preload mechanism explored and dropped: cumulative duplication with Reads, phase-gating complexity, frozen-artifact restrictions — all infrastructure to automate something a skill invocation handles directly
- SessionStart hook explored for recall expansion — useful for scripted expansion but doesn't solve phase-specific gating
- D+B anchored discovery gate explored — session.md Read is itself redundant (already in system prompt), scripted gate proposed but adds infrastructure
- Final direction: explicit `/prime` skill for ad-hoc work, workflow skills unchanged, chain-call `/recall` for recall pass
