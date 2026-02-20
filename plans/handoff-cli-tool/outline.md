# Outline: Handoff CLI Tool

**Task:** Mechanical handoff pipeline in CLI, following the worktree CLI pattern.

## Approach

New `handoff/` subpackage under `src/claudeutils/` exposed as `claudeutils _handoff`. Single command that accepts agent-drafted markdown via stdin, writes it to session.md, and returns diagnostic output. Agent retains all judgment (what content to draft, learnings, pending task mutations). CLI handles mechanical writes and diagnostic gathering.

**Inputs (FR-1):** Markdown via stdin with `**Status:**` line marker and `## Completed This Session` heading. No other file inputs — all other session.md mutations (pending task edits, learnings, blockers, reference files) remain agent-owned.

**Outputs (FR-2):** Markdown diagnostics to stdout. Learnings age status, precommit result, git status/diff (suppressed if precommit red means `just precommit` exits non-zero), worktree ls. Sections shown only when noteworthy — no "nothing to report" reporting.

**Remains manual (agent Edit):** Reference files update, pending task mutations, blockers, learnings append + invalidation, gitmoji selection, commit creation (FR-4 and commit pipeline deferred — see Scope OUT).

## Command

### `claudeutils _handoff`

Single command, two modes — fresh (stdin has content) and resume (no stdin, reads state file):

**Fresh** (stdin has content):
```bash
cat <<'EOF' | claudeutils _handoff
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

**Handoff CLI tool design (Phase A):**
- Produced outline
- Review by outline-review-agent
EOF
```

1. Parse stdin for `**Status:**` marker and `## Completed This Session` heading
2. Cache input to state file (before any mutation — enables safe retry)
3. Write status to session.md (overwrite status line)
4. Write completed to session.md (see committed detection below)
5. Run `just precommit`
   - On precommit failure (exit non-zero): output precommit result + learnings age + worktree ls (git status/diff suppressed per D-3), leave state file, exit code 1
6. Output diagnostics (conditional — see D-3)
- On success: delete state file
- On other failure (write error, subprocess error): leave state file, exit with semantic code

**Resume** (no stdin):
```bash
claudeutils _handoff
```

- Load input from `<project-root>/tmp/.handoff-state.json`
- Re-execute pipeline from `step_reached`
- Success: delete state file
- Failure: leave state file, errors to stderr

Agent doesn't re-enter handoff skill on retry — calls `claudeutils _handoff` directly.

## Key Decisions

### D-1: Domain boundaries

| Owner | Responsibility |
|-------|---------------|
| Handoff CLI | Session.md mechanical writes (status overwrite, completed section) + precommit + diagnostics + state caching |
| Worktree CLI | `→ slug` markers |
| Agent (Edit/Write) | Pending task mutations (insertion = judgment), learnings append + invalidation, blockers, reference files |

**Session.md write mechanics:**
- **Status location:** Between first heading (`# Session Handoff:`) and first subheading (`## Completed`). Identified by `**Status:**` line marker. Overwrite in place.
- **Completed location:** Content under `## Completed This Session` heading, bounded by next `##` heading.
- **Committed detection:** Diff the completed section only against HEAD (`git diff HEAD -- agents/session.md`, extract completed section from both versions).
  - No diff → overwrite (prior content committed, new content replaces it)
  - Old content removed, new content present → append (agent cleared old entries, kept new uncommitted work)
  - Old content preserved with additions → **undecided** (open question: should CLI append, overwrite, or error?)
- CLI writes these two sections only. All other session.md sections are agent-owned.

**Learnings flow:** Agent writes learnings (Edit) → reviews combined file for invalidation (semantic anchoring) → then calls CLI. Manual append before invalidation improves conflict detection via spatial proximity.

### D-2: State caching

- Location: `<project-root>/tmp/.handoff-state.json` (project-relative; project root resolved from git toplevel)
- Contents: `{"input_markdown": "...", "timestamp": "...", "step_reached": "..."}`
- `step_reached` values: `"write_session"`, `"precommit"`, `"diagnostics"` — resume starts from failed step. `"write_session"` means session.md write failed (cache exists, safe to retry writes); `"precommit"` means write succeeded but precommit failed; `"diagnostics"` means precommit passed but diagnostic output failed.
- Created at step 2 — before first mutation (enables clean retry if write fails at step 3 or 4)
- Success: file deleted
- Errors go to stderr (agent sees them directly); state file stores only resume position

### D-3: Output format and suppression

Markdown to stdout. Errors to stderr (never mixed into stdout diagnostic output). Semantic exit codes: 0=success (pipeline complete, state file deleted), 1=pipeline error (session.md write failed, precommit failed, subprocess error), 2=guard/validation failure (stdin missing required markers, state file absent on resume).

**Output suppression rules:**
- Precommit result: always shown (clean confirmation or failure details)
- Git status/diff: suppressed if precommit red (noise until precommit passes)
- Learnings age: summary status only (e.g., "3 entries ≥7 active days, 120 lines — consider /remember"), not the full learnings list. Suppressed if no entries have ≥7 active days.
- Worktree ls: suppressed if no worktrees exist

### D-4: Package structure

```
src/claudeutils/handoff/
├── __init__.py
├── cli.py            # Click command, registered as `_handoff` in parent cli.py
├── pipeline.py       # Pipeline + state caching; calls context.py for step 6 diagnostics
└── context.py        # Diagnostic info gathering: invokes learning-ages.py, git status/diff, worktree ls

src/claudeutils/cli.py            # MODIFIED: add_command(handoff) registration
```

## Open Questions

1. **Completed section: old content preserved with additions (USER DECISION NEEDED).** When the completed section has both the prior committed content AND new additions, should the CLI append (new content after old), overwrite (replace with stdin), or error (ambiguous state, let agent resolve)? This is the one unresolved committed-detection case — implementation cannot proceed without a decision on this branch.

## Scope

**IN:**
- `handoff/` subpackage with single CLI command (no subcommands)
- Stdin markdown parsing (status marker + completed heading)
- Session.md mechanical writes (status overwrite, completed section with committed detection)
- Diagnostic output with conditional suppression
- State caching for failure resume
- Tests (CliRunner pattern, mock git repos)
- Registration in main `cli.py`

**OUT:**
- Commit pipeline (precommit gate → stage → commit) — separate `commit-cli-tool` worktree
- Gitmoji auto-selection (FR-4: embedding/cosine similarity over pre-computed vectors) — deferred to `commit-cli-tool` worktree where it belongs; this tool only handles the handoff write + diagnostics pipeline, not commit creation
- Integrated handoff+commit optimization — future work
- Skill modifications (handoff skill updated in separate task)
- Consolidation delegation (already exists in skill)
- Pending task mutations, learnings, blockers, reference files (agent judgment via Edit)
