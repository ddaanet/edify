# Problem: Worktree Lifecycle CLI

Umbrella plan for worktree CLI improvements. Consolidates:

- `wt-exit-ceremony` — exit ceremony for worktree sessions
- `wt-rm-task-cleanup` — task entry cleanup on worktree removal
- `worktree-ad-hoc-task` — ad-hoc task creation within worktrees
- Worktree CLI UX improvements
- `--base` submodule bug fix

## Investigation Scope

- Exit ceremony: what state transitions and side effects should occur when leaving a worktree session
- Task cleanup: how `_worktree rm` should handle session.md task entries (currently strips marker but leaves entry)
- Ad-hoc tasks: how to create tasks scoped to a worktree without main session.md
- CLI UX: command discoverability, help text, error messages
- `--base` submodule: `_worktree new --base` fails when submodule ref differs between branches

---

## Absorbed: wt-exit-ceremony

Source: `plans/wt-exit-ceremony/brief.md` (2026-03-01)

### Problem

After deliverable review passes in a worktree, the user must manually: run `hc`, switch terminal, remember slug, type `wt merge <slug>` then `wt-rm <slug>`. No automation guides the transition.

### Proposed solution

Two UPS Tier 1 shortcuts:

**`k`/`ok` — acceptance + context transfer:**
- Semantics: "I acknowledge this result, help me transition out"
- After commit in a worktree with no pending tasks, copies merge+rm command to clipboard
- Implementation: UPS hook Tier 1 command → `additionalContext` injection → agent runs pbcopy/xclip

**`g`/`go` — forward momentum within session:**
- Semantics: "execute the next thing" (similar to `x` but lighter)
- Distinct from `k`: "go" implies work continues in current session; "ok" implies completion + transition

### Worktree lifecycle change

- After deliverable review passes → status shows "Branch complete"
- After commit → `k` copies transition command
- Post-review → commit → transition sequence should be guided, not ad-hoc

### Semantic distinction

| Situation | `g`/`go` | `k`/`ok` |
|-----------|----------|----------|
| After status display | Execute next task | Acknowledge, might adjust first |
| After commit | Start next pending task | Copy transition command |
| After deliverable review | Start fixing findings | Accept review, proceed to handoff |
| After `d:` conclusion | Execute what was discussed | Accept assessment, think about it |
| Branch complete (no pending) | No target | Transition out (clipboard) |

### Implementation notes

- UPS hook: `plugin/hooks/userpromptsubmit-shortcuts.py`
- Tier 1 commands are exact-match, simplest tier (like `c`, `y`)
- `additionalContext` is agent-only, `systemMessage` is user-only (~60 char budget)
- `dangerouslyDisableSandbox: true` required for clipboard access

---

## Absorbed: wt-rm-task-cleanup

Source: `plans/wt-rm-task-cleanup/brief.md` (2026-03-02, updated 2026-03-06)

### Problem

`_worktree rm` after merge leaves orphaned `[ ]` task entries in Worktree Tasks. `remove_slug_marker()` strips the `→ slug` marker but doesn't remove the entry. Caused by task-classification (D-4) which replaced `remove_worktree_task()` with `remove_slug_marker()`.

### Design decision

**Completion signal:** Check branch session.md for `[x]` status on the task (`git show <branch>:agents/session.md`). If completed in branch, remove entry from main's session.md. If not `[x]`, strip marker only (cleanup/abandoned case).

**Not merge state.** `_is_merge_of(slug)` doesn't distinguish "work complete" from "sync merge" or "partial progress merge."

### Scope

- `_update_session_and_amend()` in `cli.py`: after `remove_slug_marker`, check branch session.md for task completion, remove entry if `[x]`
- Needs `extract_task_blocks` or similar to read branch session.md and find task status
- Test: merge→rm with `[x]` → entry removed; merge→rm with `[ ]` → marker stripped, entry preserved

### Compound failure (2026-03-06)

Stale markers block session-validator (exit code 1). Validator is correct — marker pointing to nonexistent worktree IS invalid state. Root cause is rm not cleaning up. The `[x]` branch-check should also handle the case where rm runs after worktree removal (no branch to check). Marker should be stripped unconditionally by rm; `[x]` check governs whether the entire task entry is removed.

---

## Absorbed: worktree-ad-hoc-task

Source: `plans/worktree-ad-hoc-task/requirements.md`

### Requirements

**FR-1: Add task to session.md before worktree creation**
When the user requests a focused worktree for a task not yet in session.md, the worktree skill (Mode A) must add the task entry before invoking `claudeutils _worktree new`. The CLI requires the task to exist for `move_task_to_worktree()` and `focus_session()`.

Acceptance criteria:
- Skill detects task absence after reading session.md
- Skill writes minimal task entry (`- [ ] **Task Name** — command | model`)
- Subsequent `_worktree new` succeeds

**FR-2: Derive task metadata from user request**
Derive reasonable metadata: task name (normalized), command (from plan state or user instruction), model tier (default sonnet).

### Constraints

**C-1: Skill-layer change only** — prose addition to worktree SKILL.md Mode A. No CLI code changes — CLI's strict exact-match behavior is correct.
