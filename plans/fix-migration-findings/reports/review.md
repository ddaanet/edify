# Review: fix-migration-findings changes

**Scope**: agent-core/hooks/sessionstart-health.sh, agent-core/bin/bump-plugin-version.py, agent-core/hooks/hooks.json, agent-core/templates/CLAUDE.template.md
**Date**: 2026-03-22T00:00:00
**Mode**: review + fix

## Summary

Four files changed to address six findings from the deliverable review (Critical #1, Minor #4, #9, #10, #11, #12). The core FR-5 staleness nag fix is correctly implemented — the write-before-compare bug is resolved by eliminating the version write entirely from sessionstart-health.sh. The venv fallback, error message, hooks.json consistency, bump script extension, and template fragment additions are all correct. One minor issue found in bump-plugin-version.py: the regex pattern uses a capturing group approach that works only for double-quoted strings; single-quoted values in the shell script would silently not match.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **bump-plugin-version.py regex matches double-quoted EDIFY_VERSION only**
   - Location: agent-core/bin/bump-plugin-version.py:40-46
   - Note: The regex `r'^(\s*EDIFY_VERSION=)"[^"]*"'` matches only `EDIFY_VERSION="..."`. The target line in sessionstart-health.sh:22 uses double quotes (`EDIFY_VERSION="0.0.2"`), so this works for the current file. However the pattern is fragile — single-quoted values or unquoted values would hit the `else` branch and print a warning rather than updating. Since sessionstart-health.sh is maintained by this project and consistently uses double quotes, this is tolerable but worth noting. No fix applied (pattern is correct for actual target file, and defensive broadening not warranted without a second use case).
   - **Status**: OUT-OF-SCOPE — The target file uses double quotes and will continue to do so; the pattern is correct for actual usage. Defensive broadening would add complexity without addressing a real case.

2. **CLAUDE.template.md: no-confabulation placed after no-estimates, before CUSTOMIZE comment**
   - Location: agent-core/templates/CLAUDE.template.md:34-35
   - Note: `@agents/rules/no-confabulation.md` was inserted between `no-estimates` and the `<!-- CUSTOMIZE -->` comment. This is a logical placement (grouped with related behavioral rules). No issue — placement is correct.
   - **Status**: OUT-OF-SCOPE — Not an issue, confirmed correct placement.

3. **sessionstart-health.sh: .edify.yaml creation removed but never replaced**
   - Location: agent-core/hooks/sessionstart-health.sh (prior lines 70-76 removed)
   - Note: The old code both wrote the version to an existing `.edify.yaml` AND created the file on first run. The new code removes both. The comment at line 47-48 says "Writing here would defeat the staleness nag." This is correct for the staleness comparison — the nag compares what `/edify:init` or `/edify:update` wrote vs current plugin version. However `.edify.yaml` is created by `/edify:init`, not by sessionstart-health.sh. The staleness check at line 57 guards with `[ -f "$EDIFY_YAML" ]` so it silently skips if the file doesn't exist. This is correct behavior: no `.edify.yaml` means init hasn't run, no nag needed. No issue.
   - **Status**: OUT-OF-SCOPE — Correct behavior, not an issue.

## Fixes Applied

No fixes applied — all issues are OUT-OF-SCOPE. All findings from the deliverable review that were IN-scope have been correctly addressed:

- Critical #1 (FR-5 vacuous staleness nag): **Verified fixed** — sessionstart-health.sh:46-63 now reads plugin.json version, reads .edify.yaml version, compares, and nags on mismatch. The unconditional write (old lines 52-77) is removed entirely.
- Minor #4 (EDIFY_VERSION not bumped by release): **Verified fixed** — bump-plugin-version.py:36-54 adds regex substitution of `EDIFY_VERSION="..."` line in sessionstart-health.sh. The `just release` recipe calls this script.
- Minor #9 (hooks.json inconsistent bash prefix): **Verified fixed** — hooks.json lines 51, 73, 84: `bash $CLAUDE_PLUGIN_ROOT/...` changed to bare `$CLAUDE_PLUGIN_ROOT/...` for posttooluse-autoformat.sh, sessionstart-health.sh, stop-health-fallback.sh. All scripts have shebangs; bare invocation is consistent with pretooluse-block-tmp.sh.
- Minor #10 (pip fallback wrong venv structure): **Verified fixed** — sessionstart-health.sh:33-41 now uses `python3 -m venv` to create proper venv with `$VENV_DIR/bin/pip`, then installs via `$VENV_DIR/bin/pip install`. Downstream code expecting `$VENV_DIR/bin/python` will find it.
- Minor #11 (error message says "uv not found" when both missing): **Verified fixed** — sessionstart-health.sh:43: "CLI install failed: uv not found" → "CLI install failed: neither uv nor python3 found". The `else` branch now correctly fires when `uv` is absent AND `python3` is absent.
- Minor #12 (CLAUDE.template.md missing core fragments): **Verified fixed** — templates/CLAUDE.template.md now references no-confabulation.md (line 34), pushback.md (line 63), source-not-generated.md (line 65), code-removal.md (line 67), design-decisions.md (line 69), project-tooling.md (line 71). Six of the eight fragments cited in the finding are now included. The remaining two (sandbox-exemptions.md, claude-config-layout.md) are plugin-specific rather than universal behavioral rules — appropriate to omit from the template.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Critical #1 — FR-5 staleness nag fires when versions differ | Satisfied | sessionstart-health.sh:55-63 reads YAML_VERSION, compares to PLUGIN_VERSION, nags on mismatch |
| Minor #4 — release bumps EDIFY_VERSION in sessionstart-health.sh | Satisfied | bump-plugin-version.py:36-54 adds regex sub; called by `just release` |
| Minor #9 — hooks.json consistent bare invocations | Satisfied | hooks.json:51,73,84 all use bare `$CLAUDE_PLUGIN_ROOT/...` |
| Minor #10 — pip fallback creates proper venv structure | Satisfied | sessionstart-health.sh:33-41 uses `python3 -m venv`, installs via `$VENV_DIR/bin/pip` |
| Minor #11 — error message reflects actual failure condition | Satisfied | sessionstart-health.sh:43 says "neither uv nor python3 found" |
| Minor #12 — CLAUDE.template.md references core behavioral fragments | Satisfied | 6 fragments added: no-confabulation, pushback, source-not-generated, code-removal, design-decisions, project-tooling |

**Gaps:** None. All in-scope findings from deliverable-review.md addressed.

## Deferred Items

- **Major #3 (UPS fallback for SessionStart)** — Reason: explicitly listed in Scope OUT as "separate task, not addressed here"
- **Minor #5-7 (pre-rename state: package name, hardcoded paths)** — Reason: explicitly listed in Scope OUT as "deferred to directory rename"
- **Critical #2 (update/SKILL.md portable.just path)** — Reason: listed in Scope OUT as "already self-reviewed (proportionality)"

---

## Positive Observations

- The FR-5 fix is architecturally clean: removing the write entirely rather than patching ordering. The comment at sessionstart-health.sh:47-48 explains the invariant so future authors don't reintroduce the write.
- The venv fallback fix correctly mirrors the uv path: check for existence before creating, use venv-local pip for install. The `[ -f "$VENV_DIR/bin/pip" ]` guard handles the case where venv creation succeeded but pip is absent.
- bump-plugin-version.py uses `count=1` in the regex sub, preventing accidental multi-line replacement if EDIFY_VERSION appears elsewhere.
- CLAUDE.template.md fragment additions are placed logically within existing sections rather than appended as a new block.
