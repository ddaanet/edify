# Brief: Skill-CLI Composition Completion

## Origin

Session trace observation (2026-03-30). User identified two integration gaps during skill-cli-integration execution:

1. Handoff skill composition deferred on false premise
2. Commit skill discovery phase left manual despite CLI existing

## Problem

### Handoff (D-4 deferral invalidated)

D-4 (skill-cli-integration outline) deferred handoff skill composition with rationale: "Skill manages 4+ additional sections. Partial composition adds split-write complexity for minimal gain. Batch synthesis wins on consistency."

Session trace shows the opposite. The handoff skill uses targeted Edit calls — reproducing old section content in `old_string` to replace with new content. The "Completed This Session" section is a fresh write every handoff. A CLI handling that section eliminates old-content reproduction. The skill is NOT doing monolithic rewrite — D-4's premise is wrong.

### Commit discovery (input side missed)

The brief specified composition as: `_git changes` → draft message → pipe to `_commit`. The runbook only scoped replacing Step 4 (commit execution → `_commit`). Step 1 discovery was left as 3+ separate git Bash calls. `claudeutils _git changes` exists and provides unified parent + submodule status and diff in one call.

The runbook scoped half the composition: output to CLI, input left manual.

### SP-2 review findings wrongly deferred

SP-2 skill-reviewer found 3 Majors (M-1: double validation, M-2: `--test` flag CLI gap, M-3: Step 1c staging bypass) and assessed "Needs rework (0C/3M)." The calling agent overrode to "Ready" by classifying all three as "DEFERRED — pre-existing." These are the same integration gap pattern — skills retaining operations that D-2 assigns to CLI. The override was wrong; the reviewer's assessment was correct.

Design must address both the reviewer's findings (M-1, M-2, M-3) and the user-identified gaps (`_git changes`, handoff D-4) as a single integration scope.

## Scope

Four integration points remaining:

1. **Commit discovery** — Replace Step 1 manual git calls with `claudeutils _git changes`. Remove skill-side `just precommit` (CLI handles validation per D-2). Remove Step 1c `git add` (CLI handles staging).
2. **Commit `--test` flag** — Add `just-test` to CLI's `_VALID_OPTIONS` and pipeline path, or reconcile the flag semantics.
3. **Handoff composition** — Revisit D-4 with corrected premise. Identify which sections benefit from CLI handling vs skill synthesis.
4. **Status unscheduled plans** — Current `_status` lists all local unscheduled plans (floods output). Fix: show plans scheduled HERE (local session.md tasks), plus a count of plans HERE scheduled NOWHERE (cross-tree check via `aggregate_trees`). Full list available via `_worktree ls`.

## Constraints

- Skills are agentic-prose (opus for edits)
- Item 2 requires CLI-side code change (production, sonnet)
- Handoff redesign (item 3) needs careful scoping — the skill's judgment-heavy sections (tasks, blockers, next steps) may genuinely not benefit from CLI composition

## Evidence

- Session dump: `tmp/session-full-dump.json` (286 entries, current session)
- SP-2 review: `plans/skill-cli-integration/reports/review-sp2.md` (M-1, M-2, M-3)
- D-4 deferral: `plans/skill-cli-integration/outline.md` (D-4 section)
- `_git changes` CLI: `claudeutils _git changes --help`
- `_commit` parser: `src/claudeutils/session/commit.py` (`_VALID_OPTIONS`)
- `_status` unscheduled: `src/claudeutils/session/status/cli.py:70,97-100` — local-only `list_plans` + local-only `task_plan_dirs`
- Cross-tree aggregation: `src/claudeutils/planstate/aggregation.py` — `aggregate_trees` already iterates all worktrees

## References

- `plans/skill-cli-integration/outline.md` — Original design (D-2 composition boundary, D-4 handoff deferral)
- `plans/skill-cli-integration/reports/review-sp2.md` — SP-2 skill review (M-1, M-2, M-3 — reviewer said rework, agent overrode to ready)
- `plugin/skills/commit/SKILL.md` — Current commit skill (post-SP-2)
- `plugin/skills/handoff/SKILL.md` — Current handoff skill
- Learnings: "When reviewing CLI-skill integration" (circular justification pattern)
