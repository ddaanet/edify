# Brief: Design Context Prerequisite

## 2026-03-25: Agents need design specifications to modify code correctly

**Context:** Handoff-cli-tool deliverable review RC12. A fix for m-2/m-3 (change error type from CommitResult to CommitInputError) introduced a Critical regression — the CLI handler wasn't updated to catch the new exception type. The fixing agent had the deliverable review report (which said "violates S-3") but not the design document (outline.md) where S-3's full contract is defined. Agent inferred S-3's meaning from the finding description, which was incomplete.

**Root cause:** 12 review rounds. The `/design` fix-task template passed only the report path. The report is a diagnostic artifact (what's wrong), not a specification artifact (what's right). Fixing conformance findings without the conformance baseline means reasoning from the failure description, not the contract.

### Principle

Agents modifying existing code must have the system design specification in context. The design document defines correct behavior — without it, the agent infers intent from the implementation, which is circular when the implementation is wrong.

- **Design documents exist** (outline.md, design.md): load before work begins
- **Design documents absent:** reverse-engineer from code + user-validate before proceeding. Do not proceed on inferred intent alone.

### Scope

Applies broadly to any modification workflow:
- `/design` fix routing (the triggering case)
- `/inline` execution on existing code
- Rework cycles
- Maintenance and enhancement work
- Any agent that modifies behavior

### TDD step agent exception

TDD workers are deliberately context-restricted to prevent over-implementation. They see only the step file and test specification. Full design context would let them anticipate future steps and add unspecified behavior. The narrow context window is the feature.

This is not an exemption from the principle — TDD agents already have design context, pre-distilled into step boundaries during runbook generation. The design → step file distillation is where the boundary is set.

### Deliverable

Codify as a fragment governing context loading for modification workflows. Not a per-skill patch — a cross-cutting rule that skills inherit.

Specific fix: `/deliverable-review` Phase 4 fix-task template must include design document path alongside report path.
