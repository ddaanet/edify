# Outline Review: commit-cli-tool

**Artifact**: plans/commit-cli-tool/outline.md
**Date**: 2026-02-20T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is architecturally sound and correctly separates LLM-specific concerns (Gate A, message drafting, gitmoji) from scriptable mechanics (Gate B, precommit, staging, submodule coordination). Four issues were found and fixed: one major design conflict between D-2's proposed `cwd` parameter and the existing `-C` arg pattern, one inaccurate skill step numbering, one incomplete failure output format, and one unspecified edge case in D-4. No unfixable issues.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from: session.md task, `/commit` skill (SKILL.md), defense-in-depth decisions, and design decisions from user discussion (as provided in task prompt).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Single `claudeutils commit` command (structured markdown I/O) | D-1, Approach | Complete | stdin/stdout markdown format specified |
| FR-2: `just-lint` option for TDD GREEN WIP commits | D-1 Options, D-5 | Complete | Maps to `just lint` (ruff + docformatter + mypy) |
| FR-3: `no-vet` option to skip Gate B | D-1 Options, D-5 | Complete | WIP and first-commit-in-plan use case specified |
| FR-4: Default validation is `just precommit` (REFACTOR postcondition) | D-5 | Complete | Default row in validation table |
| FR-5: No validate-only mode — always commits | Scope OUT, D-5 | Complete | Single pipeline, no `--check-only` flag |
| FR-6: No skip-validation-entirely option | D-5 | Complete | Escape hatch is removing sandbox blacklist |
| FR-7: Flat file list — git add handles all change types | D-1 Files section | Complete | Explicit note: modifications, additions, deletions |
| FR-8: Gate B scripted vet check (Gate B → scripted check) | D-3 | Complete | Path pattern classification + report discovery |
| FR-9: Submodule coordination (main + agent-core) | D-4 | Complete | Partition, submodule commit first, pointer stage |
| FR-10: Shared `_git()` extraction (no duplication) | D-2 | Complete | Extract to `claudeutils/git.py` |
| FR-11: Tests (CliRunner + real git repos) | Scope IN, Phase Notes | Complete | TDD phases 2-3 unit, phase 4 integration |
| NFR-1: Scripted gate — no LLM judgment | D-3 | Complete | Mechanical path pattern matching only |
| NFR-2: Sole commit path (direct git blacklisted) | Approach | Complete | Stated in opening sentence |
| NFR-3: Structured markdown extensible without code changes | D-1 Parsing rules | Complete | Unknown sections ignored (forward-compatible) |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **D-2 `cwd` parameter approach conflicts with existing codebase pattern**
   - Location: D-2, "Signature extension"
   - Problem: The outline proposed adding `cwd: Path | str | None = None` to the shared `_git()` helper for submodule operations. However, the existing codebase already handles submodule context via `-C agent-core` as leading args — `_probe_registrations` uses `_git("-C", "agent-core", "worktree", ...)` and `_remove_worktrees` uses `_git("-C", "agent-core", "worktree", "remove", ...)`. Adding `cwd` is unnecessary and inconsistent with established patterns.
   - Fix: Replaced `cwd` parameter note with documentation of the existing `-C` arg approach. Added codebase references so implementer can find the existing pattern.
   - **Status**: FIXED

### Minor Issues

1. **Skill Integration step numbering was wrong**
   - Location: Skill Integration section, last sentence
   - Problem: "Steps 2-5 of the current skill" — the SKILL.md has Steps 1, 1b, 2, 3, 4 (no step 5). Numbering was off by one and referenced a nonexistent step.
   - Fix: Changed to "Steps 1-4 of the current skill (validation + discovery, submodule check, message draft, stage+commit)."
   - **Status**: FIXED

2. **Failure output format incomplete — precommit failure not shown**
   - Location: D-1, Output section
   - Problem: Only one failure example (Gate B failure) was provided. A caller parsing structured output needs to know what precommit failure looks like — specifically that `## Gate` appears as `passed` but `## Precommit` appears as `failed`, and `## Result` is absent in all failure cases.
   - Fix: Added precommit failure example. Added note that `## Result` is omitted when no commit was made.
   - **Status**: FIXED

3. **D-4 edge case unspecified — `## Submodule Message` with no submodule files**
   - Location: D-4
   - Problem: Behavior when caller provides `## Submodule Message` but no `agent-core/` paths are in `## Files` was unspecified. Implementer would need to decide: error or ignore?
   - Fix: Added explicit note — silently ignored.
   - **Status**: FIXED

4. **D-4 missing `_is_submodule_dirty()` reference**
   - Location: D-4
   - Problem: D-2 moves `_is_submodule_dirty()` to `git.py` but D-4 didn't show where it gets used in the commit pipeline, leaving the connection implicit.
   - Fix: Added explicit step 2 in D-4 calling `_is_submodule_dirty()` with reference to D-2.
   - **Status**: FIXED

## Fixes Applied

- D-1 Output section — added precommit failure output example; added note that `## Result` is omitted on failure
- D-2 — replaced `cwd` parameter extension with `-C` arg pattern documentation referencing existing codebase usage
- D-4 — added step 2 (submodule dirtiness check via `_is_submodule_dirty()`); added silent-ignore behavior for orphaned `## Submodule Message`
- Skill Integration — corrected "Steps 2-5" to "Steps 1-4" with accurate step descriptions

## Positive Observations

- Clean separation of LLM vs scripted concerns is correct. Gate A + message drafting + gitmoji stay in skill; Gate B + precommit + staging + submodule coordination move to CLI. This is the right decomposition — LLM concerns that require conversation context can't be scripted.
- D-3 production/exempt classification list is complete and matches the vet-requirement.md taxonomy. The `tmp/` exclusion with rationale is correctly included.
- D-1 markdown I/O rationale is well-reasoned — LLM native format eliminates quoting/escaping, multiline is natural, forward-compatible via unknown-section ignore.
- D-5 validation level table covers all four option combinations with no gaps and no escape hatch for skipping validation entirely.
- Phase types (general/TDD) correctly assigned: Phase 1 is structural refactor (general), Phases 2-4 are behavioral with testable contracts (TDD).
- Skill Integration section makes the future simplification explicit — caller knows the target state without reading the current skill in full.

## Recommendations

- **D-3 report freshness gap**: Known limitation is correctly called out. The `mtime(report) > mtime(changed_file)` heuristic would catch stale reports but adds complexity. Defer to follow-up if false passes become an operational problem.
- **Gate B scope for submodule files**: The D-3 production artifact list covers `agent-core/skills/**`, `agent-core/agents/**`, `agent-core/fragments/**`, `agent-core/bin/**` but not `agent-core/scripts/**`. Confirm whether agent-core scripts are subject to the same vet gate as the parent repo's `scripts/**`.
- **`_is_submodule_dirty()` usage in D-4**: The function checks if agent-core has staged/unstaged changes. In D-4, the trigger is "files include `agent-core/` paths" (caller-specified), not dirty detection. Clarify in runbook whether `_is_submodule_dirty()` is a guard (error if submodule unexpectedly dirty) or the primary trigger for submodule commit.

---

**Ready for user presentation**: Yes
