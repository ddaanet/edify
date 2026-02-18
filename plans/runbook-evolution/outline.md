# Runbook Evolution — Outline

## Approach

Add three generation directives to runbook SKILL.md that address recurring quality gaps in generated runbooks. Each FR targets a specific failure class observed in deliverable reviews.

All changes are additive prose edits to SKILL.md and its reference files. No code, no new files, no pipeline enforcement changes.

## Key Decisions

- **Placement:** FR-3 (testing diamond) gets a new top-level section in SKILL.md because it's fundamental strategy, not a phase-specific concern. FR-1 and FR-2 are constraints on outline/expansion generation — they slot into Phase 0.75 and Phase 1.
- **Testing diamond replaces implicit pyramid.** Current SKILL.md has integration tests only in Checkpoints (xfail pattern for composition tasks). Diamond makes integration the default layer, unit the exception. The xfail checkpoint pattern stays but integration becomes the primary test layer during cycle planning.
- **FR-3c/FR-3d generalize existing decisions.** `testing.md` "When Preferring E2E Over Mocked Subprocess" covers git specifically. FR-3c generalizes to all subprocess domains. FR-3d adds local-substitute pattern (SQLite, local services). Both are generation directives in SKILL.md, not changes to testing.md.
- **FR-1 exception mechanism.** FR-2a (migration consistency) is the only exception to prose atomicity. The directive references FR-2a explicitly rather than creating a generic escape hatch.
- **FR-2b codifies existing decision.** `workflow-advanced.md` already has "When Bootstrapping Self-Referential Improvements." The SKILL.md directive references it and adds concrete guidance for outline ordering.
- **Single holistic edit per file.** SKILL.md receives one comprehensive edit pass covering all three FRs. Anti-patterns.md receives one edit pass. Consistent with FR-1 (prose atomicity applied to the implementation itself).

## Scope

**IN:**
- `agent-core/skills/runbook/SKILL.md` — new Testing Strategy section, additions to Phase 0.75 verification, additions to Phase 1 TDD Cycle Planning
- `agent-core/skills/runbook/references/anti-patterns.md` — new anti-pattern entries

**OUT:**
- Plan-reviewer enforcement criteria (strategy-agnostic, unchanged)
- Vet-fix-agent criteria (unchanged)
- `agents/decisions/testing.md` (historical record, not revisionist)
- Test suite migration (FR-5, separate design)
- FR-4 (deferred enforcement, observe first)

## Insertion Points in SKILL.md

### New section: "Testing Strategy" (after line 791, between "What NOT to Test" and "Cycle/Step Ordering Guidance")

Content covers:
- Diamond shape: integration tests as default layer (FR-3a)
- Unit tests as surgical supplement with explicit criteria (FR-3b)
- Real subprocesses for subprocess domains (FR-3c) — generalizes testing.md git decision
- Local substitutes for external dependencies (FR-3d)

### Addition to Phase 0.75 verification checklist (after line 253)

Two new verification bullets:
- Prose atomicity: all edits to a prose artifact land in a single item (FR-1)
- Self-modification ordering: tool improvements precede tool usage (FR-2b), with expand/contract exception for migration (FR-2a)

### Addition to TDD Cycle Planning Guidance (after line 535, after GREEN specification)

- Integration-first cycle ordering: plan integration test cycles before/alongside unit cycles
- Wire-then-isolate: default to testing through production call paths, add unit cycles only for combinatorial or edge-case coverage

### Anti-patterns.md additions

- "Split prose edits across steps" (FR-1)
- "Unit-test-only coverage" / "Missing integration wiring tests" (FR-3a — strengthens existing "Missing integration cycles" entry)
- "Mocked subprocess when real is fast" (FR-3c)

## Open Questions

None. Requirements are well-specified with clear rationale and evidence.
