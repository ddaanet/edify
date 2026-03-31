# Review: Phase 3 — Migration Skills (/edify:init, /edify:update)

**Scope**: plugin/skills/init/SKILL.md, plugin/skills/update/SKILL.md, plugin/templates/CLAUDE.template.md
**Date**: 2026-03-21
**Mode**: review + fix

## Summary

Phase 3 creates two agentic skill prose artifacts (`/edify:init` and `/edify:update`) plus a `CLAUDE.template.md` for new consumer projects. The skills implement the conflict-detection-via-synced-hashes design from outline Component 4. The core logic is correct and well-structured, with clear separation of concerns between init (scaffold) and update (sync). Two fixable issues found: the init skill's `allowed-tools` is missing `python3` and `sha256sum` required for SHA-256 hash computation in Step 6, and the update skill has no guard against a missing `portable.just` source file (which won't exist until Phase 4).

**Overall Assessment**: Ready (all issues fixed)

## Issues Found

### Critical Issues

1. **Init skill missing allowed-tools for hash computation**
   - Location: plugin/skills/init/SKILL.md, line 4
   - Problem: Step 6 requires computing SHA-256 hashes for each copied fragment to populate `synced_hashes`. The `allowed-tools` frontmatter includes `Bash(cp:*)` and `Bash(find:*)` but omits `Bash(python3:*)` and `Bash(sha256sum:*)`. Without these, the agent cannot compute hashes and will either skip the hash population step (leaving `.edify.yaml` with `synced_hashes: {}`) or fail with a permission error.
   - Fix: Add `Bash(python3:*)` and `Bash(sha256sum:*)` to `allowed-tools` — matching update skill's frontmatter which already has both.
   - **Status**: FIXED

### Major Issues

1. **Update skill does not guard against missing portable.just source**
   - Location: plugin/skills/update/SKILL.md, Step 3 and Step 4
   - Problem: Step 3 lists `$CLAUDE_PLUGIN_ROOT/just/portable.just` as a sync target. Phase 4 creates this file — it does not exist yet. If `/edify:update` runs before Phase 4, the agent tries to compute a SHA-256 hash of a non-existent source file. The four-way classification in Step 4 covers missing *destination* files (New case) but not missing *source* files. The agent will either error out or produce undefined behavior when the source doesn't exist.
   - Fix: Add a guard at the start of Step 3's portable justfile handling: if source does not exist, skip that sync target and note it in the summary as "not yet available".
   - **Status**: FIXED

### Minor Issues

1. **Init skill Step 6 two-write sequence is ambiguous**
   - Location: plugin/skills/init/SKILL.md, lines 89-112
   - Note: Step 6 says "create `.edify.yaml`" first with `synced_hashes: {}`, then says "After initial creation, compute content hashes... and populate the `synced_hashes` map." This implies the agent writes `.edify.yaml` twice — once with empty hashes, then again with computed hashes. The prose doesn't say to update the existing file; it says to "populate" which an agent may interpret as a second write or as populating before writing. This ambiguity could cause the idempotency guard (first check "if `.edify.yaml` does not exist") to fire correctly the first time but then the second write would be updating an existing file — which would bypass the idempotency check. Clarify that the two-phase creation is a single write: compute hashes first, then write the complete `.edify.yaml` in one operation.
   - **Status**: FIXED

## Fixes Applied

- `plugin/skills/init/SKILL.md:4` — Added `Bash(python3:*)` and `Bash(sha256sum:*)` to `allowed-tools` (hash computation in Step 6 requires these)
- `plugin/skills/update/SKILL.md` — Added guard at Step 3 portable justfile section: skip sync target if source file does not exist, report as unavailable in summary
- `plugin/skills/init/SKILL.md:89-112` — Clarified Step 6 two-phase sequence: compute hashes first, then write complete `.edify.yaml` in a single operation

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-3: /edify:init scaffolds CLAUDE.md + fragments (idempotent) | Satisfied | init/SKILL.md Steps 1-7 cover fragments, CLAUDE.md (both cases), agents/ scaffold, .edify.yaml |
| FR-4: /edify:update syncs fragments + portable.just when plugin version changes | Satisfied | update/SKILL.md Steps 1-6 cover per-file sync with conflict detection, version update |
| D-6: .edify.yaml holds plugin version + sync policy | Satisfied | Both skills read/write .edify.yaml with version + sync_policy fields |
| Conflict policy (outline Component 4) | Satisfied | Four-case classification (New/Safe/Conflict/No-hash) matches spec exactly |
| Idempotency | Satisfied | Every init step guards with existence check before acting |

---

## Positive Observations

- Conflict detection via `synced_hashes` correctly distinguishes "user edited" from "plugin updated" — comparing against last-synced hash, not current plugin hash, prevents false conflicts on routine updates.
- The `--force` flag is scoped to all conflicting files (v1 per design) with clear user guidance to review the conflict list first.
- Step separation is clean: init owns scaffolding, update owns sync. No overlap.
- Summary output format in both skills is concrete and enumerated — useful for human review after automated execution.
- Prerequisite check in update skill (agents/rules/ must exist) fails fast with actionable error.
- Case A / Case B CLAUDE.md handling correctly handles both `@plugin/fragments/` and `@edify-plugin/fragments/` rewrite targets.
