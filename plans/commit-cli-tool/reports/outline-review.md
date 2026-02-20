# Outline Review: commit-cli-tool

**Artifact**: plans/commit-cli-tool/outline.md
**Date**: 2026-02-19T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is architecturally sound and feasible. Approach correctly separates LLM-specific concerns (Gate A, message drafting, gitmoji) from scriptable mechanics (Gate B, precommit, staging, submodule coordination). Four issues were found and fixed — one major design gap (`tmp/` report search), one missing signature detail for `_git()`, one ambiguity in validate mode, and one vague consolidation note. No unfixable issues.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements are derived from the task description in session.md, the `/commit` skill (SKILL.md), and the defense-in-depth decisions (agents/decisions/defense-in-depth.md).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Single `claudeutils commit` command | D-1, D-5, Scope IN | Complete | Dual-mode on `-m` presence |
| FR-2: Gate B scripted vet check | D-3 | Complete | File classification + report existence |
| FR-3: Submodule coordination (main + agent-core) | D-4 | Complete | Partition, commit submodule first, stage pointer |
| FR-4: Precommit validation (`just precommit`) | D-1, Skill Integration | Complete | `--check` flag controls level |
| FR-5: File staging (specific files, not `-A`) | D-1 commit mode, Scope IN | Complete | Files passed as positional args |
| FR-6: Tests (CliRunner + real git repos) | Scope IN, Phase Notes | Complete | TDD phases 2-3; integration phase 4 |
| NFR-1: Scripted gate (no LLM judgment) | D-3 | Complete | Mechanical path pattern matching |
| NFR-2: Structural alignment with worktree CLI | D-5 | Complete | Same module layout, same registration pattern |
| NFR-3: No `_git()` duplication | D-2 | Complete | Extract to `claudeutils/git.py` |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **`tmp/` in vet report search is unreliable**
   - Location: D-3, "Vet report discovery"
   - Problem: `tmp/` is ephemeral and gitignored. A vet report written to `tmp/` during a previous session may not exist when the gate runs (e.g., after `git clean`, restart, or on a fresh worktree). Using `tmp/` as a search path creates false passes — gate passes because no report is found, not because work was vetted. `plans/*/reports/` is the durable, tracked location.
   - Fix: Removed `tmp/` from discovery scope. Added note explaining the exclusion.
   - **Status**: FIXED

2. **`_git()` signature gap — no `cwd` parameter**
   - Location: D-2
   - Problem: The existing `_git()` in `worktree/utils.py` has no `cwd` parameter. D-4 requires `git -C agent-core` operations (submodule commits/staging), which need working directory control. Without noting this, the implementation phase would either discover the gap mid-cycle or use subprocess directly (breaking the shared helper pattern).
   - Fix: Added signature extension note to D-2: add `cwd: str | None = None` to shared `_git()`, passed as `subprocess.run(..., cwd=cwd)`.
   - **Status**: FIXED

### Minor Issues

1. **Validate mode input source ambiguous**
   - Location: D-1 and Approach section
   - Problem: "Without `-m` → validation only (gate + precommit)" doesn't state what files the gate classifies. Does it take a file list, or classify all dirty files? Without this, Gate B in validate mode has unclear input semantics.
   - Fix: Added "Classifies dirty files (staged + unstaged)" to the Approach dual-mode bullet. Added annotation in D-1 command block.
   - **Status**: FIXED

2. **`--skip-gate` scope undefined**
   - Location: D-1
   - Problem: `--skip-gate` appears in the command signature without definition. Gate A is out of scope; Gate B is the scripted check. Unclear which gate(s) it skips.
   - Fix: Added explicit note: "`--skip-gate` skips Gate B (vet check) only."
   - **Status**: FIXED

3. **`--check none` asymmetry in validate mode**
   - Location: D-1
   - Problem: `--check none` is available in commit mode but not validate mode. The asymmetry is implicit. Without a note, implementer may accept `--check none` in validate mode (pointless — validate mode exists to run checks).
   - Fix: Added annotation in D-1 command block: "`--check none` not valid in validate mode."
   - **Status**: FIXED

4. **Phase consolidation note was vague**
   - Location: Phase Notes
   - Problem: "Phases 2-4 may consolidate depending on runbook tier assessment" gives no guidance. Tests are embedded in TDD phases, not separate — this needed clarification so Phase 4 isn't seen as test-only redundancy.
   - Fix: Replaced with explicit note: consolidation deferred to tier assessment, unit tests embedded in each TDD phase, Phase 4 integration tests are distinct.
   - **Status**: FIXED

## Fixes Applied

- Approach section — added "Classifies dirty files (staged + unstaged)" to validate-mode bullet
- D-1 — added `--check none` validity annotation for validate mode; added explicit `--skip-gate` scope note
- D-2 — added `_git()` signature extension note for `cwd` parameter
- D-3 vet report discovery — removed `tmp/` from search scope, added exclusion rationale
- Phase Notes — replaced vague consolidation note with explicit guidance on test embedding and Phase 4 distinctness

## Positive Observations

- Clean separation of LLM vs scripted concerns: Gate A + message drafting + gitmoji stay in skill; Gate B + precommit + staging + submodule coordination move to CLI. This is the correct decomposition.
- D-3 production/exempt classification list is complete and matches the vet-requirement.md taxonomy.
- D-4 submodule coordination sequence is correct: submodule commit first, then pointer stage, then parent commit. Matches the existing skill behavior.
- D-5 module structure follows worktree CLI pattern exactly — same layout, same registration, same `add_command` call.
- Skill Integration section makes the future skill simplification explicit, enabling the follow-up task to have a clear target state.
- Phase types (general vs TDD) are correctly assigned: Phase 1 is refactor (general), Phases 2-4 are behavioral/testable (TDD).

## Recommendations

- **D-3 stale report gap**: The known limitation (stale reports pass) is correctly called out. Consider whether the gate should check report recency against the changed files' modification time — `mtime(report) > mtime(changed_file)` as a lightweight freshness heuristic. Not required for initial implementation (YAGNI), but worth flagging for user discussion.
- **Validate mode file list**: Confirm that dirty-file detection (staged + unstaged via `git status --porcelain`) is the right scope for validate mode. An alternative is requiring explicit files even in validate mode (symmetric with commit mode). The outline uses dirty-file detection — discuss if explicit file list is preferred.
- **`_git()` cwd vs `-C` flag**: Two options exist — pass `cwd` to subprocess or prepend `-C path` to args. The `cwd` approach is cleaner but changes the shared helper signature. The `-C` approach leaves `_git()` unchanged and passes `-C agent-core` as an arg. Either works; document the choice in the runbook.

---

**Ready for user presentation**: Yes
