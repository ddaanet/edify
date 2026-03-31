# Code Deliverable Review

## File: plugin/bin/bump-plugin-version.py

### Findings

- [Minor] :10 — robustness: No version format validation. Any string accepted (e.g., empty string, non-semver). Low risk since callers (`just release`) provide validated input from `uv version --short`.
- [Minor] :15 — modularity: Path resolution via `Path(__file__).parent.parent` couples the script to its directory position within `plugin/`. Correct for current layout but fragile if script moves. Acceptable given the mechanical nature of the script.

### Assessment

Clean, focused script. Correctly implements the plugin.json half of FR-12 (bump). Preserves JSON formatting (indent=2, trailing newline). No functional issues.

---

## File: plugin/bin/check-version-consistency.py

### Findings

- [Minor] :10 — robustness: `Path(__file__).parent.parent.parent` assumes the script lives at `<repo>/plugin/bin/`. Matches current layout; fragile on restructuring. Acceptable given project conventions.
- [Minor] :39 — robustness: TOML parsing via line scan handles `version = "X.Y.Z"` in `[project]` but would fail on valid TOML like `version="X.Y.Z"` (no spaces) — the `partition("=")` handles this, but `stripped.startswith("version")` also matches `version_suffix` or similar keys. Risk is negligible in practice since `[project]` section has a well-defined schema, but a more precise match (e.g., `re.match(r'version\s*=', stripped)`) would be safer.
- [Minor] :56 — idempotency: Provides actionable guidance ("Run: just release") on mismatch. Good UX.

### Assessment

Correct implementation of FR-12 precommit validation. The TOML line-scan approach avoids a `tomllib` dependency (stdlib since 3.11, but this project requires 3.14 per pyproject.toml — `tomllib` is actually available). The line-scan is defensible as a simpler approach for extracting a single field. No functional issues.

---

## File: plugin/hooks/sessionstart-health.sh

### Findings

- [Critical] :52-83 — functional correctness (FR-5 vacuity): Step 3 (lines 52-76) unconditionally writes the current `PLUGIN_VERSION` to `.edify.yaml`, then step 4 (lines 79-83) reads it back and compares against the same `PLUGIN_VERSION`. Unless the write fails, the values always match, making the staleness nag dead code. The outline specifies (Component 3, lines 128-129): "Setup hook reads `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json` version, compares against `.edify.yaml` version. Mismatch → nag." The design intent is that `.edify.yaml` records the version at which fragments were last *synced* (by `/edify:update`), not the current plugin version. The version write (FR-10, provenance) and the version comparison (FR-5, staleness) serve different purposes but the implementation conflates them — writing before comparing destroys the signal. Fix: read and compare *before* writing, or write a separate field (e.g., `plugin_version` for provenance vs `synced_version` for staleness tracking).
- [Major] :30,35 — conformance (D-1): Package installed is `claudeutils==$EDIFY_VERSION` but D-1 states the Python package name is `edify`. The pyproject.toml still shows `name = "claudeutils"` so this is currently correct at runtime, but it diverges from the naming decision. If the rename has been deferred, this should be documented; if it hasn't, the package name should be `edify`.
- [Minor] :33-36 — robustness: The `pip` fallback installs to `$VENV_DIR/lib` with `--target` but doesn't create a proper venv structure. `$VENV_DIR/bin/python` will not exist for the pip path, so any downstream code expecting a standard venv layout (e.g., FR-11 validation: `$CLAUDE_PLUGIN_ROOT/.venv/bin/edify --version`) will fail in the pip fallback scenario.
- [Minor] :38 — error signaling: Error message "CLI install failed: uv not found" fires when *both* uv and pip are missing. Slightly misleading — could say "neither uv nor pip found."
- [Minor] :45 — robustness: `python3 -c "import json; print(json.load(open('$PLUGIN_JSON'))['version'])"` uses shell variable interpolation inside Python code. If the path contains single quotes or special characters, this breaks. Low risk since plugin root paths are typically clean.
- [Minor] :80 — robustness: The regex for reading `.edify.yaml` version is complex and handles both quoted and unquoted values, but the *write* path on line 64 always writes `version: "X.Y.Z"` (double-quoted) while the create path on line 74 writes `version: "$PLUGIN_VERSION"` (also double-quoted, though via heredoc substitution). Consistent, but the reader regex complexity is disproportionate.
- [Minor] :97 — robustness: `"${CLAUDE_PLUGIN_ROOT:-}/bin/learning-ages.py"` resolves to `/bin/learning-ages.py` when not running as plugin. The `|| echo "⚠️..."` fallback catches the error, but the invocation is noisy (attempts to run a nonexistent path). Acceptable since stderr is suppressed via `2>/dev/null`.

### Assessment

The setup section implements FR-10 (version provenance) and FR-11 (CLI venv install) correctly. FR-5 (staleness nag) is functionally vacuous due to the write-before-compare ordering — this is a Critical finding because the requirement is unimplemented in effect. The health check section (dirty tree, learnings, stale worktrees) is unchanged and correct. The `pip` fallback is structurally incomplete but reasonable as a best-effort path.

---

## File: plugin/hooks/stop-health-fallback.sh

### Findings

- [Minor] :4 — robustness: `TMPDIR="${TMPDIR:-/tmp}"` provides a fallback. Correct defensive coding for the Stop hook context where `TMPDIR` may not be set.

### Assessment

Clean, no issues. The unbound variable fix (adding `TMPDIR` default on line 4, replacing bare `$TMPDIR` references) is correct. Health check logic mirrors `sessionstart-health.sh` without the setup section, as expected (Stop hook provides fallback when SessionStart was bypassed). No conformance issues with outline Component 2.

---

## File: plugin/hooks/pretooluse-recipe-redirect.py

### Findings

- [Minor] :44 — conformance: The task description claims "+0, -7 lines" of changes, but the file shows no diff against main. No migration-specific modifications found. If path fixes were intended (outline Component 2: "Audit `$CLAUDE_PROJECT_DIR` usage"), no such changes are present in the file. The script uses `Path(path)` for local file validation and reads `$CLAUDE_PROJECT_DIR` only via the hook input JSON, not via environment — so no path fix was needed.

### Assessment

The file has no migration-related changes. It correctly uses `hook_input` JSON for command extraction and `Path()` for local filesystem checks. No `$CLAUDE_PROJECT_DIR` environment variable usage, so the Component 2 audit finding is "no change needed" — which is the correct outcome. The claimed line-count delta appears to be an error in the review scope description.

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 1 |
| Major | 1 |
| Minor | 10 |

**Critical finding:** FR-5 (staleness nag) is vacuous in `sessionstart-health.sh` — the version write on lines 52-76 destroys the staleness signal before the comparison on lines 79-83. The requirement is effectively unimplemented.

**Major finding:** Package name `claudeutils` in the install command diverges from D-1's stated naming (`edify`). This needs clarification — either the rename is deferred (document it) or the package name should be updated.

**Overall:** Four of five files are functionally correct. `sessionstart-health.sh` has one Critical defect (FR-5 vacuity) that requires a logic reorder or field separation to fix. The remaining findings are minor robustness and style observations.
