# Justfile Structure Analysis

## Summary

This project uses a three-tier justfile architecture: a root justfile with project-specific recipes, an plugin justfile with reusable symlink utilities, and a Makefile for cache management. The root justfile imports bash helper functions via template variables (not `include` statements) and orchestrates checks/builds. Recipes are partitioned by concern: development workflows (dev/format/check/lint), testing/validation (test/precommit), worktree management (wt-new/wt-ls/wt-rm/wt-merge), and releases (release). The architecture emphasizes project tooling principles: recipes encapsulate complex operations, handle sandbox detection for Claude Code environments, and provide consistent error handling.

## Key Findings

### 1. Root Justfile — `/Users/david/code/edify-plugin-migration/justfile`

**File type:** Main justfile (390 lines)

**Recipes (documented):**

| Recipe | Purpose | Key Details |
|--------|---------|------------|
| `help` | List available recipes | Delegates to `just --list --unsorted` |
| `dev` | Format + cache + precommit | Chained execution: `format cache precommit` |
| `cache` | Rebuild cached help output | Calls `gmake --no-print-directory -C plugin all` to generate `.cache/just-help*.txt` |
| `precommit` | Run all validation checks | Calls 7 validators, lint checks, pytest, line limits (lines 24-35) |
| `test *ARGS` | Run pytest with optional arguments | Supports argument pass-through (`pytest {{ ARGS }}`) |
| `line-limits` | Check file line limits | Calls `./scripts/check_line_limits.sh` |
| `wt-new name base="HEAD"` | Create worktree for parallel work | Git worktree + submodule init + direnv + initial commit |
| `wt-ls` | List active git worktrees | Delegates to `git worktree list` |
| `wt-rm name` | Remove worktree and branch | Force-removes worktree (submodule-aware), deletes branch with fallback |
| `wt-merge name` | Merge worktree + resolve conflicts | Fetches plugin branch, auto-resolves session.md, commits |
| `lint` | Format + style checks + tests | Disables complexity rules (`C901` etc), runs pytest-quiet |
| `check` | Code style without modifications | Runs ruff/docformatter/mypy without changes |
| `format` | Auto-format code | Ruff + docformatter with diff-based reformatting patch system |
| `release *ARGS` | Tag/build/publish to PyPI+GitHub | Supports `--dry-run` and `--rollback`, interactive confirmation |

**Import/include mechanism:**

No `import` or `include` statements. Instead, the root justfile uses **inline bash prolog with template variables**:

```justfile
[private]
bash_prolog := (if trace == "true" { ... }) + "\n" + '''
COMMAND="..."
RED=$'\033[31m'
...
'''
```

Recipes invoke this prolog using `#!{{ bash_prolog }}` at the shebang line (lines 24, 40, etc.). This embeds pre-defined bash functions (`safe`, `visible`, `fail`, `sync`, etc.) into each recipe's script body.

**Sandbox-aware sync:**

```bash
sync() { if [ -w /tmp ]; then uv sync -q; fi; }
```

Detects Claude Code sandbox by checking `/tmp` writability. Skips `uv sync` in sandbox to avoid permission errors.

**Helper functions defined in bash_prolog:**

- `safe <cmd>` — Run command, catch non-zero exit (sets `status=false`)
- `end-safe` — Check `$status` and propagate exit code
- `visible <cmd>` — Show command then execute (implicit echo)
- `fail <msg>` — Print error and exit 1
- `report <header> <cmd>` — Run command, print output with header if non-empty
- `pytest-quiet` — Wrapper that detects pytest failures despite exit code 0 bug
- `run-checks` — Consolidated ruff/docformatter/mypy invocation
- `run-line-limits` — Calls `./scripts/check_line_limits.sh`
- `report-end-safe` — Print success/failure status with color

**Language-specific content:**

- Python tools: ruff, docformatter, mypy, pytest
- Python version/dependency management: `uv` (universal virtualenv tool)
- PyPI publishing: `uv publish`
- GitHub release: `gh` CLI
- All Python-specific (not portable to non-Python projects)

---

### 2. Agent-Core Justfile — `/Users/david/code/edify-plugin-migration/plugin/justfile`

**File type:** Justfile for plugin submodule (98 lines)

**Recipes:**

| Recipe | Purpose | Details |
|--------|---------|---------|
| `help` | List available recipes | `just --list --unsorted` |
| `sync-to-parent` | Create symlinks in parent's `.claude/` | Detailed below |
| `precommit` | Stub validation | Just prints `✓ Precommit OK` (plugin has no validation) |

**sync-to-parent detailed implementation:**

Creates relative symlinks from parent project's `.claude/` directory to plugin sources:

**Structure created:**
```
parent-project/.claude/
  skills/ → (symlinks to ../../plugin/skills/*)
  agents/ → (symlinks to ../../plugin/agents/*.md)
  hooks/ → (symlinks to ../../plugin/hooks/*.sh, *.py)
```

**Algorithm:**
1. Detect parent directory: `PARENT_DIR="$(cd .. && pwd)"`
2. Create `.claude/{skills,agents,hooks}` if missing
3. **Clean stale symlinks**: iterate `$CLAUDE_DIR/skills/*/`, remove symlinks where source doesn't exist
4. **Sync skills**: For each directory in `plugin/skills/`, create relative symlink (removes existing target)
5. **Sync agents**: For each `.md` file in `plugin/agents/`, create relative symlink
6. **Sync hooks**: If `hooks/` exists, sync `hooks.json`, all `.sh` and `.py` files to `.claude/hooks/` (chmod +x hook files)

**Error handling:** Uses `set -euo pipefail` (fail on error, exit undefined variables, fail on pipe failures). Removes targets before creating new symlinks (no error if target missing).

**Output:** Diagnostic echo statements show each action (✓/✗ with file names).

**Platform:**
- Uses `ln -s` for relative symlinks (portable across Unix)
- Uses `rm -rf` / `rm -f` (platform-aware based on file type)
- Relative symlink paths: `../../plugin/skills/$skill_name` (portable across worktrees)

---

### 3. Makefile — `/Users/david/code/edify-plugin-migration/plugin/Makefile`

**File type:** GNU Make configuration (35 lines)

**Purpose:** Cache management for justfile help output (used by CLAUDE.md `@file` references)

**Targets:**

| Target | Produces | Details |
|--------|----------|---------|
| `all` (default) | `.cache/just-help.txt` + `.cache/just-help-plugin.txt` | Depends on justfiles |
| `check` | (validation only) | Runs `make -q all`, exits non-zero if stale |
| `clean` | (none) | Deletes both cache files |

**Dependency tracking:**

```makefile
$(CACHE_DIR)/just-help.txt: $(PARENT)/justfile | $(CACHE_DIR)
    cd $(PARENT) && just help > .cache/just-help.txt

$(CACHE_DIR)/just-help-plugin.txt: justfile | $(CACHE_DIR)
    just help > $@
```

- Root cache depends on root justfile
- Agent-core cache depends on plugin justfile
- Order-only dependency `|` ensures `.cache/` directory exists before writing files

**Integration with root justfile:**

The `cache` recipe (line 18 of root justfile) calls `gmake --no-print-directory -C plugin all`, which runs this Makefile. It's invoked before `precommit` in the `dev` workflow (line 15).

---

### 4. Recipe Dependencies and Portability

**Import/include mechanism: ABSENT (uses template variables instead)**

- ❌ No `import` or `include` statements in any justfile
- ✅ Root justfile uses `#!{{ bash_prolog }}` shebang to inject bash helper functions
- ✅ Agent-core justfile is completely self-contained (no dependencies on root)
- ✅ Makefile coordinates cache generation (standalone tool)

**Why no imports?**
- Just language doesn't support imports from plugin in a reusable way
- Template variable approach (`bash_prolog := ...`) is the idiomatic workaround
- Allows recipes to embed full prolog on-demand without file path coupling

**Cross-recipe dependencies:**

```
dev → format → (uses sync + helpers from bash_prolog)
    → cache  → gmake C plugin
    → precommit → (runs 7 validators + checks)

precommit → sync (function, not recipe)
         → run-checks (function)
         → run-line-limits (function)
         → report-end-safe (function)

release → _fail_if_claudecode (private recipe)

wt-new → (uses sync, visible, fail functions)
wt-rm → (uses visible, fail, git commands)
wt-merge → (complex 2-step: fetch + auto-resolve)
```

**Portable recipes (no Python dependency):**

- `help` — Just built-in, runs anywhere
- `wt-*` (all four) — Git/Bash only, portable across projects
- `cache` — Makefile wrapper, portable
- `lint`, `format`, `check` — Require ruff/docformatter/mypy (Python-specific)

**Python-specific recipes (not portable):**

- `test` — Requires pytest
- `precommit` — Requires validators (ruff, docformatter, mypy, pytest)
- `release` — Requires uv, gh (GitHub CLI), PyPI token

---

### 5. Worktree Recipes in Detail

#### `wt-new name base="HEAD"`

**Purpose:** Create parallel worktree for independent task execution.

**Implementation:**
```bash
repo_name=$(basename "$PWD")                    # Get repo name
wt_dir="../${repo_name}-{{name}}"              # Sibling directory
branch="wt/{{name}}"                            # Create feature branch

# Step 1: Create worktree with new branch
git worktree add "$wt_dir" -b "$branch" "{{base}}"

# Step 2: Initialize submodule with reference to avoid remote fetch
(cd "$wt_dir" && git submodule update --init --reference "$main_dir/plugin")

# Step 3: Check out plugin submodule on its own branch
(cd "$wt_dir/plugin" && git checkout -b "wt/{{name}}")

# Step 4: Set up Python environment
(cd "$wt_dir" && uv sync)

# Step 5: Allow direnv to load
(cd "$wt_dir" && direnv allow 2>/dev/null) || true

# Step 6: Commit initial state
(cd "$wt_dir" && git add -A && git commit -m "Initial worktree state")
```

**Submodule handling (key gotcha):**
- Uses `--reference "$main_dir/plugin"` to avoid remote fetch (plugin is local)
- If commits in plugin aren't pushed, remote clone would fail
- Reference tells git to use local objects as alternates (efficient, local-only)
- Agent-core gets its own branch (not detached HEAD) for easier merge tracking

**Output format:**
```
✓ Worktree ready: ../edify-plugin-migration-<name>
  Launch: cd ../edify-plugin-migration-<name> && claude
```

**Sandbox requirement:** Requires `dangerouslyDisableSandbox: true` (writes outside project directory)

#### `wt-ls`

**Purpose:** Show all active worktrees.

**Implementation:** Direct delegation to `git worktree list` (no post-processing)

**Output:** Standard git format
```
/path/to/main                 <hash> [main]
/path/to/main-task1           <hash> (detached) wt/task1
/path/to/main-task2           <hash> wt/task2
```

#### `wt-rm name`

**Purpose:** Remove worktree directory and delete associated branch.

**Implementation:**
```bash
# Validate worktree exists
if [ ! -d "$wt_dir" ]; then fail "Worktree not found: $wt_dir"; fi

# Warn about uncommitted changes
if ! (cd "$wt_dir" && git diff --quiet HEAD); then
    echo "Warning: $wt_dir has uncommitted changes"
fi

# Remove worktree (--force required for submodules)
git worktree remove --force "$wt_dir"

# Delete branch (with fallback message if unmerged)
if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    git branch -d "$branch" || \
        echo "Branch $branch has unmerged changes. Use: git branch -D $branch"
fi
```

**Key detail:** `--force` flag is **required** because git refuses to remove worktrees with submodules, even after cleanup. This matches the learnings documented in CLAUDE.md.

#### `wt-merge name`

**Purpose:** Merge worktree branch back to main and resolve conflicts.

**Implementation (2 steps):**

**Step 1: Fetch and merge plugin commits**
```bash
# Check if plugin branch exists in worktree
if [ -d "$wt_dir/plugin" ] && (cd "$wt_dir/plugin" && git rev-parse --verify "$branch" >/dev/null 2>&1); then
    # Fetch commits from worktree's plugin into main's submodule
    (cd plugin && git fetch "$wt_dir/plugin" "$branch:$branch")
    # Merge the branch
    (cd plugin && git merge --no-edit "$branch")
    # Clean up local branch
    (cd plugin && git branch -d "$branch")
    # Stage submodule change
    git add plugin
fi
```

**Step 2: Merge worktree branch with auto-conflict resolution**
```bash
if ! git merge --no-edit "$branch"; then
    # Auto-resolve session.md with ours (parent's version)
    if git diff --name-only --diff-filter=U | grep -q "agents/session.md"; then
        git checkout --ours agents/session.md
        git add agents/session.md
    fi

    # Fail if other conflicts remain
    remaining=$(git diff --name-only --diff-filter=U)
    if [ -n "$remaining" ]; then
        echo "Unresolved conflicts:"
        echo "$remaining"
        fail "Resolve conflicts, then: git commit --no-edit"
    fi
    git commit --no-edit
fi
```

**Conflict resolution strategy:**
- Agent-core: Merge explicitly, allowing conflicts (for review)
- session.md: Auto-resolve using parent's version (`--ours`) — rationale: parent had most recent state
- Other files: Fail with diagnostic message (requires manual resolution)

**Output:**
```
✓ Merged wt/task1
  Cleanup: just wt-rm task1
```

---

### 6. Validation and Testing Recipes

#### `precommit`

**Purpose:** Run all pre-commit checks (called by `dev` workflow).

**Sequence:**

1. `sync` — Update Python dependencies (skipped in sandbox)
2. `plugin/bin/validate-tasks.py agents/session.md agents/learnings.md` — Validate session and learnings structure
3. `plugin/bin/validate-learnings.py agents/learnings.md` — Additional learnings validation
4. `plugin/bin/validate-decision-files.py` — Validate agents/decisions/*.md structure
5. `plugin/bin/validate-memory-index.py agents/memory-index.md` — Validate memory index format
6. `plugin/bin/validate-jobs.py` — Validate jobs.md structure
7. `gmake --no-print-directory -C plugin check` — Agent-core cache validation (Makefile)
8. `run-checks` — ruff, docformatter, mypy checks
9. `safe pytest-quiet` — Run tests with quiet mode (bug workaround)
10. `run-line-limits` — Check line length constraints
11. `report-end-safe` — Print final status

All validators are project-specific (not portable).

#### `test *ARGS`

**Purpose:** Run pytest with optional arguments.

**Key feature:** Argument pass-through
```bash
sync
pytest {{ ARGS }}
```

Allows: `just test tests/test_foo.py -v`

---

### 7. Release Recipe

**Purpose:** Automate versioning, tagging, building, and publishing to PyPI + GitHub.

**Features:**

- `--dry-run` — Verify permissions without publishing
- `--rollback` — Revert a failed dry-run
- Positional arg for bump type: `patch` (default), `minor`, `major`

**Workflow:**

```
Check preconditions (on main branch, clean working tree, tag not exists)
↓
Version bump (uv version --bump $BUMP)
↓
Commit version change (git commit -m "🔖 Release X.Y.Z")
↓
Build distribution (uv build)
↓
IF DRY_RUN:
  Verify git/PyPI/GitHub permissions (no actual push/publish)
  Rollback local changes
ELSE:
  Push to git (+ tag)
  Publish to PyPI (uv publish)
  Create GitHub release (gh release create)
```

**Rollback mechanism:**

If dry-run exits non-zero (permission failure), cleanup function:
1. Reverts commit: `git reset --hard HEAD~1`
2. Returns to original branch
3. Cleans up build artifacts matching version

Supports explicit rollback via `just release --rollback` (if release commit at HEAD).

**Protected:** Recipe blocked if `CLAUDECODE` env var set (prevents accidental execution from agent context).

---

## Patterns

### Bash Prolog Pattern

**Problem:** Recipes need consistent helper functions (fail, visible, report) without file inclusion.

**Solution:** Define `bash_prolog` as a private template variable, inject via `#!{{ bash_prolog }}` shebang.

**Benefits:**
- No file path coupling (no imports)
- Self-contained (each recipe is self-describing)
- Sandboxable (all functions defined inline)
- Consistent across recipes

**Anti-pattern avoided:** Separate bash library file (would require imports, breaks project tooling isolation)

### Sandbox Detection

**Pattern:**
```justfile
[private]
sandboxed := shell('[ -w /tmp ] && echo "0" || echo "1"')
```

**Used in:** Makefile (plugin/configs/justfile-base.just)

**In root justfile:** Inline check in `sync()` function:
```bash
sync() { if [ -w /tmp ]; then uv sync -q; fi; }
```

**Rationale:** Claude Code sandbox prevents `/tmp` writes. Skip dependency updates in sandbox to avoid permission errors.

### Relative Symlink Paths

**Pattern:** `ln -s "../../plugin/skills/$skill_name" "$target"`

**Portability:** Works across worktrees because paths are relative to `.claude/` location.

**Alternative avoided:** Absolute paths (would break across different machine paths, different worktree locations).

### Git Submodule Reference Handling

**Pattern in wt-new:**
```bash
git submodule update --init --reference "$main_dir/plugin"
```

**Solves:** Unpushed plugin commits. Avoids remote fetch by using local objects as alternates.

**Documented in:** agents/learnings.md (Git worktree submodule gotchas)

### Auto-Conflict Resolution

**Pattern in wt-merge:**
```bash
if ! git merge --no-edit "$branch"; then
    git checkout --ours agents/session.md  # Auto-resolve with parent's version
    git add agents/session.md
fi
```

**Rationale:** session.md is always authoritative in the parent (main branch). Worktree's version is stale. Auto-resolve prevents manual merge step.

**Exception:** Other files require manual resolution (fail with diagnostic).

---

## Gaps / Unresolved Questions

1. **No testfile imports discovered** — Justfile uses template variables instead of `include`. The comment in Makefile (lines 4-5) says "FUTURE: When justfiles are factored to use plugin includes..." — This suggests a planned refactoring to add `include` statements, not yet implemented.

2. **Cache staleness enforcement** — Makefile `check` target exits non-zero if cache is stale, but root `precommit` calls `gmake check` which could fail. How is this failure propagated? (Answer: `set -e` in bash_prolog catches it.)

3. **Docformatter line length** — CLAUDE.md references 80-char limit, but Makefile doesn't validate this. The `check` recipe calls `docformatter -c src tests` which checks via pyproject.toml settings. Need to verify docformatter configuration enforces 80-char limit.

4. **Ruff complexity exceptions** — Root `lint` disables `C901` (complexity), but `precommit` includes full ruff check. Are complex functions flagged in precommit? (Answer: They are, but not treated as fatal — it's a warning-level check.)

5. **pytest-quiet bug workaround** — Custom wrapper detects "Re-run failed: " in output. Suggests pytest -q has a known exit code bug. Is this documented upstream? Why not use `-v` flag instead?

6. **Line limits validation** — Calls `./scripts/check_line_limits.sh` but file not examined. What constraints does it enforce? Are there exceptions for justfiles themselves?

7. **Worktree session.md handling** — wt-merge auto-resolves with `--ours`. Implies parent session.md is always correct. But execute-rule.md mentions focused session.md for worktrees. Are these two mechanisms aligned? (Answer: execute-rule.md describes the initial focused session.md in the worktree; wt-merge assumes final session.md in worktree was updated during execution, parent's version is newer.)

8. **Agent-core cache output** — Root justfile reads `.cache/just-help-plugin.txt` via CLAUDE.md `@` reference. Is this cache always fresh before it's read? (Answer: Yes — `dev` recipe calls `cache` before `precommit`, which runs validators that might read it.)

---

## File Locations (Absolute Paths)

- **Root justfile:** `/Users/david/code/edify-plugin-migration/justfile` (390 lines)
- **Agent-core justfile:** `/Users/david/code/edify-plugin-migration/plugin/justfile` (98 lines)
- **Agent-core Makefile:** `/Users/david/code/edify-plugin-migration/plugin/Makefile` (35 lines)
- **Base config template:** `/Users/david/code/edify-plugin-migration/plugin/configs/justfile-base.just` (152 lines)

---

## Key Recipes Reference Table

| Recipe | File | Type | Portable? | Sandbox-safe? | Requires Restart? |
|--------|------|------|-----------|---------------|-------------------|
| `help` | root | Info | ✅ | ✅ | No |
| `dev` | root | Workflow | ❌ (Python) | Partial | No |
| `cache` | root | Build | ✅ | ✅ | No |
| `precommit` | root | Validation | ❌ (Python) | Partial | No |
| `test` | root | Execution | ❌ (Python) | Partial | No |
| `line-limits` | root | Validation | ❓ (bash script) | ✅ | No |
| `wt-new` | root | Git | ✅ | ❌ (needs `dangerouslyDisableSandbox`) | Maybe |
| `wt-ls` | root | Git | ✅ | ✅ | No |
| `wt-rm` | root | Git | ✅ | ❌ (needs `dangerouslyDisableSandbox`) | Maybe |
| `wt-merge` | root | Git | ✅ | ❌ (needs `dangerouslyDisableSandbox`) | Maybe |
| `lint` | root | Validation | ❌ (Python) | Partial | No |
| `check` | root | Validation | ❌ (Python) | Partial | No |
| `format` | root | Transformation | ❌ (Python) | Partial | No |
| `release` | root | Publishing | ❌ (Python+gh) | ❌ (protected) | No |
| `sync-to-parent` | plugin | Setup | ✅ | ❌ (needs `dangerouslyDisableSandbox`) | Yes (hook reloads) |

---

## Summary of Findings

**Architecture:** Justfiles use inline bash prolog injection (`#!{{ bash_prolog }}`) rather than imports. Root justfile is project-specific (Python validation, PyPI release). Agent-core justfile is generic (symlink management). Makefile coordinates cache generation.

**Key strength:** Clear separation of concerns. Root handles project builds; plugin handles environment setup. No cyclic dependencies.

**Key risk:** No include mechanism discovered. Future refactoring (per Makefile comment) may change this pattern. Template variable approach is idiomatic but less flexible than includes.

**Worktree recipes:** Fully featured (create/list/remove/merge). Includes submodule-aware operations, auto-conflict resolution for session.md, and sandboxing annotations. Matches learnings documented in agents/learnings.md.
