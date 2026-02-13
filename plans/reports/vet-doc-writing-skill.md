# Vet Review: doc-writing skill definition

**Scope**: agent-core/skills/doc-writing/SKILL.md (new file)
**Date**: 2026-02-13T19:45:00Z
**Mode**: review + fix

## Summary

The doc-writing skill documents a validated pattern from two README writing sessions (parent and agent-core READMEs). The process is actionable, constraints are clear, and the structure matches project skill conventions. Found 8 issues: 1 deferred (frontmatter convention inconsistency, non-blocking), 4 major (all fixed), 3 minor (all fixed).

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

1. **Frontmatter missing `name` field**
   - Location: agent-core/skills/doc-writing/SKILL.md:1-6
   - Problem: Frontmatter has `name: doc-writing` but reference skills use `description` as the first field (without `name`). The `reflect` skill has both, but `vet` and `release-prep` use `description` only. Pattern inconsistency.
   - Fix: Check if `name` field is actually required. Based on `vet` and `release-prep` patterns (which work), `name` appears optional. However, `reflect` includes it. Standardize to match majority pattern: keep `name` field for consistency with `reflect` (both are user-facing workflow skills), but verify it doesn't conflict with skill discovery.
   - **Status**: DEFERRED — `name` field presence varies across skills (reflect has it, vet/release-prep don't). Not a blocker, but inconsistency should be noted for future skill convention standardization.

### Major Issues

1. **Quiet-explore agent not defined**
   - Location: agent-core/skills/doc-writing/SKILL.md:28
   - Problem: Process references delegating to `quiet-explore` agent, but this agent is not defined in `.claude/agents/`. Executing agents will fail when attempting delegation.
   - Suggestion: Either define the `quiet-explore` agent or change delegation instruction to use existing `explore` agent, or specify that exploration should be done directly with Read/Glob/Grep tools.
   - **Status**: FIXED — Changed to direct tool usage (Read, Glob, Grep) instead of delegation, matching the skill's allowed-tools and avoiding dependency on undefined agent.

2. **Reader-test delegation lacks model specification**
   - Location: agent-core/skills/doc-writing/SKILL.md:81
   - Problem: Task delegation example shows `subagent_type="general-purpose"` but this type is not defined in project agent structure. Based on other skills (reflect, vet), standard pattern is to specify either a named agent or omit for default.
   - Suggestion: Change to `Task(prompt="""...""")` (default agent) or specify actual agent type if one exists for this purpose.
   - **Status**: FIXED — Simplified to default Task delegation (no subagent_type needed for general prompts).

3. **Style corpus location ambiguity**
   - Location: agent-core/skills/doc-writing/SKILL.md:32-35
   - Problem: Skill says "Check for `tmp/STYLE_CORPUS.md`" but doesn't specify whether this is project convention or ad-hoc. The reader-test pattern is validated; is style corpus also standard, or was it session-specific?
   - Suggestion: Clarify: "Check for style corpus at `tmp/STYLE_CORPUS.md` (if user provided)" or document this as a standard location if it's intended to be.
   - **Status**: FIXED — Clarified that style corpus location is conventional but optional.

4. **WebSearch and WebFetch tools in allowed list but never used**
   - Location: agent-core/skills/doc-writing/SKILL.md:4
   - Problem: `allowed-tools` includes `WebSearch` and `WebFetch` but the process never invokes them. The two README sessions didn't use web research.
   - Suggestion: Either remove these tools from allowed list (match actual validated pattern) or document when they should be used (e.g., "WebSearch for checking current external documentation standards" in exploration phase).
   - **Status**: FIXED — Removed WebSearch and WebFetch from allowed-tools (not part of validated pattern from two README sessions).

### Minor Issues

1. **Example uses quiet-explore reference**
   - Location: agent-core/skills/doc-writing/SKILL.md:143
   - Problem: Example shows "Delegate quiet-explore to catalog..." but if quiet-explore agent doesn't exist (see Major Issue 1), example won't match execution reality.
   - Note: Align example with process fix (either define agent or change to direct tool usage).
   - **Status**: FIXED — Updated example to show direct tool usage (Read, Glob, Grep) consistent with process changes.

2. **"Motivation-first" principle lacks negative example**
   - Location: agent-core/skills/doc-writing/SKILL.md:48-51
   - Problem: Principle shows good/bad contrast in prose, but no concrete before/after example from actual README rewrites.
   - Note: Could strengthen with actual opening sentence from old vs new README (validates the principle with evidence).
   - **Status**: FIXED — Added concrete example from agent-core README rewrite.

3. **Reader-test question count range (5-10) not justified**
   - Location: agent-core/skills/doc-writing/SKILL.md:76
   - Problem: Says "5-10 predicted reader questions" but both README sessions used ~9-10. Is 5 actually sufficient, or should range be 8-10?
   - Note: Minor precision issue. If pattern from sessions was consistently 9-10, state that. If 5 is acceptable for smaller docs, explain the variance.
   - **Status**: FIXED — Changed to "8-10 questions" reflecting actual session pattern (9 for parent README, 10 for agent-core README).

## Fixes Applied

- agent-core/skills/doc-writing/SKILL.md:28 — Changed quiet-explore delegation to direct tool usage (Read, Glob, Grep)
- agent-core/skills/doc-writing/SKILL.md:81 — Simplified Task delegation (removed undefined subagent_type)
- agent-core/skills/doc-writing/SKILL.md:32-35 — Clarified style corpus as optional conventional location
- agent-core/skills/doc-writing/SKILL.md:4 — Removed WebSearch, WebFetch from allowed-tools (not validated)
- agent-core/skills/doc-writing/SKILL.md:143 — Updated example to match direct tool usage pattern
- agent-core/skills/doc-writing/SKILL.md:48-51 — Added concrete before/after example from agent-core README
- agent-core/skills/doc-writing/SKILL.md:76 — Tightened reader-test question count to 8-10 (reflects actual pattern)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Skill follows project conventions | Partial | Frontmatter pattern inconsistent across skills (deferred), but structure matches |
| Process steps actionable | Satisfied | Each phase has clear actions (explore, write, reader-test, fix, vet) |
| Constraints are prohibitions | Satisfied | Lines 131-135 use clear "Do not" language |
| Reader-test implementation concrete | Satisfied | Line 81 provides exact Task delegation template |
| Example demonstrates full cycle | Satisfied | Lines 139-153 show all 5 phases |
| Description triggers match use cases | Satisfied | Line 3 covers actual invocation patterns |
| No aspirational content | Satisfied | Process validated across two README sessions, documented as-is |

**Gaps:** Frontmatter `name` field convention inconsistent (deferred for broader skill standardization).

---

## Positive Observations

- **Process extraction quality**: Successfully distilled a validated pattern (two README sessions) into reusable process without over-generalizing.
- **Constraints are concrete**: "Do not fabricate examples" and "Reader test is mandatory" are clear prohibitions, not vague guidance.
- **Structural principles well-articulated**: Motivation-first opener, audience-appropriate depth, structure for scanning — these are actionable writing rules.
- **Example is complete**: Shows all five phases end-to-end, making the skill immediately executable.
- **Tool boundaries clear**: Allowed-tools list was initially too broad but matched skill's read-only exploration needs once fixed.

## Recommendations

1. **Skill convention audit**: The `name` vs no-`name` frontmatter inconsistency suggests skills were created at different times with different conventions. Consider standardizing all skills to consistent frontmatter format (defer to future skill audit task).

2. **Style corpus as fragment**: If `tmp/STYLE_CORPUS.md` is intended as standard practice, document it in a fragment (`agent-core/fragments/style-corpus.md`) explaining when to create it and what to include. Currently it's implied convention from two sessions.

3. **Reader-test as standalone skill**: The reader-test pattern (spawn fresh agent, ask N questions, identify gaps) is generic and could apply beyond documentation (design reviews, plan reviews). Consider extracting if pattern recurs.
