# Deliverable Review: plugin-migration

**Date:** 2026-03-22
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - |
|------|------|---|---|
| Code | plugin/bin/bump-plugin-version.py | +34 | -0 |
| Code | plugin/bin/check-version-consistency.py | +63 | -0 |
| Code | plugin/hooks/sessionstart-health.sh | +79 | -2 |
| Code | plugin/hooks/stop-health-fallback.sh | +2 | -2 |
| Code | plugin/hooks/pretooluse-recipe-redirect.py | +0 | -7 |
| Agentic prose | plugin/skills/init/SKILL.md | +132 | -0 |
| Agentic prose | plugin/skills/update/SKILL.md | +136 | -0 |
| Agentic prose | plugin/fragments/claude-config-layout.md | +0 | -5 |
| Agentic prose | plugin/fragments/project-tooling.md | +0 | -3 |
| Agentic prose | plugin/fragments/sandbox-exemptions.md | +0 | -7 |
| Configuration | plugin/.claude-plugin/plugin.json | +5 | -0 |
| Configuration | plugin/hooks/hooks.json | +88 | -55 |
| Configuration | plugin/portable.just | +472 | -0 |
| Configuration | justfile | +9 | -346 |
| Configuration | plugin/justfile | +0 | -98 |
| Configuration | .edify.yaml | +4 | -0 |
| Configuration | .gitignore | +1 | -1 |
| Configuration | .cache/just-help.txt | +21 | -0 |
| Human docs | plugin/templates/CLAUDE.template.md | +12 | -12 |

**Totals:** 19 files, +1058 / -538, net +520

**Note:** Inventory script listed 23 files; 4 agentic prose files (inline/SKILL.md, runbook/SKILL.md, review-dispatch-template.md, tier3-planning-process.md) showed zero diff in submodule commit range — excluded as not modified by migration.

**Design conformance:** 11/13 outline In-scope items delivered. Two items explicitly deferred: directory rename (`plugin/` → `edify-plugin/`, "cosmetic, last step") and marketplace setup. Step 6.3 checkpoint confirms: "Proceed to Phase 7 (directory rename)."

## Critical Findings

**1.** sessionstart-health.sh:52-83 — **FR-5 staleness nag is vacuous**

Conformance, functional correctness. Step 3 (lines 52-76) unconditionally writes `PLUGIN_VERSION` to `.edify.yaml`, then step 4 (lines 79-83) reads the version back and compares. After a successful write, YAML_VERSION == PLUGIN_VERSION always. The staleness nag only fires when the write itself fails — not when fragments are actually stale (the common case).

Outline Component 3 (lines 128-129): "Setup hook reads plugin.json version, compares against .edify.yaml version. Mismatch → nag." The design intent: `.edify.yaml` records the version at which fragments were last *synced* (by `/edify:update`). The hook should compare, not overwrite.

Fix: read and compare *before* writing. Or separate fields (`synced_version` for staleness tracking vs `plugin_version` for provenance).

**2.** skills/update/SKILL.md:53 — **portable.just path wrong, sync silently skipped**

Conformance, functional correctness. Source path is `$CLAUDE_PLUGIN_ROOT/just/portable.just` but actual file location is `$CLAUDE_PLUGIN_ROOT/portable.just` (no `just/` subdirectory). The guard clause (line 55) catches "source does not exist" and reports "not yet available in this plugin version" — a misleading message when the file exists at a different path.

FR-4 requires `/edify:update` to sync `portable.just`. This path error defeats that requirement.

Fix: change source path to `$CLAUDE_PLUGIN_ROOT/portable.just`.

## Major Findings

**3.** hooks.json + sessionstart-health.sh — **No early-session fallback for setup hook**

Functional completeness. Outline Component 2 specifies "SessionStart, with UPS fallback via transcript scraping." Known issue #10373: SessionStart doesn't fire for new interactive sessions. The current fallback is `stop-health-fallback.sh` (Stop event), meaning setup (FR-5 nag, FR-10 version write, FR-11 CLI install) only runs at session end or after `/clear`/`/compact`.

The outline's UPS fallback was designed to run setup on first prompt submit when SessionStart was missed. No UPS hook for setup exists in hooks.json.

Impact: In the most common session type (new interactive), `EDIFY_PLUGIN_ROOT` is not exported, CLI is not installed, version is not written, and staleness nag doesn't run until session termination.

## Minor Findings

**Release recipe (4):**
- sessionstart-health.sh:22 — `EDIFY_VERSION="0.0.2"` hardcoded. `just release` bumps plugin.json and pyproject.toml but not this value. Manual step required each release.

**Pre-rename state (5, 6, 7):**
- sessionstart-health.sh:30 — Package name `edify` vs D-1 decision `edify`. Correct for current state (pyproject.toml is `edify`). Rename deferred with directory rename.
- check-version-consistency.py:11 — Hardcoded `plugin` path. Correct pre-rename; needs update with rename.
- portable.just:84,102,136 — Hardcoded `plugin/` and `./scripts/check_line_limits.sh` paths. Consumer projects post-rename need these updated.

**Skill allowed-tools (8):**
- init/SKILL.md:4, update/SKILL.md:4 — `Bash(python3:*)` and `Bash(find:*)` in allowed-tools are excess. `python3` is in settings.json deny list (overrides allowed-tools). `find` unused by any step.

**hooks.json consistency (9):**
- hooks.json:9,51,73,84 — Inconsistent `bash` prefix: `pretooluse-block-tmp.sh` invoked bare, `posttooluse-autoformat.sh`/`sessionstart-health.sh`/`stop-health-fallback.sh` use `bash $CLAUDE_PLUGIN_ROOT/...`. All scripts have shebangs; both patterns work.

**Robustness edge cases (10, 11):**
- sessionstart-health.sh:33-36 — pip fallback creates `$VENV_DIR/lib` with `--target` but no proper venv structure. Downstream code expecting `$VENV_DIR/bin/python` fails on pip path.
- sessionstart-health.sh:38 — Error "CLI install failed: uv not found" fires when both uv and pip missing. Should say "neither uv nor pip found."

**Template coverage (12):**
- CLAUDE.template.md — References 12/27 available fragments. By design (minimal starting point), but consumer projects starting from template lack pushback.md, no-confabulation.md, source-not-generated.md, code-removal.md, design-decisions.md, project-tooling.md, sandbox-exemptions.md, claude-config-layout.md. Init copies all fragments to `agents/rules/` but template doesn't `@`-reference them.

**Determinism (13):**
- init/SKILL.md:95-96 — SHA-256 computation method unspecified (could use `sha256sum` or `python3 hashlib`). Both allowed. Single prescribed method would reduce agent choice variance.

## Gap Analysis

| Outline Requirement | Status | Reference |
|---|---|---|
| FR-1: Plugin auto-discovery | ✓ Covered | plugin.json, hooks.json |
| FR-2: `just claude` wrapper | ✓ Covered | portable.just:115-117 |
| FR-3: `/edify:init` scaffolding | ✓ Covered | skills/init/SKILL.md |
| FR-4: `/edify:update` sync | ⚠ Partial | skills/update/SKILL.md (portable.just path wrong — Critical #2) |
| FR-5: Staleness nag | ✗ Vacuous | sessionstart-health.sh (write-before-compare — Critical #1) |
| FR-6: Portable justfile | ✓ Covered | portable.just |
| FR-7: Migration by removing symlinks | ✓ Covered | .claude/ dirs empty |
| FR-8: Plan-specific agent coexistence | ✓ Covered | step-6-3-checkpoint.md confirms |
| FR-9: Hooks in plugin, settings.json empty | ✓ Covered | hooks.json, settings.json verified |
| FR-10: SessionStart writes version | ✓ Covered | sessionstart-health.sh:41-77 |
| FR-11: SessionStart installs CLI | ✓ Covered | sessionstart-health.sh:22-39 |
| FR-12: Version consistency check + bump | ✓ Covered | check-version-consistency.py, bump-plugin-version.py, justfile release |
| NFR-1: Dev reload speed | ✓ Validated | `--plugin-dir` live loading |
| NFR-2: No token overhead increase | ✓ Validated | Architectural (same content, different delivery) |
| Directory rename | Deferred | Planned as Phase 7 |
| Marketplace setup | Deferred | Not yet executed |

## Summary

| Severity | Count |
|----------|-------|
| Critical | 2 |
| Major | 1 |
| Minor | 10 |

**Layer 1 sources:** `reports/deliverable-review-code.md`, `reports/deliverable-review-prose-config.md`
