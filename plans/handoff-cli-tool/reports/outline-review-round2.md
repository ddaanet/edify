# Outline Review: handoff-cli-tool (Round 2)

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-02-20T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline represents a significantly redesigned scope compared to round 1: the 4-command structure (`info`, `gitmoji`, `commit`, `resume`) has been replaced with a single `_handoff run` command focused exclusively on the handoff write + diagnostics pipeline. Commit and gitmoji are explicitly deferred. This is a coherent scope reduction, not a gap. Four issues were identified and fixed: FR-1 had an ambiguous "optional files" gap, FR-4 deferral lacked rationale, the "precommit red" condition was undefined, and the committed-detection edge case (staged changes) was undocumented. All issues fixed.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from session.md task description and exploration reports (no requirements.md found).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Inputs — status line, completed text, optional files, commit message | Approach, D-1 | Complete | Fixed: Added explicit note that no other file inputs are accepted; optional files / commit message are agent-owned. Exploration report `input_markdown` field in state cache confirms single-blob stdin model. |
| FR-2: Outputs (conditional) — learnings age, precommit result, git status+diff, worktree ls | Approach, D-3 | Complete | Fixed: Added definition of "precommit red" (non-zero exit from `just precommit`) which was previously implicit |
| FR-3: Cache on failure — inputs to state file, rerun without re-entering skill | D-2, run command | Complete | Fixed: Added JSON key names and `step_reached` value semantics (what each value means for resume). Verified 3 values match the 3 pipeline steps in scope. |
| FR-4: Gitmoji — embeddings + cosine similarity over pre-computed vectors | Scope OUT | Documented deferral | Fixed: Added explicit rationale in Scope OUT explaining gitmoji belongs with commit pipeline, not handoff. Not missing — intentional scope boundary. |
| FR-5: Worktree CLI pattern — mechanical ops in CLI, judgment in agent | Approach, D-1, D-4 | Complete | Pattern correctly applied: CLI writes session.md sections, agent owns all judgment calls. |

**Traceability Assessment**: All requirements covered. FR-4 intentionally deferred with documented rationale.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **FR-4 deferral had no rationale**
   - Location: Scope OUT
   - Problem: "Gitmoji auto-selection (embedding/cosine similarity) — future research" — the original wording implies uncertainty ("future research") rather than a firm design decision. Users reading this wouldn't know whether gitmoji was dropped, unresolved, or placed elsewhere.
   - Fix: Rewrote Scope OUT entry to name FR-4 explicitly, state where it belongs (`commit-cli-tool` worktree), and explain why (handoff handles write + diagnostics, not commit creation).
   - **Status**: FIXED

2. **FR-1 "optional files" not addressed**
   - Location: Approach (Inputs section)
   - Problem: Exploration report's state cache struct included `optional_files`. The outline said "Markdown via stdin" without clarifying what happened to file inputs. A reader implementing from this outline would face ambiguity: does the CLI accept file paths? Pipe multiple files?
   - Fix: Added explicit sentence to FR-1 inputs: "No other file inputs — all other session.md mutations remain agent-owned." Combined with the state cache showing `input_markdown` as a single field, this resolves the ambiguity.
   - **Status**: FIXED

### Minor Issues

1. **"Precommit red" condition undefined**
   - Location: Approach (Outputs), D-3
   - Problem: "suppressed if precommit red" — "red" was undefined. Could mean non-zero exit, specific failure pattern, or lint-only failures.
   - Fix: Added parenthetical definition in FR-2 Outputs: "suppressed if precommit red means `just precommit` exits non-zero".
   - **Status**: FIXED

2. **Committed detection edge case (staged changes) undocumented**
   - Location: D-1 Session.md write mechanics
   - Problem: "git diff HEAD -- agents/session.md" detects uncommitted content in the completed section. But staged (indexed but not committed) changes also appear in `git diff HEAD` — creating potential confusion for an implementer who might expect staged content to be treated as "committed" since it's been `git add`ed.
   - Fix: Added explicit note: staged changes appear in `git diff HEAD` and are treated as uncommitted (append mode). Noted this is intentional behavior.
   - **Status**: FIXED

3. **State cache JSON key names not specified**
   - Location: D-2
   - Problem: D-2 said `{input_markdown, timestamp, step_reached}` using brace notation without distinguishing it from Python dict vs JSON format. JSON keys require quotes; the format was ambiguous.
   - Fix: Changed to `{"input_markdown": "...", "timestamp": "...", "step_reached": "..."}` with JSON syntax and added semantic descriptions for each `step_reached` value.
   - **Status**: FIXED

4. **Mode intro inconsistency**
   - Location: `_handoff run` section
   - Problem: Opening line said "Single command, two modes based on stdin" — technically correct but "based on stdin" doesn't communicate the asymmetry (fresh vs. resume have different behavior chains). A reader might think stdin presence just switches input sources with the same processing.
   - Fix: Changed to "two modes — fresh run (stdin has content) and resume (no stdin, reads state file)" making the asymmetry explicit.
   - **Status**: FIXED

5. **FR-4 reference missing from Approach**
   - Location: Approach, Remains manual section
   - Problem: The "Remains manual" bullet didn't mention gitmoji or commit creation — a user might assume these weren't considered at design time rather than being deliberate exclusions.
   - Fix: Added "gitmoji selection, commit creation (FR-4 and commit pipeline deferred — see Scope OUT)" to the Remains manual section.
   - **Status**: FIXED

## Fixes Applied

- Approach / Inputs — Added explicit note: no file inputs beyond stdin markdown; agent owns all other mutations
- Approach / Outputs — Added definition of "precommit red" (`just precommit` exits non-zero)
- Approach / Remains manual — Added gitmoji and commit creation with pointer to Scope OUT
- `_handoff run` intro — Reworded from "two modes based on stdin" to name fresh/resume explicitly
- D-1 committed detection — Added note on staged changes behavior (append mode, intentional)
- D-2 state cache — Changed to valid JSON format for keys; added semantic descriptions for `step_reached` values
- D-3 output format — Added "(never mixed into stdout diagnostic output)" to error-to-stderr line
- Scope OUT / gitmoji — Named FR-4 explicitly, added rationale (belongs with commit pipeline, not this tool)

## Positive Observations

- Single-command design is the right call. The 4-command structure from round 1 added surface area without corresponding value for the handoff-specific workflow. The `run` / resume duality is clean and operationally clear.
- D-1 domain boundary table is precise. Worktree CLI / Handoff CLI / Agent responsibilities are non-overlapping and complete.
- State caching before first mutation (step 4 in Fresh run) is correct — ensures retry is safe. The "On success: delete" / "On failure: leave" pattern is clean.
- `git diff HEAD -- agents/session.md` for committed detection is a solid approach — it uses git's own understanding of committed state rather than timestamp heuristics.
- Scope OUT is appropriately bounded. Deferring commit pipeline to a separate worktree keeps this tool focused and testable.

## Recommendations

- **User input needed on staged changes edge case:** The committed-detection note now documents that staged session.md content triggers append mode. Confirm this is the intended behavior — if precommit is run before the session.md commit, staging may be a normal intermediate state and append would produce duplicates. Consider whether the detect-and-overwrite case should use `git diff --cached` instead to distinguish staged from unstaged.
- **Testing coverage for resume path:** The outline mentions "CliRunner pattern, mock git repos" but the resume path (no stdin, loads state file, re-executes from `step_reached`) is the complex path. Implementation should test each `step_reached` value independently.
- **Learnings age threshold not specified:** D-3 says "learnings age: suppressed if no entries near limit" but "near limit" is not defined. The `learning-ages.py` script uses ≥7 active days as the consolidation trigger. Implementation should use the same threshold to determine when to show the learnings section.

---

**Ready for user presentation**: Yes
