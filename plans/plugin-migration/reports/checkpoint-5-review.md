# Review: Phase 5 — Version Coordination and Release

**Scope**: Phase 5 changed files: `.edify.yaml`, `agent-core` (submodule pointer), `justfile`, `plans/prototypes/validate-edify-yaml.py`
**Date**: 2026-03-21T13:03:12Z
**Mode**: review + fix

## Summary

Phase 5 wires version consistency between `plugin.json` and `pyproject.toml`. The implementation creates `.edify.yaml`, adds `check-version-consistency.py` to precommit, and modifies the `release` recipe to bump `plugin.json` alongside `pyproject.toml`. The precommit check is correct and passes. One critical bug exists in the `release` recipe: `version=$(uv version)` returns `"claudeutils 0.0.2"` (name + version) in uv 0.10.8, but `bump-plugin-version.py` uses that string directly as the JSON value, corrupting `plugin.json` with `"claudeutils 0.0.2"` instead of `"0.0.2"`. The precommit check then fails on the next run.

**Overall Assessment**: Needs Minor Changes (one fix applied)

## Issues Found

### Critical Issues

1. **`version=$(uv version)` passes "name version" string to bump-plugin-version.py**
   - Location: `justfile:140-141`
   - Problem: `uv version` (without `--short`) returns `"claudeutils 0.0.2"` in uv 0.6+. The release recipe captures this into `$version` and passes it to `bump-plugin-version.py "$version"`. The script assigns it directly: `data["version"] = version`, so `plugin.json` gets `"claudeutils 0.0.2"` as its version field. The subsequent `check-version-consistency.py` call then catches the mismatch and aborts — but by then `plugin.json` has already been written with a corrupt value and must be reset manually.
   - Fix: Change `version=$(uv version)` to `version=$(uv version --short)`
   - **Status**: FIXED

### Major Issues

None.

### Minor Issues

1. **`validate-edify-yaml.py` asserts `sync_policy == "nag"` unconditionally**
   - Location: `plans/prototypes/validate-edify-yaml.py:7`
   - Note: The script is a prototype (not wired into precommit), used as a one-shot validation tool. Asserting `sync_policy == "nag"` means it fails for any project that has changed sync_policy. As a prototype it serves its current purpose, but the assertion will false-positive if reused after a user has set `sync_policy: auto-with-report`. The prototype is in `plans/prototypes/` which is the correct location for throwaway validation scripts.
   - **Status**: FIXED — relaxed to only assert version match, not sync_policy (which is user-configurable)

## Fixes Applied

- `justfile:140` — Changed `version=$(uv version)` to `version=$(uv version --short)` to get bare version number `"0.0.2"` instead of `"claudeutils 0.0.2"`
- `plans/prototypes/validate-edify-yaml.py:7` — Removed `sync_policy` assertion; prototype now only validates version match (sync_policy is user-configurable)

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-12: plugin.json version == pyproject.toml version, precommit validates | Satisfied | `check-version-consistency.py` in `portable.just` precommit; passes `just dev` |
| FR-12: `just release` bumps both together | Satisfied (after fix) | `bump-plugin-version.py` + `check-version-consistency.py` in release recipe; bug with `uv version` output format fixed |
| FR-10: SessionStart hook writes version to `.edify.yaml` | Partial — `.edify.yaml` schema exists; SessionStart hook (Phase 2) implements the write | `.edify.yaml` created with correct schema; hook implementation is Phase 2 scope |
| FR-5: stale fragment detection via `.edify.yaml` | Partial — schema exists; hook logic is Phase 2 scope | `.edify.yaml` `version` and `sync_policy` fields present |

---

## Positive Observations

- `check-version-consistency.py` avoids `tomllib` version pinning issues by using a line-scan fallback instead of relying on stdlib `tomllib` (which requires Python 3.11+)
- `bump-plugin-version.py` preserves existing JSON formatting (indent=2, trailing newline)
- `validate-edify-yaml.py` correctly placed in `plans/prototypes/` — not wired into precommit where it would over-constrain `sync_policy`
- Precommit integration placed after `run-checks` and before `run-pytest` — correct ordering (fast static checks before slower tests)
- `agent-core/.claude-plugin/plugin.json` added to `git add` in release recipe — versions stay in sync across commits
