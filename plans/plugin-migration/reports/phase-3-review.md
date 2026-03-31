# Runbook Review: Phase 3 — Migration Skills

**Artifact**: plans/plugin-migration/runbook-phase-3.md
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (2 steps)

## Summary

Phase 3 creates the `/edify:init` and `/edify:update` skills. Steps are well-structured with clear prerequisites, error conditions, and validation. Three issues found: the init skill description framed execution as open-ended conversation contradicting the outline's specified concrete actions (FR-3), a template target that already exists was marked "Create" instead of "Update," and an ambiguous path reference in Step 3.2. All three fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **Init skill framed as conversational inquiry instead of concrete execution**
   - Location: Step 3.1, Implementation item 1
   - Problem: Runbook said "Conversational, not predetermined recipe" and "discuss setup with user: What fragments to copy...How to rewrite..." — frames the skill as an open-ended consultation where the user decides what to do. The outline (FR-3, Component 4) specifies the skill executes concrete operations: copies fragments to `agents/rules/`, rewrites CLAUDE.md refs, scaffolds `agents/` structure (session.md, learnings.md, jobs.md), generates CLAUDE.md from template, writes `.edify.yaml`. The conversational framing contradicts the specified behavior and would produce a skill that asks rather than acts.
   - Fix: Replaced with concrete behavior list matching outline FR-3 and Component 4. Added "No submodule detection" design decision per outline line 142.
   - **Status**: FIXED

### Minor Issues

1. **Template target exists but step said "Create"**
   - Location: Step 3.1, Implementation item 2
   - Problem: `plugin/templates/CLAUDE.template.md` already exists (verified via Glob). Step instructed "Create" which would cause executor to overwrite without reading. The template needs updating (existing file uses `@plugin/fragments/` paths; step correctly specifies it should use `@agents/rules/` paths).
   - Fix: Changed "Create" to "Update", added "(file exists — needs ref rewrites)" note, and clarified what must change (the `@plugin/fragments/` → `@agents/rules/` rewrite).
   - **Status**: FIXED

2. **Step 3.1 missing `jobs.md` from `agents/` scaffold list**
   - Location: Step 3.1, Implementation item 1, agents/ structure list
   - Problem: Outline Component 4 line 138 specifies scaffolding "session.md, learnings.md, jobs.md". Runbook listed only "session.md, learnings.md".
   - Fix: Added `jobs.md` to the scaffold list.
   - **Status**: FIXED

3. **Step 3.2 ambiguous fragment path "plugin's `fragments/`"**
   - Location: Step 3.2, Implementation item 1, bullet 1
   - Problem: "plugin's `fragments/`" is ambiguous during bootstrap phase — the directory is still called `plugin/`. Executor might create a separate `fragments/` directory.
   - Fix: Replaced with explicit path: "plugin's fragments at `plugin/fragments/`".
   - **Status**: FIXED

## Fixes Applied

- Step 3.1 Implementation item 1 — Replaced conversational framing with concrete behavior list (copy, rewrite, scaffold, generate, write) per outline FR-3 + Component 4. Added `jobs.md` to scaffold list. Added no-submodule-detection constraint.
- Step 3.1 Implementation item 2 — Changed "Create" to "Update (file exists — needs ref rewrites)". Clarified the `@plugin/fragments/` → `@agents/rules/` rewrite requirement.
- Step 3.2 Implementation item 1 bullet 1 — Replaced "plugin's `fragments/`" with explicit `plugin/fragments/` path.

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
