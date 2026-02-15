# Skill Review: review-plan Section 11 Expansion (Step 2.2)

**Artifact**: `agent-core/skills/review-plan/SKILL.md`
**Date**: 2026-02-15
**Mode**: review + fix-all
**Criteria**: plugin-dev-validation (skills)

## Summary

- Sections modified: 11.1, 11.2, 11.3 (General subsections), Section 6 (restart verification)
- Issues found: 2 minor
- Issues fixed: 2
- Unfixable: 0
- Overall assessment: Ready

## Findings

### Minor-1: Stale axis count reference

**Location**: Section 11, intro line
**Problem**: Referenced "four axes" but runbook-review.md (Step 2.1) now defines five axes (added file growth)
**Fix**: Updated to "five axes"
**Status**: FIXED

### Minor-2: Purpose bullet missing file growth

**Location**: Purpose section, LLM failure modes bullet
**Problem**: Listed "vacuity, ordering, density, checkpoints" but omitted file growth (now a full axis in runbook-review.md)
**Fix**: Added "file growth" to the enumeration
**Status**: FIXED

## Verification Checklist

- [x] General subsections added to 11.1 (vacuity): scaffolding-only, merge-candidate, composable changes + heuristic
- [x] General subsections added to 11.2 (ordering): forward references, unvalidated prerequisites, foundation-after-behavior
- [x] General subsections added to 11.3 (density): <20 LOC delta, collapsible sequences, over-granular decomposition
- [x] Criteria concrete: each bullet has specific detection heuristic (LOC thresholds, structural patterns)
- [x] Criteria distinct from TDD: General focuses on step outcomes/artifacts, TDD focuses on RED/GREEN/assertions
- [x] Section numbering preserved: 11.1, 11.2, 11.3, 11.4 intact
- [x] Restart-reason verification added to Section 6 (Metadata Accuracy)
- [x] Restart triggers enumerated (agents, hooks, plugins, MCP)
- [x] Non-triggers enumerated (decision docs, skills, on-demand fragments)
- [x] @-reference vs index-recall distinction documented
- [x] Frontmatter valid (name, description, user-invocable present)
- [x] Progressive disclosure maintained (criteria organized by section)
- [x] Imperative form used throughout additions
