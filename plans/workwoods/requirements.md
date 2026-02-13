# Workwoods

## Requirements

### Functional Requirements

**FR-1: Cross-tree status display (wt-ls upgrade)**
Upgrade `wt-ls` to read across all worktrees and display computed live status. Per worktree: session.md base status, commit count since last handoff (via `git log <session.md-last-commit-hash>..HEAD`), latest commit subject, tree clean/dirty state, recency. Sort by most recently committed first.

**FR-2: Vet artifact tracking**
For each worktree (and main), display design/runbook vet chain status. Design chain: outline → design-vet report. Runbook chain: phase files → checkpoint reports. Vet validity determined by filesystem mtime comparison: source artifact mtime > vet report mtime = stale, needs re-vet. Include outline mtime to determine if next step is vet.

**FR-3: Plan state inference from filesystem**
Infer plan state from directory contents and filesystem timestamps, replacing manual jobs.md tracking. Plan directory existence + artifact presence determines state: outline.md exists → designed, phase files exist → planned, vet reports exist and valid → vetted. Next action computed from what exists and timestamp validity.

**FR-4: Bidirectional worktree merge**
`wt-merge` merges worktree into main without deleting the worktree. `wt-rm` is a separate explicit deletion operation. Status snippet in worktree session.md is volatile — squashed on merge. Enables long-lived worktrees that sync back and forth with main.

**FR-5: Additive task merge**
On worktree merge, tasks combine additively (union by task name). Worktrees append new tasks and mark their own completions but never remove other trees' entries. Integrate with worktree-update recovery (R1 auto-combine requirement).

**FR-6: Eliminate jobs.md**
Replace jobs.md manual plan tracking with FR-3 filesystem inference. Plan directories are the source of truth. Every plan status implies a next action (designed → runbook, planned → execute). No separate tracking file needed.

### Non-Functional Requirements

**NFR-1: No writes during execution**
Status is computed on demand from git history + filesystem, not stored. No additional session.md updates or status file writes needed during runbook execution or between handoffs.

**NFR-2: No unversioned shared state**
Each tree owns its own versioned state (session.md). Cross-tree awareness is read-only aggregation by script. No files outside git working trees.

**NFR-3: Stays within git model**
All state is either git-versioned or computed from git-versioned artifacts. No external databases, lockfiles, or coordination mechanisms.

### Constraints

**C-1: Filesystem timestamps for artifact validity**
Use filesystem mtime (not git commit timestamps) for vet staleness detection. Uncommitted modifications must be visible — an edited outline that hasn't been committed yet should still invalidate its vet report.

**C-2: Git commit hash for work counting**
Use `git log -1 --format=%H -- agents/session.md` as anchor for commit counting, not filesystem timestamps. Commit hash is stable across checkout/touch operations.

**C-3: Sandbox permissions already sufficient**
`claudeutils-wt` container directory is already in `.permissions.additionalDirectories`. No new permission configuration needed for cross-tree reads.

### Out of Scope

- Separate tasks.md extraction from session.md — validate carry-forward rule first, revisit if insufficient
- Sonnet-for-TDD model tier change — separate concern, RCA points to planning skill not execution model
- Handoff review agent — cost/benefit rejected

### Dependencies

- worktree-update delivery — FR-4 and FR-5 modify merge behavior in the same codebase
- worktree-update recovery — R1 (auto-combine session.md/jobs.md) overlaps with FR-5

### Open Questions

- Q-1: Exact format of status snippet in each tree — reuse session.md status line, or dedicated lightweight file?
- Q-2: How does wt-ls upgrade interact with existing justfile recipe? Pure replacement or new recipe name?
- Q-3: Scope boundary with worktree-update recovery — what integrates vs what is follow-on?
- Q-4: Transition plan for jobs.md elimination — can it be incremental (script reads both sources during transition)?
