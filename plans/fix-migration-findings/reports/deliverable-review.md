# Deliverable Review: fix-migration-findings

**Date:** 2026-03-22
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

Scoped to agent-core submodule diff `4399a1d8..9741e550` (commit `9741e55 🐛 Fix 9 deliverable review findings`).

| Type | File | + | - |
|------|------|---|---|
| Code | agent-core/bin/bump-plugin-version.py | +28 | -2 |
| Code | agent-core/hooks/sessionstart-health.sh | +17 | -38 |
| Configuration | agent-core/hooks/hooks.json | +3 | -3 |
| Agentic prose | agent-core/skills/init/SKILL.md | +2 | -2 |
| Agentic prose | agent-core/skills/update/SKILL.md | +2 | -2 |
| Human docs | agent-core/templates/CLAUDE.template.md | +12 | -0 |

**Totals:** 6 files, +64 / -47, net +17

**Design conformance:** The design baseline is `plans/plugin-migration/reports/deliverable-review.md` (parent plan's deliverable review). The classification (`plans/fix-migration-findings/classification.md`) scoped 9 findings as Group A (inline). All 9 are addressed.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

**Corrector review coverage (1):**
- `plans/fix-migration-findings/reports/review.md` — The corrector review verified 6 of 9 Group A findings (Critical #1, Minor #4, #9, #10, #11, #12). Three findings were not verified: Critical #2 (update/SKILL.md path fix, classified as "self-reviewed"), Minor #8 (excess allowed-tools), Minor #13 (sha256sum prescription). All three are correctly fixed (verified by this review), but the corrector's coverage claim ("All in-scope findings addressed") overstates its verification scope.

**Robustness — bump exit code (2):**
- `agent-core/bin/bump-plugin-version.py:50-53` — When EDIFY_VERSION pattern is not found in sessionstart-health.sh, the script prints a warning to stderr but exits 0. `just release` won't fail. Consequence: release proceeds with stale EDIFY_VERSION, causing CLI install to fetch an older version at SessionStart. The staleness nag (FR-5) is unaffected (compares plugin.json, not EDIFY_VERSION). Tolerable given single-maintainer context.

**Robustness — silent pip absence (3):**
- `agent-core/hooks/sessionstart-health.sh:38-41` — If `python3 -m venv` succeeds but `pip` is absent in the venv (no `ensurepip`), the `[ -f "$VENV_DIR/bin/pip" ]` guard silently skips install with no warning. The CLI is simply not installed with no diagnostic. Rare edge case (`ensurepip` is present on most systems).

## Gap Analysis

| Classification Finding | Status | Evidence |
|---|---|---|
| Critical #1 — FR-5 staleness nag vacuous | ✓ Fixed | sessionstart-health.sh:46-63 — write removed, read-and-compare only |
| Critical #2 — portable.just path wrong | ✓ Fixed | update/SKILL.md:53 — `$CLAUDE_PLUGIN_ROOT/portable.just` |
| Minor #4 — EDIFY_VERSION not bumped by release | ✓ Fixed | bump-plugin-version.py:36-54 — regex sub with `count=1` |
| Minor #8 — Excess allowed-tools | ✓ Fixed | init/SKILL.md:4, update/SKILL.md:4 — `Bash(python3:*)`, `Bash(find:*)` removed |
| Minor #9 — Inconsistent bash prefix | ✓ Fixed | hooks.json:51,73,84 — all bare invocation |
| Minor #10 — pip fallback wrong venv structure | ✓ Fixed | sessionstart-health.sh:33-41 — `python3 -m venv` + `$VENV_DIR/bin/pip` |
| Minor #11 — Error message inaccurate | ✓ Fixed | sessionstart-health.sh:43 — "neither uv nor python3 found" |
| Minor #12 — Template missing core fragments | ✓ Fixed | CLAUDE.template.md:37,65,67,69,71,73 — 6 fragments added |
| Minor #13 — SHA-256 method unspecified | ✓ Fixed | init/SKILL.md:95 — prescribes `sha256sum` |
| Major #3 — UPS fallback (Group B) | Out of scope | Separate task: `health-check-ups-fallback` plan |
| Minor #5-7 — Pre-rename state (Deferred) | Out of scope | Deferred to directory rename |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 3 |
