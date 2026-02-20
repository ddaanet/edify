# Outline Review: commit-cli-tool

**Artifact**: plans/commit-cli-tool/outline.md
**Date**: 2026-02-20T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is architecturally sound after two prior review cycles. All requirements from the user discussion are correctly addressed. Three minor gaps were found and fixed: the D-4 pre-staged agent-core behavior was implicit, the D-1 output section only showed one gate failure format (missing-report) when two exist (also stale-report), and unknown option values in `## Options` had no specified error behavior.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from: task prompt design decisions (user discussion context), session.md task description.

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Structured markdown I/O (not CLI flags) | D-1, Approach | Complete | stdin/stdout markdown, rationale specified |
| FR-2: Files section first, Message section last (blockquoted) | D-1 Sections | Complete | Section order and blockquote protection explicit |
| FR-3: `just-lint` option for TDD GREEN WIP | D-1 Options, D-6 | Complete | Maps to `just lint`; table shows all combinations |
| FR-4: `no-vet` option to skip Gate B | D-1 Options, D-6 | Complete | WIP and first-commit-in-plan use case specified |
| FR-5: Gate patterns from pyproject.toml `require-review` | D-3 | Complete | Config structure shown, opt-in semantics specified |
| FR-6: Report freshness via mtime comparison | D-3 | Complete | Newest artifact vs newest report, stale failure output shown |
| FR-7: Input validation — clean files → STOP error | D-5, D-1 output | Complete | Clean-files error with STOP directive in output format |
| FR-8: Submodule message symmetric validation | D-4 | Complete | 4-row table, all states covered |
| FR-9: Error taxonomy — Stop vs Warning+proceed | D-1 Error taxonomy | Complete | Definitions and rationale provided |
| FR-10: No validate-only mode — always commits | D-6, Scope OUT | Complete | Explicitly excluded from scope |
| FR-11: Direct git blacklisted — CLI is sole commit path | Approach | Complete | First sentence states this |
| NFR-1: No hardcoded paths, no submodule internal knowledge | D-3 | Complete | Gate config belongs to each project |
| NFR-2: Scripted gate — no LLM judgment | D-3 | Complete | Mechanical path pattern matching only |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **D-4 pre-staged agent-core behavior implicit**
   - Location: D-4 Commit sequence
   - Problem: The symmetric validation table says "agent-core paths in `## Files` OR staged in index" as the trigger for requiring `## Submodule Message`. But the commit sequence only described partitioning `## Files`. Behavior for already-staged agent-core content (not in `## Files`) was unspecified — implementer could miss that pre-staged changes still require the submodule message.
   - Fix: Added explicit paragraph after commit sequence: pre-staged agent-core changes are included in step 2's staging, and the submodule message requirement applies equally to pre-staged index content.
   - **Status**: FIXED

2. **D-1 gate failure output only showed missing-report format**
   - Location: D-1 Output section, Gate failure examples
   - Problem: D-1 showed one gate failure format (`unvetted:` list). D-3 defines a second format (stale-report with `reason:`, `newest-change:`, `newest-report:`). A caller parsing output needs to handle both. Without both formats in D-1, the output specification was incomplete.
   - Fix: Expanded gate failure section to show both subtypes (missing-report and stale-report) with cross-reference to D-3.
   - **Status**: FIXED

3. **Unknown option values in `## Options` had no specified behavior**
   - Location: D-1 Parsing rules
   - Problem: Parsing rules specified behavior for unknown section *names* (treated as message body). No equivalent rule for unknown option *values* within `## Options`. An implementer could choose either silently-ignore or error — both are plausible but only error is safe (typos like `just_lint` would silently proceed with full precommit).
   - Fix: Added explicit rule after parsing rules: unknown option values → error (exit non-zero), rationale includes typo prevention.
   - **Status**: FIXED

## Fixes Applied

- D-4 — Added paragraph specifying pre-staged agent-core behavior (included in submodule commit, still requires `## Submodule Message`)
- D-1 Output — Expanded gate failure to show both subtypes: missing-report (`unvetted:`) and stale-report (`reason: stale-report`) with D-3 cross-reference
- D-1 Parsing rules — Added unknown option values → error rule with rationale

## Positive Observations

- The structured markdown I/O design is well-reasoned and complete. Input format, output format, error cases, and warning cases are all specified with concrete examples.
- Symmetric validation table in D-4 is exhaustive — all four states handled, behaviors unambiguous.
- Error taxonomy (Stop vs Warning+proceed) correctly matches risk profile: data-loss or unrecoverable → Stop; detectable discrepancy → Warning+proceed.
- D-3 avoids hardcoding by delegating classification to per-project config. The "no patterns → gate passes" opt-in default is the right default (doesn't break existing projects).
- Phase typing (general/TDD) is correctly assigned. The phase notes correctly flag integration tests as distinct from unit-test-embedded TDD phases.

## Recommendations

- **D-4 `_is_submodule_dirty()` usage**: Review-2 noted ambiguity about whether this function is a guard or a trigger. The current outline uses `## Files` + index check as the trigger; `_is_submodule_dirty()` from D-2 isn't referenced in D-4. Clarify in the runbook whether this function has a role in the commit pipeline or is only needed by the worktree module.
- **Gate B submodule scope**: D-3 says no hardcoded submodule knowledge. But if agent-core files are in `## Files`, Gate B classification runs against the parent's `require-review` patterns — which won't match `agent-core/fragments/**.md`. Confirm whether agent-core files bypass Gate B or whether agent-core should have its own `pyproject.toml` gate config.

---

**Ready for user presentation**: Yes
