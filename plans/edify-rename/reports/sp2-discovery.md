# SP-2 Discovery: Package Rename `claudeutils` → `edify`

## Summary

SP-2 renames the Python package from `claudeutils` to `edify`, affecting the CLI entry point, all source code internal imports, test references, configuration, and submodule runtime dependencies. Total scope: 1,389 occurrences across 388 files. The rename touches three boundary categories: (1) package name in config (`pyproject.toml` scripts), (2) internal imports across 103 source files and 160 test files, and (3) critical runtime references in plugin hooks and scripts deferred from SP-1.

## 1. Source Code (`src/claudeutils/`)

### File Inventory
- **Total Python files:** 103
- **Internal `claudeutils` imports:** 153 occurrences

### Details
All 103 Python files in `src/claudeutils/` are candidates for directory move to `src/edify/`. Each file that imports from the package must update the import statement.

**Pattern:** `from claudeutils.X import Y` → `from edify.X import Y` and `import claudeutils.X` → `import edify.X`

**Examples of import-heavy files:**
- `src/claudeutils/cli.py` — 17 imports from claudeutils submodules
- `src/claudeutils/session/cli.py` — 5 imports from claudeutils
- `src/claudeutils/validation/cli.py` — 10 imports from claudeutils
- `src/claudeutils/recall/cli.py` — 7 imports from claudeutils
- `src/claudeutils/worktree/cli.py` — 9 imports from claudeutils

**Key files to move:**
- `/Users/david/code/claudeutils/src/claudeutils/` → `/Users/david/code/claudeutils/src/edify/`

All subdirectories and nested imports follow automatically with the directory move and import rewrites.

## 2. Tests (`tests/`)

### File Inventory
- **Total test files:** 196
- **Test files with `claudeutils` references:** 160 files
- **Total occurrences:** 643

### Categories
- **Import statements:** Majority are `from claudeutils.X import Y` patterns
- **String literals/mock targets:** CLI invocation strings (`"claudeutils _command"`), pytest parametrization strings, mock targets
- **Mixed:** Many files have both imports and string references

**Examples:**
- `/Users/david/code/claudeutils/tests/test_cli_tokens.py` — imports + usage
- `/Users/david/code/claudeutils/tests/test_session_commit.py` — imports + mock targets
- `/Users/david/code/claudeutils/tests/test_worktree_merge_parent.py` — imports + subprocess mock strings

## 3. Configuration (`pyproject.toml`)

### Scope
- **File:** `/Users/david/code/claudeutils/pyproject.toml`
- **Occurrences:** 6
- **Critical items:**
  - **Line 2:** `name = "claudeutils"` → `name = "edify"`
  - **Line 22:** `claudeutils = "claudeutils.cli:main"` → `edify = "edify.cli:main"`
  - **Lines 18-19:** GitHub URLs (see boundary section below)

### Details
The `[project.scripts]` section defines the CLI entry point. This is the primary mechanism for the CLI command name change (`claudeutils` → `edify` at shell level).

**Example section:**
```toml
[project.scripts]
edify = "edify.cli:main"
```

After SP-2, `pip install .` or `uv tool install .` creates an `edify` command instead of `claudeutils`.

## 4. Plugin Runtime References (Submodule)

### Scope
These are files in `plugin/` that reference `claudeutils` as a runtime CLI/package dependency. **These were deferred from SP-1** because submodule runtime refs to `claudeutils` break immediately if renamed before the parent package renames in SP-2.

### Breakdown by File

#### `/Users/david/code/claudeutils/plugin/bin/compress-key.py`
- **Type:** Python import
- **Line 7:** `from claudeutils.when.compress import compress_key, load_heading_corpus`
- **Category:** Direct import of parent's installed package

#### `/Users/david/code/claudeutils/plugin/bin/when-resolve.py`
- **Type:** Python import
- **Line 7:** `from claudeutils.when.cli import when_cmd`
- **Category:** Direct import of parent's installed package

#### `/Users/david/code/claudeutils/plugin/bin/prepare-runbook.py`
- **Type:** Subprocess call (CLI invocation) + error message
- **Line 139:** `cmd = ["claudeutils", "_recall", "resolve"] + triggers`
- **Line 143:** `print("WARNING: recall resolve: claudeutils not found", file=sys.stderr)`
- **Category:** Parent CLI invocation; both subprocess call and error message reference the CLI name

#### `/Users/david/code/claudeutils/plugin/hooks/userpromptsubmit-shortcuts.py`
- **Type:** Python import + help text
- **Line 78:** `'Resolve topic-relevant recall: claudeutils _recall resolve "when <topic>" ...\n'`
- **Line 888:** `from claudeutils.planstate.inference import infer_state`
- **Category:** (1) Help text with CLI name example, (2) Direct import of parent's installed package

#### `/Users/david/code/claudeutils/plugin/hooks/pretooluse-recipe-redirect.py`
- **Type:** Error/redirect messages (help text, not code execution)
- **Lines 107, 108, 109:** Error messages suggesting `claudeutils _worktree` CLI
  - `"Use claudeutils _worktree — wrapper manages session.md"`
  - `"Use \`claudeutils _worktree\` — wrapper manages session.md."`
  - `"🚫 git worktree — use claudeutils _worktree"`
- **Category:** User-facing error messages; no functional impact but improves UX if updated
- **Note:** SP-1 notes suggest this file was already updated for hook refactoring; verify grep results

#### `/Users/david/code/claudeutils/plugin/hooks/sessionstart-health.sh`
- **Type:** pip install command (subprocess/shell execution)
- **Lines 32, 41:**
  - `uv pip install --quiet --python "$VENV_DIR/bin/python" "claudeutils==$EDIFY_VERSION" > /dev/null 2>&1`
  - `"$VENV_DIR/bin/pip" install --quiet "claudeutils==$EDIFY_VERSION" > /dev/null 2>&1`
- **Category:** Package installation references; critical for environment setup

#### `/Users/david/code/claudeutils/plugin/portable.just`
- **Type:** CLI invocation strings (justfile recipes)
- **Occurrences:** 10 occurrences across repeated `claudeutils validate` commands
- **Lines (sample):** 130-132: `report "validate memory-index" claudeutils validate memory-index`
- **Category:** Justfile recipes invoking parent's CLI; used during validation recipes
- **Note:** Lines repeat because validation recipes are duplicated in the file

### Summary: Plugin Files to Modify
| File | Type | Count | Priority |
|------|------|-------|----------|
| `plugin/bin/compress-key.py` | import | 1 | High |
| `plugin/bin/when-resolve.py` | import | 1 | High |
| `plugin/bin/prepare-runbook.py` | subprocess + error-msg | 2 | High |
| `plugin/hooks/userpromptsubmit-shortcuts.py` | import + help-text | 2 | High |
| `plugin/hooks/pretooluse-recipe-redirect.py` | help-text | 3 | Medium |
| `plugin/hooks/sessionstart-health.sh` | pip-install | 2 | High |
| `plugin/portable.just` | CLI invocation | 10 | High |

**Total plugin occurrences:** 21

## 5. Agentic Prose (agents/, fragments/, skills/)

### Scope
- **Directories:** `agents/`, `plugin/fragments/`, `plugin/skills/`
- **Total occurrences:** 94
- **Category:** Documentation, instruction fragments, skill definitions, agent system prompts

### Examples
- **agents/decisions/*.md** — References to `claudeutils` in decision documentation
- **agents/learnings.md** — Accumulated learnings mentioning `claudeutils` context
- **agents/role-*.sys.md** — Agent role definitions
- **plugin/fragments/*.md** — Instruction fragments for agent behavior
- **plugin/skills/*/*.md** — Skill documentation and examples

**No functionality impact** — these are documentation updates only. However, they improve consistency and user-facing clarity.

## 6. Active Plan Files

### Scope
Excluding `plans/edify-rename/`, `plans/plugin-migration/`, and `plans/retrospective/`:
- **Total occurrences:** 370

### Categories
- Requirements, briefs, outlines, reports, and supporting notes
- References to `claudeutils` as context in plan documentation
- Examples of CLI usage in plan steps
- Historical references in older plans

**No functionality impact** — documentation updates for clarity. User-facing text (examples, instructions) benefits from consistency.

## 7. README.md and Other Docs

### `/Users/david/code/claudeutils/README.md`
- **Line 1:** `# claudeutils` → `# edify`
- **Line 11:** `git clone https://github.com/ddaanet/claudeutils` (see boundary below)
- **Line 13:** `uv tool install .` (no change to command, package name handled by pyproject.toml)
- **Multiple:** README references to `claudeutils` framework elements

## 8. Boundary Classifications

### A. GitHub Repository URL (FR-12: Separate Task)

**Files affected:**
- `pyproject.toml` lines 18-19
- `README.md` line 11
- `plans/edify-rename/requirements.md` (reference only)

**URLs to update:**
- `https://github.com/ddaanet/claudeutils` → `https://github.com/ddaanet/edify`

**Status:** Classified as **FR-12** (external GitHub rename, out of SP-2 scope). User must rename the GitHub repository before or after SP-2, but the URL changes are part of a separate step. **Flag in runbook:** Check GitHub rename completion before SP-2 final validation.

### B. PyPI Package Name

**Status:** Not currently on PyPI ("Not on PyPI. Install from source" per README.md line 8). The `name = "claudeutils"` in `pyproject.toml` defines the package name for future PyPI publication. **No external dependency:** Changing this does not require PyPI coordination.

## Summary Table

| Category | Files | Occurrences | Complexity |
|----------|-------|-------------|-----------|
| Source code (`src/`) | 103 | 174 | Directory move + imports |
| Tests (`tests/`) | 160 | 643 | Imports + string refs |
| Config (`pyproject.toml`) | 1 | 6 | Entry point + URLs |
| Plugin runtime refs (`plugin/`) | 7 | 21 | Imports + subprocess + shell |
| Agentic prose (`agents/`, `fragments/`, `skills/`) | Multiple | 94 | Documentation only |
| Active plans | Multiple | 370 | Documentation only |
| **TOTAL** | **388** | **1,389** | — |

## Scope Notes

### Mechanical vs. Content Edits
- **Mechanical (must change):** Source directory rename, imports, config entry point, pip install commands, subprocess calls, error message strings used by tests/CLI, validation recipes
- **Content (improve UX):** Help text, documentation examples, agentic prose

### Dependency Order
1. **SP-2 Phase 1:** Directory rename + import rewrites (src + tests)
2. **SP-2 Phase 2:** Config + entry point (`pyproject.toml`)
3. **SP-2 Phase 3:** Plugin runtime refs (ensure these stay aligned with parent package name)
4. **SP-2 Phase 4:** Documentation + agentic prose (low risk, high polish)
5. **FR-12 (parallel):** GitHub repository rename (external, can happen anytime before publication)

### Verification Checkpoints
- `just precommit` after each phase (ensures linters + tests pass)
- `pip install .` or `uv tool install .` in a fresh venv (confirms entry point works)
- `edify --version` runs without error
- `edify _status`, `edify _worktree ls` work (sample CLI commands)

## Key Learning from SP-1

SP-1 learned that `.just` extension was missed by discovery grep filtering by extension. **SP-2 must use extensionless grep** or enumerate all tracked text file types via `git ls-files`. The `plugin/portable.just` file was caught in this task's discovery, but the pattern-miss risk remains for other edge-case extensions.

**Recommendation:** In SP-2 discovery verification step, explicitly check:
- `*.just`, `justfile` files for any missed patterns
- File extensions not in the default grep (shell scripts, config files, etc.)
