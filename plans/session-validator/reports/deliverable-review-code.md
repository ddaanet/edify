# Deliverable Review: Session.md Validator — Code

**Reviewer:** Opus 4.6
**Baseline:** `plans/session-validator/requirements.md`
**Scope:** 9 source files listed in review request

---

## Findings by File

### src/claudeutils/validation/task_parsing.py

**[Severity: Minor]** task_parsing.py:21 — Conformance — `TASK_PATTERN` does not anchor on em dash `—` after the bold name, while `tasks.py:16` still does (`\*\* —`). The shared module pattern matches `- [.] **Name**` without requiring em dash, meaning a malformed line like `- [ ] **Name** extra stuff` parses successfully. This is intentional (permissive parse, strict validation elsewhere) but creates a behavioral difference: `tasks.py` still defines its own `TASK_PATTERN` that requires `—`, so the two modules can disagree on what constitutes a task line.

**[Severity: Minor]** task_parsing.py:15 — Vacuity — `TASK_PATTERN` in `task_parsing.py` and the separate `TASK_PATTERN` in `session_structure.py:21` are nearly identical but not the same module-level constant. NFR-4 requires consolidation into a single extraction module, yet `session_structure.py` retains its own `TASK_PATTERN` (used by `extract_section_tasks`). Two definitions persist.

**[Severity: Minor]** task_parsing.py:87 — Robustness — Priority parsing uses `re.match(r"^\d+(\.\d+)?$", seg_lower)` which accepts strings like `999999999999` as valid priorities. No upper bound or format constraint. Low risk since priority is informational, but no validation of the value is performed anywhere else either.

### src/claudeutils/validation/session_structure.py

**[Severity: Minor]** session_structure.py:21,25-43 — Vacuity — `TASK_PATTERN` is defined at module level (line 21) and used only by `extract_section_tasks`. This is a duplicate of the pattern in `task_parsing.py`. `ALLOWED_SECTIONS` and `SECTION_ORDER` are identical lists defined as separate constants (lines 25-43). One should reference the other or be a single constant.

**[Severity: Minor]** session_structure.py:282 — Robustness — `check_task_section_lines` uses `stripped.startswith("  ")` (two spaces) to detect indented sub-items. A line indented with a single space or tab would not be caught as indented and would be treated as a top-level task line requiring parsing. This could produce false-positive errors on lines with non-standard indentation.

**[Severity: Minor]** session_structure.py:240 — Functional correctness — The ordering check in `check_section_schema` reports `{name} appears before {prev_name}` which reads as "{current_section} appears before {previous_section}" — but the current section appears _after_ the previous section in the file. The error message means "should appear before" but reads ambiguously. The message at line 243 says "In-tree Tasks appears before Next Steps" when the actual file has Next Steps first. This is confusing: it names the out-of-order section and which section it incorrectly follows, but the English reads backward.

**[Severity: Major]** session_structure.py:338-392 — Conformance — `validate()` runs `check_worktree_markers()` and feeds errors into the unified error list. However, the warnings (orphaned worktrees) returned as the second element of the tuple are silently discarded (line 387-389: `marker_errors, _ = check_worktree_markers(...)`). FR-4 acceptance criteria specify "Worktrees in `git worktree list` that don't appear as markers produce a warning." NFR-1 specifies "Warnings printed to stderr but don't fail the check." The warnings are computed but never surfaced to the caller or to stderr.

### src/claudeutils/validation/session_commands.py

**[Severity: Minor]** session_commands.py:35 — Functional completeness — The `break` after the first matching anti-pattern means only one anti-pattern is reported per task line. If a command matches multiple anti-patterns, only the first is reported. Currently there is only one pattern so this is not a live issue, but adding a second overlapping pattern would silently lose diagnostics.

No other issues found. Clean module, well-structured, extensible as specified.

### src/claudeutils/validation/session_worktrees.py

**[Severity: Major]** session_worktrees.py:36-52 — Functional correctness — `get_worktree_slugs` parses `git worktree list --porcelain` output incorrectly. The porcelain format has multi-line entries where each entry starts with `worktree <path>` followed by metadata lines. This code iterates all lines and does `parts = line.split()`, treating each line independently. For a `worktree /path/to/.claude/worktrees/slug` line, `parts[0]` would be `worktree`, not the path. The code only checks `if ".claude/worktrees/" in path` where `path = parts[0]`, so it would check if `".claude/worktrees/"` is in `"worktree"` — which is always false. The existing `_parse_worktree_list` in `git_ops.py` correctly parses the porcelain format (splits on `"worktree "` prefix, tracks multi-line entries). However: this code path is only reached when `worktree_slugs` is `None` (production path, not test path). All tests pass `worktree_slugs=` explicitly, so this bug is untested.

**[Severity: Minor]** session_worktrees.py:44 — Robustness — `path.removesuffix("/.git")` followed by `if path.endswith(".git"): continue` — bare repositories have paths ending in `.git` (the directory itself). The `removesuffix` removes `/.git` (with leading slash) but the skip check looks for trailing `.git`. A path like `/repo.git` would survive the first check but be skipped by the second. This is defensive but the logic is confusing and the intent unclear.

### src/claudeutils/validation/plan_archive.py

**[Severity: Minor]** plan_archive.py:34 — Robustness — `result.stdout.strip().split("\n")` on empty stdout produces `['']` (a list with one empty string), not `[]`. The `if not line: continue` on line 35 handles this, so no functional bug, but the data flow is non-obvious.

**[Severity: Minor]** plan_archive.py:42-47 — Functional completeness — Only `status == "D"` (deleted) is checked. Git rename operations produce `R` status with two paths. A renamed plan directory (e.g., `plans/old-name/` to `plans/new-name/`) would not be detected as a deletion. The requirements say "staged for deletion" which is specifically `D`, so this may be intentional, but renames could be a gap.

No other issues found. Good parameterization for testability.

### src/claudeutils/validation/cli.py

**[Severity: Minor]** cli.py:82 — Conformance — `_run_validator("plan-archive", check_plan_archive_coverage, all_errors, root)` passes only `root` to `check_plan_archive_coverage`. Since `deleted_plans` and `archive_headings` default to `None`, the function will query git staging and read the archive file. This is correct for production use but means the CLI always queries live git state. No issue, just noting the coupling.

**[Severity: Minor]** cli.py:185-193 — Error signaling — The `plan_archive` CLI subcommand prints errors to stderr and exits 1, consistent with other subcommands. However, the main `validate` command (line 100-104) prints errors with a `"Error ({validator_name}):"` prefix and then indented messages. The `plan_archive` errors from `check_plan_archive_coverage` don't have the `"  "` prefix that other validators add to their error strings, so the output formatting will be inconsistent — plan-archive errors will be double-indented (`"  Deleted plan 'x'..."` under `"  Error (plan-archive):"`).

### src/claudeutils/validation/tasks.py

**[Severity: Minor]** tasks.py:16 — Conformance (NFR-4) — `TASK_PATTERN` remains as a module-level regex in `tasks.py` rather than importing from `task_parsing.py`. The pattern here requires `— ` after the bold name (`\*\*(.+?)\*\* —`), while `task_parsing.py` does not. This means `tasks.py` and `task_parsing.py` can disagree on what constitutes a task line. NFR-4 says "Consolidate session.md task-line parsing into a single extraction module" and "New validators must consume the shared layer, not add additional regex copies." The consumer migration updated the character class from specific chars to `.` but did not eliminate the duplicate definition.

### src/claudeutils/worktree/resolve.py

No issues found. The consumer migration correctly updates `[x–]` (en dash) to `[x-]` (hyphen), consistent with the task status marker migration.

### src/claudeutils/worktree/session.py

**[Severity: Minor]** session.py:30 — Conformance (NFR-4) — Same as `tasks.py`: `task_pattern` remains as a local regex rather than importing from `task_parsing.py`. The consumer migration updated the character class but did not eliminate the duplicate definition.

---

## Cross-Cutting Findings

### Missing FR-2: Task Format Validation

**[Severity: Major]** — Conformance — FR-2 specifies: task name uniqueness across the file, model tier validation, worktree marker format validation. Task name uniqueness exists in `tasks.py` (pre-existing). Model tier and worktree marker validation exist in section-aware validation (`check_task_section_lines`). However, FR-2 also specifies "Worktree markers match `-> \`slug\`` when present (inline format after Worktree Tasks elimination)" as a format check — verifying the marker syntax itself is well-formed. The current worktree marker validation in `session_worktrees.py` only cross-references against `git worktree list`; it does not validate marker syntax (e.g., reject `-> slug` without backticks, or malformed arrow characters). The regex in `task_parsing.py` extracts markers but a malformed marker like `> slug` (missing arrow) or `-> slug` (ASCII arrow instead of Unicode) would simply not be extracted — silently passing rather than erroring. Whether this is a gap depends on whether the parse-layer's non-match counts as implicit rejection via section-aware validation. If a worktree marker is present in non-standard format, the task line still parses (name is extracted), so section-aware validation would not catch it.

### Missing FR-3: Reference Validity

**[Severity: Major]** — Conformance — FR-3 specifies three acceptance criteria: (1) paths in Reference Files section exist on disk, (2) no `tmp/` paths anywhere in session.md, (3) backtick-wrapped paths in task metadata checked. Criterion 1 is implemented in `check_reference_files`. Criterion 2 is implemented in the pre-existing `session_refs.py`. Criterion 3 ("Backtick-wrapped paths in task metadata are checked if they look like filesystem paths") is not implemented. Task lines like `Plan: plans/nonexistent/` with backtick-wrapped metadata paths are not validated for existence.

### Missing NFR-2: --fix Flag

**[Severity: Major]** — Conformance — NFR-2 specifies "`--fix` flag applies mechanical fixes (section reordering, stale reference removal)." No `--fix` flag exists anywhere in the CLI or validator modules. `grep --fix` across the validation source returns zero matches. This is a complete omission.

### Backward Compatibility

**[Severity: Minor]** — Robustness — The validators handle `"Pending Tasks"` as a legacy alias for `"In-tree Tasks"` in `ALLOWED_SECTIONS` and `check_task_section_lines`. This provides backward compatibility with session.md files on main that may use the old section name. The status line validation (`check_status_line`) is new and would fail on session.md files without the `**Status:**` line — but since this is a new check, any existing session.md would need updating. Graceful degradation is adequate for the section schema and task parsing; the status line check is strict by design.

### NFR-4 Consolidation Incomplete

**[Severity: Minor]** — Conformance — Three regex consumers were identified for consolidation. The new validators (`session_commands.py`, `session_worktrees.py`, `session_structure.py:check_task_section_lines`) correctly import from `task_parsing.py`. However, the existing consumers (`tasks.py:16`, `session_structure.py:21`, `worktree/session.py:30`) retain their own regex definitions. The requirement says "Consolidate ... into a single extraction module" and "not add additional regex copies." The new validators comply; the existing consumers were only partially migrated (character class updated, definition not removed).

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major    | 4 |
| Minor    | 13 |
| **Total** | **17** |

### Major findings:
1. Worktree warnings silently discarded in `validate()` — never surfaced to stderr per NFR-1
2. `get_worktree_slugs` porcelain parser is broken in production path (all tests bypass it)
3. FR-3 criterion 3 (backtick path validation in task metadata) not implemented
4. NFR-2 (`--fix` flag) completely missing

### Assessment

The implemented FRs (FR-1, FR-4, FR-5, FR-6, FR-7) and section-aware validation are well-structured, tested, and functionally correct within their scope. The shared parsing module (NFR-4) is a sound design with good separation between permissive extraction and strict validation. Test coverage is thorough for the tested code paths.

The main gaps are: one production-path bug (worktree porcelain parsing), one discarded output (warnings), and two requirements not implemented (FR-3 criterion 3, NFR-2). The NFR-4 consolidation is partially complete — new code uses the shared module but existing consumers retain duplicate definitions.
