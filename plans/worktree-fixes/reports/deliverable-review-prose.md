# Deliverable Review: SKILL.md (Phase 3)

**File:** `agent-core/skills/worktree/SKILL.md` (122 lines, 1,191 words)
**Design:** `plans/worktree-fixes/design.md` Phase 3

## Summary

SKILL.md correctly reflects all FR-6 automation changes. The three design requirements (remove manual session.md editing from Modes A/B, simplify Mode C, document automation) are all satisfied. The file is lean (1,191 words, within ideal range), frontmatter follows plugin-dev conventions, and the automation notes are clear.

Two issues found: incomplete allowed-tools list for error recovery paths, and second-person voice in Usage Notes.

## Conformance (Design Phase 3)

- Mode A step 4 manual editing: **Removed.** Line 40 documents automation.
- Mode B step 4 manual editing: **Removed.** Line 67 documents automation.
- Mode C step 3 simplification: **Done.** Line 87 documents `rm` handling cleanup.
- CLI automation documentation: **Done.** Line 117 in Usage Notes.

All four Phase 3 requirements satisfied.

## Findings

### F-1: Allowed-tools list incomplete for Mode C error recovery

**File:** `agent-core/skills/worktree/SKILL.md:9-16`
**Axis:** Functional completeness, Allowed-tools completeness
**Severity:** Major

The `allowed-tools` list permits `Bash(git status:*)` and `Bash(git worktree:*)` but Mode C instructs the agent to execute:
- `git add <file>` (lines 93, 99)
- `git commit --amend --no-edit` (line 100)
- `git submodule status` (line 105)
- `git branch` (line 107)
- `git log` (line 107)

None of these match the two `Bash(git ...)` patterns in allowed-tools. An agent following Mode C error recovery instructions would be blocked by permission restrictions on these commands.

**Fix:** Add `Bash(git add:*)`, `Bash(git commit:*)`, `Bash(git submodule:*)`, `Bash(git branch:*)`, `Bash(git log:*)` to allowed-tools. Alternatively, use a single broad pattern like `Bash(git:*)` if the tool matching supports it.

### F-2: Second-person voice in Usage Notes

**File:** `agent-core/skills/worktree/SKILL.md:115,121`
**Axis:** Agentic prose (plugin-dev best practice: imperative/infinitive, not second person)
**Severity:** Minor

Two sentences use "You" in Usage Notes:
- Line 115: "You can fix conflicts, stage, and re-invoke..."
- Line 121: "When you have created multiple worktrees..."

Plugin skill best practice specifies imperative/infinitive form in the body, not second person.

**Fix:** Rewrite as imperative. Example:
- "Fix conflicts, stage, and re-invoke the merge command without risk of double-merging."
- "When multiple worktrees exist via `wt` (Mode B), merge each back individually..."

### F-3: Glob tool missing from allowed-tools

**File:** `agent-core/skills/worktree/SKILL.md:9-16`
**Axis:** Allowed-tools completeness
**Severity:** Minor

Mode B step 1 requires reading `agents/session.md` and `agents/jobs.md`. While `Read` is listed, `Grep` and `Glob` are not. Mode B step 2 dependency analysis may need to search for blockers or cross-reference plan directories. The agent cannot use Grep/Glob to search for dependency indicators, forcing it to rely solely on Read for file inspection.

This is a minor gap -- Read alone is sufficient for the two known files, but Grep would be useful for robust dependency detection if blockers reference files outside session.md.

## Non-Findings (Verified Correct)

- **Frontmatter description:** Third person ("This skill should be used when...") with specific trigger phrases. Correct per plugin-dev.
- **Trigger phrases:** "create a worktree", "set up parallel work", "merge a worktree", "remove a worktree", "branch off a task", `wt`, `wt merge`, `wt-rm`. Comprehensive.
- **Word count:** 1,191 words. Within ideal range (<2,000), well under 5k max.
- **Output format:** Tab-separated `<slug>\t<path>` matches actual CLI output (cli.py:241).
- **Exit codes:** Mode C correctly documents exit 0 (success), exit 1 (conflicts/precommit), exit 2 (fatal). Matches merge.py implementation.
- **Idempotency claims:** merge.py phases are designed for re-entry. SKILL.md's idempotency claim (line 115) is accurate.
- **`rm` behavior:** Mode C step 3 accurately describes the conditional removal logic matching `remove_worktree_task()` implementation.
- **Continuation fields:** `cooperative: true` with `default-exit: []` -- appropriate for a user-invocable skill that yields control after completing its mode.
- **No stale manual editing instructions:** All manual session.md editing removed from Modes A, B. Mode C only references manual editing for source file conflict resolution (correct).
- **Scope boundaries:** Each mode has clear entry condition (Mode A: `wt <task>`, Mode B: `wt` no args, Mode C: `wt merge <slug>`) and explicit stop points.
