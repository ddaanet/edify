# Deliverable Review: Workwoods Prose & Config Artifacts

**Scope**: Agentic prose (4 skills/fragments) + human documentation (2 files) produced by Workwoods Phases 5-6
**Date**: 2026-02-17
**Design Reference**: `plans/workwoods/design.md`

## Summary

Six files reviewed against design spec. The core design requirements (D-4 bidirectional merge, Phase 5 planstate adoption, Phase 6 jobs.md elimination) are substantially implemented. One critical gap: design skill A.1 is missing plan-archive.md loading (D-8 requirement). The worktree skill has an internal contradiction between Mode C step 3 (no auto-rm) and Usage Notes (claims Mode C includes auto-cleanup). The human documentation file (plan-archive.md) has a duplicate entry and some entries lack the specified richness.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

1. **Design skill A.1 missing plan-archive.md loading**
   - Location: `agent-core/skills/design/SKILL.md` lines 75-98 (Phase A.1 Documentation Checkpoint)
   - Problem: Design spec (line 60) requires "A.1 loads plan-archive.md" per D-8. The A.1 Documentation Checkpoint has no mention of `plan-archive.md`, `plan-archive`, or `archive` anywhere in the file. D-8 specifies: "Loaded at design skill A.1 and RCA sessions." Without this, completed plan context is never surfaced during design research, defeating the purpose of the archive.
   - Fix: Add plan-archive.md to the A.1 hierarchy. Suggested placement: Level 1 (local knowledge), as a conditional read: "Read `agents/plan-archive.md` when design scope overlaps with previously completed plans (prior art, integration points, affected modules)." Alternatively, add as a new conditional level between Level 1 and Level 2.

### Major Issues

1. **Worktree skill: Mode C step 3 contradicts Usage Notes**
   - Location: `agent-core/skills/worktree/SKILL.md` line 92 vs line 126
   - Problem: Mode C step 3 (line 92) correctly implements D-4: "Worktree preserved for bidirectional workflow -- the user decides when to remove it." But the Usage Notes section (line 126) says: "Mode C includes cleanup automatically after successful merge (branch deletion, worktree removal, session.md cleanup via `claudeutils _worktree rm <slug>`)." These are mutually exclusive instructions. An agent executing Mode C will encounter the step 3 instruction first (preserve), but if it reads Usage Notes for reference, it gets the opposite instruction (auto-cleanup).
   - Suggestion: Update line 126 to align with Mode C step 3. Replace "Mode C includes cleanup automatically after successful merge (branch deletion, worktree removal, session.md cleanup via `claudeutils _worktree rm <slug>`)." with "Mode C preserves the worktree after merge -- cleanup is user-initiated via `wt-rm <slug>`."

2. **Handoff skill Principles section contradicts Step 6**
   - Location: `agent-core/skills/handoff/SKILL.md` lines 293-296 vs lines 229-235
   - Problem: Step 6 correctly implements D-8 by writing plan summaries to `agents/plan-archive.md`. But the Principles section (line 293-294) states: "Git history is the archive / No separate archive files needed." This predates the workwoods changes and now contradicts the plan-archive.md workflow. An agent following Principles may skip Step 6, reasoning that git history alone suffices.
   - Suggestion: Update the Principles bullet to acknowledge plan-archive.md. For example: "Git history is the primary archive. Plan summaries go to `plan-archive.md` for on-demand design research (loaded at A.1, not always-on)."

### Minor Issues

1. **Plan-archive.md: duplicate `worktree-skill` entry**
   - Location: `agents/plan-archive.md` lines 50-52 and lines 146-148
   - Problem: Two separate `## worktree-skill` headings with different content. First (line 50): "Worktree skill implementation. 42/42 cycles completed, merged to dev." Second (line 146): "Design.md retained on disk for reference." Duplicate H2 headings create ambiguity for both human readers and programmatic consumers.
   - Note: Merge the two entries into one, or remove the second (line 146-148) which appears to be a metadata note rather than a plan summary.

2. **Plan-archive.md: several entries below specified richness**
   - Location: `agents/plan-archive.md` various entries
   - Problem: Design D-8 specifies "paragraph (2-4 sentences: what was delivered, affected modules, key decisions)." Several entries are a single sentence without "affected modules" or "key decisions": `pushback-improvement` (line 16), `workflow-skills-audit` (line 40), `reflect-rca-sequential-task-launch` (line 44), `handoff-validation` (line 60), `review-requirements-consistency` (line 132), `handoff-lite-issue` (line 140). These are mostly superseded/killed plans where full enrichment may not add value, but they don't meet the stated format.
   - Note: Consider enriching entries that represent real deliverables (pushback-improvement has real artifacts). For truly superseded/killed plans, a single sentence noting disposition is acceptable -- but document this exception in the archive header.

3. **Plan-archive.md: entries not alphabetically sorted**
   - Location: `agents/plan-archive.md` lines 6-152
   - Problem: No clear ordering -- appears to follow migration order from jobs.md. Design doesn't specify sort order, but alphabetical (matching Unscheduled Plans in execute-rule.md) or chronological would improve scanability for human readers and design A.1 consumers.
   - Note: Low priority. Consider sorting alphabetically for consistency with planstate output conventions.

4. **Worktree skill Mode C section header says "cleanup"**
   - Location: `agent-core/skills/worktree/SKILL.md` line 86
   - Problem: Mode C description says "handling the handoff, commit, merge, and cleanup sequence." After D-4, Mode C no longer performs cleanup. The word "cleanup" in the section description is a stale artifact.
   - Note: Remove "and cleanup" from the Mode C section description to match the updated step 3 behavior.

5. **Handoff step 6: no guidance on detecting plan completion**
   - Location: `agent-core/skills/handoff/SKILL.md` lines 229-235
   - Problem: Step 6 says "When a plan completes during this session" but provides no criteria for detecting completion. The agent must infer from conversation context that a plan completed. Since `list_plans()` shows current filesystem status (requirements/designed/planned/ready), a plan that was orchestrated and merged would no longer appear in `list_plans()` output (plans/ directory deleted) or would still show as `ready`. There's no explicit signal for "plan is done."
   - Note: Add a detection hint: "A plan is complete when its orchestration finishes and all phases pass vet. The agent knows this from conversation context (orchestration completed, vet passed, code merged)." This keeps it judgment-based but reduces ambiguity.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| D-4: Bidirectional merge = skill update only | Partial | Mode C step 3 correct (line 92), but Usage Notes contradict (line 126) |
| D-8: Plan archive on demand | Partial | Handoff step 6 writes archive (line 229-235). Design skill A.1 does NOT load it (missing). |
| D-8: Not in CLAUDE.md @-references | Satisfied | No `@agents/plan-archive` or `@plan-archive` in CLAUDE.md |
| Phase 5: execute-rule.md STATUS reads list_plans() | Satisfied | Lines 49, 55 reference `list_plans()` as authoritative source |
| Phase 5: Worktree skill Mode B reads planstate | Satisfied | Line 51 calls `list_plans(Path('plans'))` |
| Phase 6: Handoff writes plan-archive.md | Satisfied | Step 6 (lines 229-235) |
| Phase 6: Design skill A.1 loads plan-archive.md | Missing | No reference to plan-archive in design SKILL.md |
| Phase 6: Remove jobs.md @-reference from CLAUDE.md | Satisfied | No jobs.md reference in CLAUDE.md |
| FR-6: Eliminate jobs.md | Satisfied (in-scope files) | No jobs.md references in any of the 6 reviewed files |

**Gaps:** D-8 is half-implemented -- the write path exists (handoff step 6) but the read path is missing (design A.1). This means plan-archive.md will accumulate entries that are never consumed during design research.

## Positive Observations

- Mode C step 3 wording is precise and actionable: "Worktree preserved for bidirectional workflow -- the user decides when to remove it. Output: ..." -- provides exact output text, leaving no ambiguity.
- execute-rule.md STATUS section cleanly references `list_plans()` as authoritative source with clear format spec for Unscheduled Plans.
- Handoff step 6 is appropriately lightweight -- three lines that specify format and note the relationship to `list_plans()`.
- Worktree skill Mode B correctly references `list_plans(Path('plans'))` with the import path, making the API call deterministic.
- CLAUDE.md is clean of all jobs.md references -- the elimination is complete in the top-level config.
- Plan-archive.md header accurately describes its consumption context ("design research Phase A.1 and diagnostic/RCA sessions").

## Recommendations

- Fix the critical issue (design skill A.1 plan-archive loading) before considering this deliverable set complete -- it's the only functional gap.
- Fix the worktree skill Usage Notes contradiction (major #1) -- this is a single-line edit with high impact since Mode C is a frequently-executed ceremony.
- The handoff Principles contradiction (major #2) is lower urgency since Step 6 is explicit and procedural steps override principles in practice, but should be fixed to prevent confusion.

## Next Steps

- Apply critical fix: add plan-archive.md loading to design skill A.1
- Apply major fix: update worktree SKILL.md Usage Notes line 126
- Apply major fix: update handoff SKILL.md Principles section lines 293-296
- Apply minor fix: deduplicate worktree-skill entry in plan-archive.md
- Optionally: update Mode C section header (line 86) to remove "cleanup"
