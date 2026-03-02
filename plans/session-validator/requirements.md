# Session.md Validator

## Problem

`agents/session.md` is consumed by multiple tools: handoff skill (read/write), worktree CLI (`new --task`, `rm` task movement), `#status` display, `task-context.sh` (git log -S lookup). Each assumes specific formatting — task lines match `- [ ] **Name** — ...`, sections appear in a fixed order, file references point to real paths. Format drift causes silent failures: worktree ops can't find tasks, status display misparses metadata, stale references mislead agents.

No validation currently exists for session.md. `validate-memory-index.py` validates the memory index via precommit; session.md has no equivalent.

**Prior art:** A handoff validation task previously existed but was dropped because agent-based review of handoff content was impractical (requires judgment about completeness, relevance). This proposal is different: scripted mechanical validation of format and referential integrity, not content quality.

**Recovery note:** Search git history (`git log -S "handoff validation" -- agents/session.md`) for the prior task to check whether it captured additional requirements beyond what's listed here.

## Functional Requirements

**FR-1: Section schema validation**

Validate that session.md contains only allowed sections in the correct order.

Allowed sections (from handoff skill):
1. `## Completed This Session`
2. `## Pending Tasks`
3. `## Blockers / Gotchas`
4. `## Reference Files`
5. `## Next Steps`

Acceptance criteria:
- Error on unrecognized `## ` headings (e.g., `## Learnings`, `## New Tasks`)
- Error on sections out of order (e.g., Next Steps before Pending Tasks)
- All sections optional (a valid session.md may omit some)
- H1 header (`# Session Handoff: ...`) required as first line

**FR-2: Task format validation**

Validate that task lines in Pending Tasks match the expected pattern.

Acceptance criteria:
- Task lines match `- [ ] **Name** — description` or `- [x] **Name** — description`
- Worktree markers match `→ \`slug\`` when present (inline format after Worktree Tasks elimination)
- Model tier if present is one of: `haiku`, `sonnet`, `opus`
- Task names are unique across the file
- Sub-items (indented bullets) are allowed but not validated beyond indentation

**FR-3: Reference validity**

Validate that file paths referenced in session.md point to real files.

Acceptance criteria:
- Paths in `## Reference Files` section exist on disk
- No `tmp/` paths anywhere in session.md (ephemeral references don't survive sessions)
- Backtick-wrapped paths in task metadata (e.g., `Plan: foo/bar`) are checked if they look like filesystem paths
- Warnings (not errors) for paths that don't exist — allows references to files created by future work

**FR-4: Worktree marker cross-reference**

Validate that `→ \`slug\`` markers in Pending Tasks correspond to actual worktrees.

Acceptance criteria:
- Each slug marker maps to an entry in `git worktree list` output
- Worktrees in `git worktree list` that don't appear as markers produce a warning (orphaned worktree)
- Main worktree excluded from cross-reference

**FR-5: Status line validation**

Validate the H1 header and status line.

Acceptance criteria:
- H1 matches `# Session Handoff: YYYY-MM-DD`
- Status line (bold text on line 3) exists and is non-empty

**FR-6: Plan archive coverage**

Validate that deleted plan directories have corresponding entries in `agents/plan-archive.md`.

Acceptance criteria:
- Compare plan directories staged for deletion (or absent from `plans/` but referenced in git history) against H2 headings in `plan-archive.md`
- Error when a plan directory is deleted without a matching archive entry
- Only applies to plans that had substantive content (at least one `.md` file beyond `.gitkeep`)
- Scoped to precommit: checks staged deletions in `plans/*/` against archive headings

**FR-7: Task command semantic validation**

Validate that command fields in task lines don't contain known anti-patterns.

Acceptance criteria:
- `/inline plans/.* execute` pattern flagged as error (bypasses Phase 2 recall D+B anchor)
- Pattern list extensible without extraction layer changes

## Non-Functional Requirements

**NFR-1: Precommit integration**
Runs as a `just precommit` check alongside existing validators. Exit 0 on success, exit 1 on validation errors. Warnings printed to stderr but don't fail the check.

**NFR-2: Autofix where possible**
Follow `validate-memory-index.py` pattern: `--fix` flag applies mechanical fixes (section reordering, stale reference removal). Schema violations and task format errors are reported, not autofixed.

**NFR-3: Dependency on format finalization**
FR-2 and FR-4 depend on the Worktree Tasks elimination (inline `→ slug` markers). Implement after the `worktree-cli-default` task lands the new format. FR-1, FR-3, FR-5 can be implemented against the current format.

**NFR-4: Shared parsing layer**
Consolidate session.md task-line parsing into a single extraction module. Currently three independent `TASK_PATTERN` regexes exist (`validation/session_structure.py`, `validation/tasks.py`, `worktree/session.py`) with subtly different capture semantics. New validators must consume the shared layer, not add additional regex copies.

## Implementation Notes

- Pattern: `validate-memory-index.py` — same structure (argparse, `--fix`, precommit integration, exit codes)
- Location: extend existing `src/claudeutils/validation/` modules (not `agent-core/bin/`)
- Existing validators already cover partial scope: `session_structure.py` (cross-section uniqueness, reference files), `tasks.py` (task name format/uniqueness/history), `session_refs.py` (tmp/ path rejection)
- Shared parsing module: extract common task-line parsing from validators + `worktree/session.py` into single source
- Worktree list parsing: reuse `_parse_worktree_list` from `worktree/utils.py` or shell out to `git worktree list --porcelain`
- Section ordering: compare indices of found sections against the canonical order list
