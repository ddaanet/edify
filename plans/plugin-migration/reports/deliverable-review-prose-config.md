# Prose + Config Deliverable Review

## File: plugin/skills/init/SKILL.md

### Findings

- [Minor] :4 — excess: `Bash(find:*)` in allowed-tools is unnecessary. The skill uses Glob for file discovery (Step 2 says "List all `.md` files"), and no step calls `find`. Dead permission.
- [Minor] :4 — excess: `Bash(python3:*)` in allowed-tools grants broad Python execution. Only used for SHA-256 hash computation (Step 6). `Bash(sha256sum:*)` is already listed and sufficient for that purpose.
- [Minor] :95-96 — determinism: Step 6 says "Compute SHA-256 hashes" but doesn't specify the tool. Could use `sha256sum` (allowed) or `python3 -c hashlib...` (also allowed). A single prescribed method would reduce agent choice variance.
- [Minor] :78-79 — completeness: Step 5 Case A rewrites `@plugin/fragments/` and `@edify-plugin/fragments/` refs but does not mention `@agents/rules/` → `@agents/rules/` (no-op). If a project already ran init once and has `@agents/rules/` refs, re-running is correctly a no-op. Behavior is correct; documenting the no-op case would improve clarity.

### Assessment

Well-structured, idempotent skill. Steps are ordered correctly (read version, inventory, scaffold, copy, CLAUDE.md, write yaml, summary). Hash computation placement is sound -- only hashes copied files, not skipped ones. FR-3 conformance is complete. The `$CLAUDE_PLUGIN_ROOT` env var usage is correct for plugin context. Minor allowed-tools excess.

---

## File: plugin/skills/update/SKILL.md

### Findings

- [Major] :53 — functional correctness: Source path for portable.just is `$CLAUDE_PLUGIN_ROOT/just/portable.just` but the actual file location is `$CLAUDE_PLUGIN_ROOT/portable.just` (no `just/` subdirectory). Agent executing this skill will fail to find the source file, skipping justfile sync entirely.
- [Minor] :4 — excess: Same `Bash(find:*)` and `Bash(python3:*)` excess as init skill.
- [Minor] :12 — accuracy: "In dev mode (submodule), fragments are read directly via `@plugin/fragments/` references -- update is a no-op." This is informational guidance, not enforced. No guard prevents running update in dev mode. Low risk since dev mode projects won't have `agents/rules/` unless they also ran init.

### Assessment

FR-4 conformance is mostly complete: conflict detection algorithm matches the outline (synced_hashes comparison, four categories, --force behavior). The portable.just path error is the sole Major finding -- it would silently skip justfile sync (the guard on line 55 catches "source does not exist" and notes it, but the note misleads about the cause). All other sync logic is correct.

---

## File: plugin/fragments/claude-config-layout.md

### Findings

- No findings. Removal of the "Symlinks in .claude/" subsection (5 lines) is correct per outline Component 8. Remaining content about hook configuration, agent configuration, and bash working directory is unaffected and still accurate.

### Assessment

Clean removal. No stale references to symlinks remain.

---

## File: plugin/fragments/project-tooling.md

### Findings

- No findings. Removed `sync-to-parent` recipe reference and the `ln` anti-pattern mention (3 lines). Remaining content is accurate. The "Check" list no longer mentions symlink management.

### Assessment

Clean removal. No stale references remain.

---

## File: plugin/fragments/sandbox-exemptions.md

### Findings

- No findings. Removed the `just sync-to-parent` subsection (7 lines). Remaining subsections (prepare-runbook.py, Worktree Operations, Commands Requiring bypass) are unaffected.

### Assessment

Clean removal. No stale references remain.

---

## File: plugin/skills/inline/SKILL.md

### Findings

- No findings attributable to the plugin migration. File was not modified in this migration branch (confirmed via `git diff-tree`). The task description listed it as changed (+3 -6 lines) but the submodule commit range shows no changes to this file.

### Assessment

No migration-related changes to review. File is pre-existing and outside migration scope.

---

## File: plugin/skills/inline/references/review-dispatch-template.md

### Findings

- No findings attributable to the plugin migration. File was not modified in this migration branch.

### Assessment

No migration-related changes to review.

---

## File: plugin/skills/runbook/SKILL.md

### Findings

- No findings attributable to the plugin migration. File was not modified in this migration branch.

### Assessment

No migration-related changes to review.

---

## File: plugin/skills/runbook/references/tier3-planning-process.md

### Findings

- No findings attributable to the plugin migration. File was not modified in this migration branch.

### Assessment

No migration-related changes to review.

---

## File: plugin/.claude-plugin/plugin.json

### Findings

- No findings. Name is `edify` (D-1), version is `0.0.2` (matches `pyproject.toml`), description is present. Wrapper format per D-4 is handled by hooks.json, not plugin.json. FR-1 and FR-12 conformance verified.

### Assessment

Minimal correct manifest. Version consistency with pyproject.toml confirmed (`0.0.2` == `0.0.2`).

---

## File: plugin/hooks/hooks.json

### Findings

- [Minor] :9 — consistency: `pretooluse-block-tmp.sh` invoked without `bash` prefix (relies on shebang + execute permission), while `posttooluse-autoformat.sh` (line 51), `sessionstart-health.sh` (line 73), and `stop-health-fallback.sh` (line 84) use `bash $CLAUDE_PLUGIN_ROOT/...` prefix. All scripts have shebangs and execute permissions, so both patterns work. Inconsistent convention.
- [Minor] :65 — vacuity: UserPromptSubmit entry has no `matcher` field. Per claude-config-layout.md, UPS hooks have no matcher support (all filtering is script-internal). The omission is correct behavior, but the entry structure differs from all other event types which include `matcher`. This is inherent to the UPS event type, not a defect.

### Assessment

FR-9 conformance verified: all 8 surviving hooks migrated (pretooluse-symlink-redirect.sh correctly deleted). Wrapper format `{"hooks": {...}}` matches D-4. Hook commands use `$CLAUDE_PLUGIN_ROOT` correctly. The `python3` prefix inconsistency from Phase 2 corrector was fixed (recipe-redirect.py and shortcuts.py no longer have `python3` prefix). settings.json hooks section confirmed empty.

---

## File: plugin/portable.just

### Findings

- [Minor] :84 — robustness: `git ls-files -z src/ tests/ plugin/hooks/ plugin/bin/` in test sentinel hash computation hardcodes `plugin/` paths. In consumer projects (post-rename to `edify-plugin/`), these paths won't exist, making the sentinel hash exclude hook/bin changes. Low impact: sentinel is a speed optimization; worst case is unnecessary test reruns, not missed tests.
- [Minor] :102 — robustness: `run-line-limits` calls `./scripts/check_line_limits.sh` with a relative path. Consumer projects may not have this script. Would fail silently or noisily depending on `set -e`. The precommit recipe calls this (line 139), so consumer projects using `just precommit` from portable.just would need this script.
- [Minor] :136 — completeness: `precommit` recipe includes `report "version consistency" python3 plugin/bin/check-version-consistency.py` with hardcoded `plugin/` path. Same rename concern as test sentinel.

### Assessment

FR-6 conformance: full opinionated recipe stack present (`claude`, `claude0`, `precommit`, `precommit-base`, `test`, `format`, `lint`, `red-lint`, `check`, `wt-*`). Matches D-5 specification. The `bash_prolog` is self-contained as documented. `wt-*` recipes are manual fallbacks per D-5. Variable merge across import boundaries works (root justfile overrides `bash_prolog`). Hardcoded `plugin/` paths are pre-rename artifacts -- rename is out of scope per outline ("cosmetic, happens last").

---

## File: justfile

### Findings

- No findings. Clean import of `plugin/portable.just` (line 6). `set allow-duplicate-recipes` and `set allow-duplicate-variables` enable override per D-5. Project-specific recipes (`dev`, `setup`, `line-limits`, `green`, `release`) are preserved. The `bash_prolog` override (line 179+) correctly replaces portable.just's prolog with the project's version including trace support and styled output.

### Assessment

FR-6 conformance: root justfile imports portable module and adds project-specific recipes. Override mechanism works as designed.

---

## File: plugin/justfile

### Findings

- No findings. Reduced to stub (`help` + `precommit` that prints OK). The 98-line removal was the `sync-to-parent` recipe and related content, correctly deleted per outline Component 6.

### Assessment

Clean removal. Stub precommit allows `just precommit` to succeed within the submodule directory (useful for CI or standalone testing).

---

## File: .edify.yaml

### Findings

- No findings. Version `0.0.2` matches plugin.json and pyproject.toml. `sync_policy: nag` matches D-6 default. No `synced_hashes` section -- correct for dev mode where `/edify:init` was not run (fragments are read directly via `@plugin/fragments/` refs). FR-10 conformance verified (SessionStart hook writes version).

### Assessment

Correct for the edify-plugin's own project (dev mode).

---

## File: .gitignore

### Findings

- [Minor] :36 — conformance: `.claude/settings.json` is gitignored. Per outline, settings.json retains permissions, sandbox config, plansDirectory, attribution, enabledPlugins after hook removal. Gitignoring it means the cleaned settings.json (hooks removed) won't be tracked. This appears to be a pre-existing pattern (settings.json was previously gitignored in this project) rather than a migration change.

### Assessment

The +1 -1 change is not visible in the current file state (likely a whitespace or reorder). No migration-specific issues.

---

## File: .cache/just-help.txt

### Findings

- No findings. Cached output of `just --list` reflecting the current recipe set. Informational artifact.

### Assessment

Matches the actual recipe list from `just --list --unsorted`.

---

## File: plugin/templates/CLAUDE.template.md

### Findings

- [Minor] :1 — completeness: Template has `# Agent Instructions` header but the project's own CLAUDE.md has additional content not in the template (Core Behavioral Rules, Operational Rules, pushback, no-confabulation, source-not-generated, code-removal, design-decisions, project-tooling sections). This is by design -- the template is a minimal starting point, and the project's CLAUDE.md is the fully customized version. However, consumer projects starting from the template will lack several fragments that the edify-plugin project uses (pushback.md, no-confabulation.md, source-not-generated.md, code-removal.md, design-decisions.md, project-tooling.md, sandbox-exemptions.md, claude-config-layout.md, continuation-passing.md, review-requirement.md, etc.). These are copied to `agents/rules/` by init but not referenced in the template's `@` includes.
- [Minor] :23 — completeness: Template references `@agents/session.md` but not `@agents/learnings.md`. The project's own CLAUDE.md references learnings via `@agents/learnings.md`. Consumer projects may want this reference. Low impact -- learnings are typically loaded by skills, not by CLAUDE.md directly.

### Assessment

FR-3 conformance: template uses `@agents/rules/` references (12 fragments). All referenced fragments exist in the plugin's fragments directory. The template provides a reasonable starting point. The gap between template coverage (12 fragments) and total available fragments (27) is a design choice -- the template includes core behavioral rules and lets users add domain-specific ones. The CUSTOMIZE comments guide users on extending.

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 1 |
| Minor | 12 |

**Major findings:**

1. **update/SKILL.md:53** — Wrong path for portable.just source (`$CLAUDE_PLUGIN_ROOT/just/portable.just` vs actual `$CLAUDE_PLUGIN_ROOT/portable.just`). Would cause justfile sync to silently skip with misleading "not yet available" message.

**Overall assessment:**

The migration deliverables are structurally sound. FR-1 through FR-12 are addressed. The plugin manifest, hooks migration, fragment versioning, init/update skills, justfile modularization, symlink cleanup, and documentation updates are all conformant with the outline. The single Major issue (wrong path in update skill) is a straightforward fix. The 12 Minor findings are stylistic consistency, robustness edge cases, and allowed-tools excess -- none affect correctness in the current deployment context (dev mode with `plugin/` directory name).

Files not modified by the migration (inline/SKILL.md, runbook/SKILL.md, review-dispatch-template.md, tier3-planning-process.md) were listed in the review manifest but confirmed unchanged in the migration branch.
