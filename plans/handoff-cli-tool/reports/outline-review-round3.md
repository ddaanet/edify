# Outline Review: handoff-cli-tool (Round 3)

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-02-20T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is a focused, coherent single-command design. Rounds 1 and 2 resolved the structural gaps (FR-1 input ambiguity, FR-4 deferral rationale, staged-changes edge case, committed-detection semantics). One critical issue remained: the pipeline step ordering placed state caching (step 4) after session.md mutations (steps 2–3), making safe retry impossible for write failures — contradicting D-2's stated invariant "created before first mutation." Four additional issues (two major, two minor) were fixed. All issues resolved. Ready for user validation.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from session.md task description and exploration reports (no requirements.md found).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Inputs — status line, completed text via stdin; no other file inputs | Approach (Inputs), D-1 | Complete | Explicit: stdin-only, agent owns all other mutations |
| FR-2: Outputs (conditional) — learnings age, precommit result, git status+diff, worktree ls | Approach (Outputs), D-3 | Complete | Fixed: learnings age threshold now defined (≥7 active days) |
| FR-3: Cache on failure — inputs to state file, rerun without re-entering skill | D-2, run command | Complete | Fixed: step ordering corrected — cache now precedes mutations |
| FR-4: Gitmoji — embeddings + cosine similarity | Scope OUT | Documented deferral | Belongs to commit-cli-tool worktree; rationale explicit |
| FR-5: Worktree CLI pattern — mechanical ops in CLI, judgment in agent | Approach, D-1, D-4 | Complete | Pattern correctly applied throughout |

**Traceability Assessment**: All requirements covered. FR-4 intentionally deferred with documented rationale.

## Review Findings

### Critical Issues

1. **State cache created after mutations — contradicts D-2 invariant**
   - Location: `_handoff run` Fresh run steps 1–6, D-2
   - Problem: Step order was: parse (1) → write status (2) → write completed (3) → cache (4) → precommit (5) → diagnostics (6). D-2 states the cache is "created before first mutation (enables clean retry)" — but steps 2–3 mutate session.md before step 4 creates the cache. A write failure at step 2 or 3 leaves no state file to resume from, making the resume path unreachable for the most likely failure mode (session.md write error). `step_reached = "write_session"` implied the cache would exist when the write failed, which was impossible given the ordering.
   - Fix: Moved cache to step 2 (before any mutation). New order: parse (1) → cache (2) → write status (3) → write completed (4) → precommit (5) → diagnostics (6). Updated D-2 to state "Created at step 2 — before first mutation (enables clean retry if write fails at step 3 or 4)."
   - **Status**: FIXED

### Major Issues

1. **Learnings age threshold undefined**
   - Location: D-3 output suppression rules
   - Problem: "Learnings age: suppressed if no entries near limit" — "near limit" undefined. The exploration report (`explore-handoff-commit.md`) establishes that `learning-ages.py` uses ≥7 active days as the consolidation trigger threshold. An implementer reading the outline has no basis for when to show the learnings section.
   - Fix: Changed to "suppressed if no entries have ≥7 active days (consolidation trigger threshold from `learning-ages.py`)".
   - **Status**: FIXED

2. **context.py / pipeline.py module boundary undefined**
   - Location: D-4 package structure
   - Problem: D-4 listed `pipeline.py` as "Run pipeline + state caching" and `context.py` as "Diagnostic info gathering" without specifying the call relationship. An implementer must decide: does pipeline.py directly call git and learning-ages.py, or does it delegate to context.py? Does context.py have a return type or write to stdout directly? The boundary was implicit.
   - Fix: Added inline comments to package structure: `pipeline.py` "calls context.py for step 6 diagnostics"; `context.py` "invokes learning-ages.py, git status/diff, worktree ls".
   - **Status**: FIXED

### Minor Issues

1. **Exit code semantics underspecified**
   - Location: D-3 output format
   - Problem: "Semantic exit codes (0=success, 1=error, 2=guard/validation)" without mapping to handoff-specific failure modes. A skill invoking the CLI needs to know: does precommit failure return 1 or 2? Does malformed stdin return 1 or 2?
   - Fix: Expanded to "0=success (pipeline complete, state file deleted), 1=pipeline error (session.md write failed, precommit failed, subprocess error), 2=guard/validation failure (stdin missing required markers, state file absent on resume)."
   - **Status**: FIXED

2. **State file path relative in Resume section**
   - Location: `_handoff run` Resume section, D-2
   - Problem: D-2 defined the location as `<project-root>/tmp/.handoff-state.json` but the Resume section still showed the relative `tmp/.handoff-state.json`. An implementer might resolve the path differently than intended.
   - Fix: Updated Resume section to use `<project-root>/tmp/.handoff-state.json`, consistent with D-2.
   - **Status**: FIXED

## Fixes Applied

- `_handoff run` Fresh run steps — Reordered: cache moved from step 4 to step 2 (before any mutation)
- D-2 state caching — Updated description: "Created at step 2 — before first mutation (enables clean retry if write fails at step 3 or 4)"
- D-3 suppression rules — Replaced "near limit" with "≥7 active days (consolidation trigger threshold from `learning-ages.py`)"
- D-3 exit codes — Expanded from abstract codes to handoff-specific failure semantics
- D-4 package structure — Added call-relationship comments to pipeline.py and context.py entries
- Resume section — Changed `tmp/.handoff-state.json` to `<project-root>/tmp/.handoff-state.json`

## Positive Observations

- Single-command design with fresh/resume duality is clean. The state file as the mode signal (absent = fresh, present = resume) eliminates a flag parameter.
- D-1 domain boundary table is complete and non-overlapping. The three owners (Handoff CLI, Worktree CLI, Agent) have disjoint responsibilities.
- Committed-detection via `git diff HEAD -- agents/session.md` is the correct approach — uses git's own notion of committed state, not timestamp heuristics.
- Scope OUT is precise: each deferred item names the worktree it belongs to and why. No "future work" hand-waving.
- D-2's "errors to stderr, state file stores only resume position" is correct separation — keeps stdout clean for the markdown diagnostic output.

## Recommendations

- **User decision needed:** The round-2 recommendation stands — confirm whether the staged-changes append behavior is correct. If precommit runs before the session.md commit, a staged session.md would trigger append mode on the second run (duplicating the completed section). Confirm the expected call sequence: agent stages other files first, then calls `_handoff run`, then commits everything together — or `_handoff run` is always called before any staging.
- **Testing coverage for resume:** Each `step_reached` value (`"write_session"`, `"precommit"`, `"diagnostics"`) should have an independent test verifying resume restarts from the correct step without re-executing earlier steps.

---

**Ready for user presentation**: Yes
