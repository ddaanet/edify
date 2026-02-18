# Vet Invariant Scope — Design

## Problem

The worktree-merge-resilience deliverable review found 4 Major issues. Process analysis showed 0 of 4 legitimately belonged at the deliverable review layer — all were catchable earlier in the pipeline.

**Root cause taxonomy:**

| Class | Count | Missed by | Example |
|-------|------:|-----------|---------|
| Design incomplete — resume behavior unspecified | 1 | Outline review | D-5 `parent_conflicts` didn't specify auto-resolution on resume |
| Vet verified delta, not invariant | 2 | Phase checkpoint vet | D-8 checked err=True removal, not "all merge output reaches stdout" |
| Vet scope narrower than invariant domain | 1 | Phase checkpoint vet | resolve.py called during merge but not in changed-files list |

Two distinct failure modes in the vet pipeline:

1. **Delta verification vs invariant verification.** The vet execution context scopes review to `Changed files`. For local requirements (FR-specific behavior), change scope ≈ verification scope. For cross-cutting invariants (D-8 output stream, NFR-2 no data loss, MERGE_HEAD lifecycle), verification scope is broader than change scope. The template has no concept of "files in the invariant's domain."

2. **Final checkpoint scope.** The Phase 5 opus vet already performed cross-cutting audits (all 12 SystemExit calls traced through the system, no data loss audit). But it applied the methodology selectively — exit codes yes, MERGE_HEAD lifecycle no. No criterion specified lifecycle completeness for stateful objects created during the implementation.

## Approach

Three changes to existing artifacts. No new infrastructure.

### Change 1: Verification scope in vet execution context

Add optional `Verification scope` field to the vet execution context template in `pipeline-contracts.md` and `vet-requirement.md`.

```
**Verification scope** (for cross-cutting invariants):
- [invariant]: [files in domain, broader than changed files]
```

**When to populate:** When the phase implements or modifies behavior governed by a cross-cutting design decision (D-N that says "all X must Y" or NFR that spans multiple modules). The orchestrator identifies these from the design document's decision list.

**When to omit:** When all requirements are local to the changed files.

**Mechanical check:** For each cross-cutting D-N or NFR in the phase's scope, list all files that participate in the invariant. `grep` for the relevant pattern (e.g., `click.echo.*err=True` for D-8, `MERGE_HEAD` for lifecycle) across the call graph, not just changed files.

### Change 2: Lifecycle audit criterion for final checkpoint

Add to the orchestrate skill's final-checkpoint instructions: after the last phase completes, the vet scope includes lifecycle audits for stateful objects.

**Criterion:** For every git state object created or consumed by the implementation (MERGE_HEAD, staged content, MERGE_MSG, lock files), trace through all code paths. Flag any path that exits success (code 0) with state still active, or exits failure without preserving state.

This is the same methodology as the exit code audit (trace a value through all paths) applied to git state instead of exit codes.

**Scope definition:** The orchestrator lists stateful objects from the design document. Most implementations won't have any (pure code changes don't create git state). When present, they're identifiable from design decisions that say "leave X in place" or "preserve Y."

### Change 3: Resume completeness in outline review

Add to the outline-review-agent's checklist: for each state machine state or resume path defined in the design, verify the design specifies what happens to auto-resolvable or auto-handled items on resume.

**Criterion:** If state S skips phases that contain auto-resolution logic, the design must specify whether S re-runs that logic or delegates it to the user. Omission is a gap — the implementer will follow the spec literally, producing a partial resume.

**Detection heuristic:** Look for states that skip phases containing `resolve_*`, `auto_*`, or `--ours`/`--theirs` patterns. If the skipped phase has auto-resolution and the resume state doesn't re-apply it, flag.

## Affected Artifacts

| Artifact | Change | Size |
|----------|--------|------|
| `agent-core/fragments/vet-requirement.md` | Add Verification scope field to execution context template | ~10 lines |
| `agents/decisions/pipeline-contracts.md` | Add Verification scope documentation, cross-cutting invariant examples | ~15 lines |
| Orchestrate skill (orchestration-execution section) | Add lifecycle audit criterion to final checkpoint instructions | ~10 lines |
| `agent-core/agents/outline-review-agent.md` | Add resume completeness criterion | ~8 lines |

## Scope Boundaries

**IN:**
- Verification scope field in vet execution context
- Lifecycle audit criterion for final checkpoint
- Resume completeness criterion for outline review

**OUT:**
- Changes to vet-fix-agent behavior (it already reviews what's scoped — the gap is in scoping, not reviewing)
- Automated detection of cross-cutting invariants (orchestrator identifies them manually from design)
- Retroactive fixes to existing plans or runbooks

## Evidence

Source: worktree-merge-resilience deliverable review (`plans/worktree-merge-resilience/reports/deliverable-review.md`).

| Major | Would Change N have caught it? |
|-------|-------------------------------|
| #1 parent_conflicts auto-resolution | Change 3 (resume completeness) |
| #2 precommit stdout dropped | Change 1 (verification scope: grep `capture_output` in merge call graph) |
| #3 submodule MERGE_HEAD lifecycle | Change 2 (lifecycle audit: trace MERGE_HEAD through all paths) |
| #4 resolve.py err=True | Change 1 (verification scope: grep `err=True` in merge call graph) |

## Phase Typing

Single phase, general (prose edits to existing artifacts). No code changes, no tests.
