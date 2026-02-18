# Worktree Merge From Main

## Requirements

### Functional Requirements

**FR-1: Worktree-focused session.md preservation**
Worktree session.md contains only the task(s) relevant to this worktree. Main's session.md contains the full task backlog. Merging main's session.md into the worktree destroys focus. Policy: always keep ours for session.md.

Acceptance criteria:
- session.md conflict resolved as "ours" automatically
- No manual intervention needed for session.md

**FR-2: Learnings merge — theirs base plus branch additions**
Use main's learnings as the base, append entries unique to this branch. Main is authoritative (memory consolidation happens there). Branch additions are the delta from merge-base to HEAD.

Acceptance criteria:
- Start with main's (theirs) learnings content
- Compute branch additions: entries in HEAD that are not in merge-base version
- Append branch additions after main's content
- Entries present in both are not doubled

**FR-3: Accept main's structural file changes**
Files deleted or restructured on main (e.g., `agents/jobs.md` replaced by planstate) should be accepted. The worktree branch's modifications to now-deleted files are stale.

Acceptance criteria:
- Delete/modify conflicts resolved as "theirs" for infrastructure files
- List of affected files reported

**FR-4: Sandbox bypass**
`git merge` writes to `.claude/` directory (agents, settings, hooks via symlinks). Sandbox blocks these writes, leaving the merge partially applied with orphaned untracked files. The entire operation must run with sandbox bypass.

Acceptance criteria:
- All git operations run without sandbox restrictions
- No partial merge states from sandbox interruption

**FR-5: Idempotent resume (includes untracked debris cleanup)**
If the merge is interrupted or partially completed, re-running the operation should detect current state and resume. Untracked file collisions (from prior worktree→main merges leaving debris, or from a sandbox-interrupted merge) are the same problem in both merge directions: `git merge` refuses to start. Cleaning colliding untracked files is a precondition for merge start, shared with worktree-merge-resilience FR-3.

Acceptance criteria:
- Untracked files that collide with incoming tracked files are `git add`ed before merge (lets git do proper three-way merge)
- Untracked files NOT on incoming branch are preserved
- Detects MERGE_HEAD (merge in progress) and resumes conflict resolution
- Detects already-merged state (main is ancestor of HEAD) and reports "already up to date"
- Does not create duplicate merge commits

### Non-Functional Requirements

**NFR-1: Minimal output**
Report: files cleaned, submodule updated, conflicts resolved, merge result. No verbose play-by-play.

**NFR-2: No data loss**
No code path should discard worktree-branch work. Session.md focus, branch-specific learnings, and uncommitted changes must survive.

### Constraints

**C-1: Unify with existing merge infrastructure**
Existing `merge.py` has a 4-phase pipeline (validate → submodule → merge+resolve → commit+precommit) and `resolve.py` has session.md and learnings.md resolution strategies. The sync-from-main operation shares the same pipeline — submodule handling, untracked debris cleanup, and idempotent resume are direction-independent problems with the same solutions.

Shared (direction-agnostic, parameterize target branch):
- `_check_clean_for_merge()` — clean tree validation
- `_phase2_resolve_submodule()` — submodule handling (already merges a target commit)
- `_phase4_merge_commit_and_precommit()` — commit + precommit (parameterize message)
- `_format_git_error()` — error formatting
- Untracked debris cleanup — `git add` colliding files before merge (new, shared with worktree-merge-resilience FR-3)
- Idempotent resume — MERGE_HEAD detection, already-merged detection (partially exists in phase 4)

Direction-specific resolution policies:
- `resolve_session_md()` — worktree→main: merge new tasks from theirs. main→worktree: keep ours entirely
- `resolve_learnings_md()` — worktree→main: ours-base + theirs additions. main→worktree: theirs-base + ours additions (inverted)
- Delete/modify conflicts — worktree→main: not applicable. main→worktree: accept theirs (FR-3)

New for sync (genuinely new):
- Delete/modify conflict auto-resolution (FR-3)
- Direction-aware orchestration function (calls shared phases with direction-specific policies)

Implementation should extend existing modules, not duplicate. A direction parameter threads through shared phases; resolution policies are the only behavioral difference.

**C-2: Requires clean tree**
Operation requires clean git tree before starting (no uncommitted changes). Consistent with `_worktree merge` behavior.

**C-3: Worktree skill integration**
Invocable from worktree skill as a new mode (e.g., Mode D: Sync from main), with exit code contract matching existing modes.

### Out of Scope

- Source code conflict resolution — report conflicts, let agent/user resolve
- Automatic rebase (merge-only, preserves branch topology)
- Remote fetch — operates on local main branch only

### Resolved Questions

- Q-1: **`_worktree merge --from-main` (flag on existing command).** Both directions share the same pipeline, ceremony, and lifecycle (merge no longer deletes worktree — incremental merge is the default). Direction is a parameter of the same operation: `merge <slug>` = worktree→main, `merge --from-main` = main→worktree. Resolution policies are the only behavioral difference, and those are internal.

### References

- This session's manual merge — all FRs directly observed
- `plans/worktree-merge-resilience/requirements.md` — same direction problems (untracked files, idempotent resume, submodule handling)
- `src/claudeutils/worktree/merge.py` — existing 4-phase merge pipeline (shared)
- `src/claudeutils/worktree/resolve.py` — session.md and learnings.md resolution strategies (direction-invertible)
- `agent-core/skills/worktree/SKILL.md` — Mode C contract, Mode D would follow same pattern
- `agents/session.md` Blockers — "Never run git merge without sandbox bypass"
