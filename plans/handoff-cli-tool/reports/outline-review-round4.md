# Outline Review: handoff-cli-tool (Round 4)

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-02-20T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is in good shape after three prior rounds. Three issues were found and fixed: the precommit failure / diagnostic output interaction was ambiguous (when precommit fails, only git status/diff is suppressed per D-3, but the step list didn't clarify which diagnostics still run on precommit failure); the resume prose used `_handoff` where the full `claudeutils _handoff` command form should appear; and D-4's cli.py annotation was ambiguous about whether `_handoff` was the Click name or the CLI prefix. The one remaining open question (committed detection: old content preserved with additions) has been flagged more explicitly as requiring user decision before implementation can proceed.

**Overall Assessment**: Ready (one user decision still needed — see Open Questions)

## Requirements Traceability

Requirements derived from session.md task description and exploration reports (no requirements.md found).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Inputs — status marker + completed heading via stdin; no other file inputs | Approach (Inputs), D-1 | Complete | Explicit: stdin-only, agent owns all other mutations |
| FR-2: Outputs (conditional) — learnings age, precommit result, git status+diff, worktree ls | Approach (Outputs), D-3 | Complete | Fixed: precommit failure behavior now explicit for each output type |
| FR-3: Cache on failure — inputs to state file, rerun without re-entering skill | D-2, Command section | Complete | step_reached values enumerated, resume path documented |
| FR-4: Gitmoji — embeddings + cosine similarity | Scope OUT | Documented deferral | Belongs to commit-cli-tool worktree; rationale explicit |
| FR-5: Worktree CLI pattern — mechanical ops in CLI, judgment in agent | Approach, D-1, D-4 | Complete | Pattern correctly applied throughout |

**Traceability Assessment**: All requirements covered. FR-4 intentionally deferred with documented rationale.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Precommit failure / diagnostic output interaction ambiguous**
   - Location: Command section Fresh run steps 5–6
   - Problem: D-3 specifies "git status/diff: suppressed if precommit red" — but doesn't state what happens to the other three diagnostic types (precommit result, learnings age, worktree ls) when precommit fails. The step list said "On failure: leave state file, exit with semantic code" which implied ALL diagnostics were skipped on failure, contradicting D-3's intent (precommit result "always shown"). An implementer faced with a precommit failure would not know whether to emit any output before exiting.
   - Fix: Added explicit failure behavior to step 5: "On precommit failure (exit non-zero): output precommit result + learnings age + worktree ls (git status/diff suppressed per D-3), leave state file, exit code 1". Updated step 6 failure note to "On other failure (write error, subprocess error)" to clarify it covers the non-precommit cases.
   - **Status**: FIXED

### Minor Issues

1. **Resume prose used bare `_handoff` instead of full command**
   - Location: Command section, Resume mode, final sentence
   - Problem: "Agent doesn't re-enter handoff skill on retry — calls `_handoff` directly." The prefix `_handoff` alone is not the invocable form; the full command is `claudeutils _handoff`. Other references in the outline use the full form consistently.
   - Fix: Changed to `claudeutils _handoff`.
   - **Status**: FIXED

2. **D-4 cli.py annotation ambiguous about registration name**
   - Location: D-4 package structure
   - Problem: `cli.py # Click command (_handoff)` — the `(_handoff)` parenthetical could mean either "the Click command object is named `_handoff`" or "this handles the `_handoff` CLI prefix". An implementer would not know whether to define `@click.command(name="_handoff")` here or in the parent registration call.
   - Fix: Changed annotation to "Click command, registered as `_handoff` in parent cli.py" — makes clear the name comes from the parent registration, not from this file's Click definition.
   - **Status**: FIXED

3. **Open question framing too low-key for a blocking decision**
   - Location: Open Questions section
   - Problem: The one remaining open question (committed section: old content preserved with additions) is framed identically to questions that have been resolved. It is the only committed-detection case that blocks implementation — implementers reaching this branch have no action to take. The framing did not signal this urgency.
   - Fix: Added "(USER DECISION NEEDED)" to the question title and added: "This is the one unresolved committed-detection case — implementation cannot proceed without a decision on this branch."
   - **Status**: FIXED

## Fixes Applied

- Command / Fresh run step 5 — Added explicit precommit failure behavior: output precommit result + learnings age + worktree ls, suppress git status/diff, leave state file, exit code 1
- Command / Fresh run step 6 — Updated failure note from "On failure" to "On other failure (write error, subprocess error)" to distinguish from the precommit failure case above
- Command / Resume, final sentence — Changed `_handoff` to `claudeutils _handoff`
- D-4 package structure — Changed `cli.py` annotation from `# Click command (_handoff)` to `# Click command, registered as '_handoff' in parent cli.py`
- Open Questions — Added "(USER DECISION NEEDED)" and blocking-implementation note to question 1

## Positive Observations

- Single-command design with stdin-presence as mode signal (no flag) is clean.
- D-1 domain boundary table is precise and complete — three owners with non-overlapping responsibilities.
- D-2 state caching before first mutation (step 2) is correct — ensures resume is reachable even if the session.md write fails.
- Scope OUT is well-bounded with explicit placement for each deferred item.
- D-3 suppression rules are specific: each of the four output types has an explicit condition. After this round's fix, the precommit failure case is now consistent with those rules.

## Recommendations

- **User decision needed:** The committed-detection third case (old content preserved with additions) must be resolved before implementation. The options are: (a) append — new content goes after existing, (b) overwrite — stdin replaces everything, (c) error — ambiguous state, surface to agent. Consider: append risks duplication if agent re-runs handoff; overwrite risks dropping uncommitted additions; error is safest but puts burden on agent to resolve. Recommend: error with a clear message that describes the ambiguous state, letting the agent use Edit to clean up before retrying.
- **Testing coverage for each precommit failure diagnostic path:** The new step 5 behavior (output precommit + learnings age + worktree ls on failure) should be tested explicitly — the suppression of git status/diff combined with emission of other types is easy to get wrong.

---

**Ready for user presentation**: Yes
