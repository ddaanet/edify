# Runbook Outline Review: pushback-improvement

**Artifact**: plans/pushback-improvement/runbook-outline.md
**Design**: plans/pushback-improvement/design.md
**Date**: 2026-02-14T18:45:00Z
**Mode**: review + fix-all

## Summary

The outline provides a clear, execution-ready plan for applying three behavioral interventions to fix agreement momentum detection. All requirements are mapped, phase structure is coherent, and complexity distribution is appropriate for the mechanical nature of the work. Seven minor issues identified and fixed related to precision, model tier alignment, and execution guidance.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-2 (Agreement momentum detection) | 1 | 1.1-1.3 | Complete | All three interventions address this requirement |
| FR-1 (Structural pushback) | 1 | 1.2 | Complete | Evaluation checklist preserved in Intervention B |
| FR-3 (Model selection) | 1 | — | Complete | Model Selection section explicitly unchanged |
| NFR-1 (Not sycophancy inversion) | 1 | 1.2 | Complete | Closing paragraph preservation enforced, overcorrection safeguard |
| NFR-2 (Lightweight mechanism) | 1 | All | Complete | Same two files, string content changes only |

**Coverage Assessment**: All requirements covered with explicit mappings and verification criteria.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 1 | 4 | Low | 100% | Appropriate for mechanical text replacement |

**Balance Assessment**: Single-phase structure is correct for this task. Work is cohesive (all interventions are text replacements in behavioral rules) and cannot be meaningfully subdivided.

### Complexity Distribution

- **Low complexity phases**: 1
- **Medium complexity phases**: 0
- **High complexity phases**: 0

**Distribution Assessment**: Appropriate. The work is mechanical text replacement following exact specifications in the design.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

**1. Imprecise line number references in Step 1.1**
- Location: Phase 1, Step 1.1
- Problem: Line reference said "section 25-29" but Agreement Momentum section is at lines 23-29
- Fix: Changed to "Agreement Momentum (lines 23-29)" with explicit design text references
- **Status**: FIXED

**2. Imprecise line number references in Step 1.2**
- Location: Phase 1, Step 1.2
- Problem: Line reference said "section 9-21" but Design Discussion Evaluation section is at lines 5-21
- Fix: Changed to "Design Discussion Evaluation (lines 5-21)" with explicit design text references and closing paragraph line number
- **Status**: FIXED

**3. Model tier mismatch with design**
- Location: Phase 1 metadata
- Problem: Outline specified "haiku" but design document Next Steps (line 254) specifies "sonnet" execution model
- Fix: Changed model from haiku to sonnet to align with design recommendation
- **Status**: FIXED

**4. Missing dependency declaration**
- Location: Step 1.4
- Problem: Symlink sync depends on Step 1.3 (hook modification) but dependency not declared
- Fix: Added "Depends on: Step 1.3 (hook file modified)" to Step 1.4
- **Status**: FIXED

**5. Vague line count descriptions**
- Location: Steps 1.1, 1.2, 1.3
- Problem: "Lines affected: ~6 lines" is estimation language, not precise reference to design
- Fix: Replaced line counts with explicit "Before text" / "After text" references to design document sections
- **Status**: FIXED

**6. Incomplete step count**
- Location: Phase 1 metadata
- Problem: "Estimated steps: 3" but Phase 1 contains 4 steps (including Step 1.4)
- Fix: Changed to "Estimated steps: 4"
- **Status**: FIXED

**7. Insufficient execution guidance**
- Location: Expansion Guidance section
- Problem: No specific guidance on how to execute the replacements efficiently or what to verify
- Fix: Added execution notes covering single-file optimization, syntax preservation, and verification criteria
- **Status**: FIXED

## Fixes Applied

- `Phase 1 metadata` — Changed model from haiku to sonnet (design alignment)
- `Phase 1 metadata` — Updated step count from 3 to 4 (accuracy)
- `Step 1.1` — Fixed line number reference (23-29 not "section 25-29"), added explicit design text references
- `Step 1.2` — Fixed line number reference (5-21 not "section 9-21"), added closing paragraph line number and preservation note, added explicit design text references
- `Step 1.3` — Added explicit design text references and verification guidance about syntax preservation
- `Step 1.4` — Added dependency declaration on Step 1.3, added verification criteria for symlink target
- `Expansion Guidance` — Added execution notes for planner covering optimization opportunities, syntax concerns, and verification approach

## Design Alignment

**Architecture**: Outline correctly preserves the two-layer mechanism (fragment + hook) from original design. Changes are content-level within existing layers as specified.

**Module structure**: Steps map directly to design interventions A, B, C with correct file targets. Model Selection section preservation explicitly noted.

**Key decisions**: All design decisions D-8 through D-12 are referenced in Key Decisions Reference section. Research grounding citations included.

**Intervention mapping**:
- Intervention A (Definition Fix) → Step 1.1 ✓
- Intervention B (Protocol Restructure) → Step 1.2 ✓
- Intervention C (Third-Person Reframing) → Step 1.3 ✓
- Symlink sync → Step 1.4 ✓

## Positive Observations

**Clear scope boundaries**: Common Context Elements section explicitly lists IN/OUT scope, preventing scope creep during execution.

**Preservation requirements**: NFR-1 safeguard (closing paragraph preservation) is called out in multiple locations (requirements mapping, Step 1.2, key constraints) ensuring it won't be missed.

**Execution readiness**: Outline already specifies exact files, line ranges, and design document section references. "Phase 0.95 sufficiency" assessment is accurate — this doesn't need full expansion.

**Traceability**: Requirements Mapping table directly links each requirement to implementing steps with notes explaining coverage approach.

**Research grounding included**: Key Decisions Reference section includes all arXiv citations and external sources, providing context for the interventions.

**Realistic complexity assessment**: Low complexity rating is correct for mechanical text replacement with exact before/after specifications.

## Recommendations

**For full runbook expansion** (if performed):
- Load design document first to verify before/after text blocks are correctly identified
- Consider combining Steps 1.1 and 1.2 into single edit session (same file, adjacent sections)
- Add precommit validation step after changes to verify no unintended regressions
- Include restart reminder in final step (hooks require session restart)

**For validation phase**:
- Use existing template at `plans/pushback/reports/step-3-4-validation-template.md`
- Scenario 3 is the primary target (agreement momentum with reasoning corrections)
- Scenarios 1, 2, 4 are regression checks only

---

**Ready for full expansion**: Yes

The outline is structurally sound, all requirements are mapped, phase structure is appropriate, and all issues have been fixed. No unfixable problems identified. Recommend proceeding with runbook creation or promoting outline directly to runbook (as outline suggests at Phase 0.95).
