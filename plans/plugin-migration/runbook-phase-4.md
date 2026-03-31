### Phase 4: Justfile modularization (type: general, model: sonnet)

Extract portable recipes and update root justfile.

**Depends on D-5 redesign:** Current D-5 specifies a single `portable.just`. Thematic modules are the better design — consumers import only what they need. Module boundaries need design work before this phase executes. If D-5 redesign has not occurred by execution time, proceed with single `portable.just` as originally designed.

---

## Step 4.1: Create portable justfile module(s)

**Objective**: Extract portable recipe stack from current `justfile` into plugin-distributed module(s).

**Prerequisites**:
- Read `justfile` (current recipe definitions — identify which recipes are portable vs project-specific)
- Read outline.md §Key Decisions D-5 (full list of portable recipes)
- Read outline.md §Component 5 (import boundary constraints, variable merging)
- Check if D-5 redesign has occurred (thematic modules vs single file)

**Implementation**:
1. Create `plugin/portable.just` containing all portable recipes
2. Extract these recipes (per D-5):
   - `claude` / `claude0` — opinionated launch wrapper (system prompt replacement, plugin config)
   - `lint` / `format` / `check` — ruff, mypy, docformatter
   - `red-lint` — permissive TDD variant (recipe name in justfile is `red-lint`, not `red`; D-5 outline uses `red` as shorthand)
   - `precommit` — full lint with complexity
   - `precommit-base` — edify-plugin validators only
   - `test` — pytest with framework flags
   - `wt-*` — manual worktree fallbacks (wt-new, wt-task, wt-ls, wt-rm, wt-merge)
4. Do NOT include: `release`, `line-limits`, project-specific helpers
5. Each module needs its own `bash_prolog` string variable — portable recipes use `#!{{ bash_prolog }}` as their shebang, so the portable module must define a self-contained prolog with all required bash functions. The root justfile's `bash_prolog` is NOT available to imported modules before the import resolves. Define:
   ```just
   # Self-contained bash prolog for portable module (cannot rely on root justfile's bash_prolog)
   bash_prolog := "/usr/bin/env bash\nset -euo pipefail\n" + '''
   RED=$'\033[31m'
   GREEN=$'\033[32m'
   NORMAL=$'\033[0m'
   safe () { "$@" || status=false; }
   end-safe () { ${status:-true}; }
   show () { echo "$@"; }
   visible () { show "$@"; "$@"; }
   fail () { echo "${RED}FAIL: $*${NORMAL}" >&2; exit 1; }
   '''
   ```
   Note: `safe`/`end-safe` are needed by `lint` and `check`; `visible`/`fail` are needed by `wt-*`. Do not omit them.
   Note: Variable merging across import boundaries means the root `bash_prolog` will override the portable module's `bash_prolog` in the root project context — this is correct behavior (root wins). The portable module's `bash_prolog` serves standalone-import consumers.
6. Update `claude` recipe to use `--plugin-dir ./plugin` flag

**Expected Outcome**:
- Portable justfile module(s) exist in `plugin/`
- All portable recipes present with correct bash prolog
- `release` and project-specific recipes NOT included

**Error Conditions**:
- If recipe depends on project-specific variables not in prolog → add to prolog or restructure
- If `just` import syntax doesn't support the module structure → simplify to single file

**Validation**:
- `just --justfile plugin/portable.just --list` shows all expected recipes
- `just --justfile plugin/portable.just --evaluate bash_prolog` shows the prolog string (confirms variable is defined)
- No project-specific recipes present (`release`, `line-limits` absent from listing)

---

## Step 4.2: Update root justfile to import portable modules

**Objective**: Replace extracted recipes with import statement(s) and verify all recipes work.

**Prerequisites**:
- Step 4.1 complete (portable module(s) exist)
- Read `justfile` (current state)

**Implementation**:
1. Add import statement at top of `justfile`:
   `import 'plugin/portable.just'`
2. Add `set allow-duplicate-recipes` for intentional recipe overrides
3. Remove recipes that moved to portable module(s):
   - `claude`, `claude0`, `lint`, `format`, `check`, `red-lint`, `precommit-base`, `test`, `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge`
4. Keep in root justfile:
   - `release` (project-specific)
   - `line-limits` (project-specific)
   - `bash_prolog` for project-specific helper functions
   - `precommit` (may need project-specific additions beyond base)
   - Project-specific worktree helpers
5. Generate or regenerate cached help files (these may not exist yet):
   - `just --list > .cache/just-help.txt` (create `.cache/` directory first if needed)
   - `.cache/just-help-edify-plugin.txt` — generate only if referenced by plugin hooks or skills

**Expected Outcome**:
- Root `justfile` imports portable module(s)
- Extracted recipes removed from root (no duplication unless `allow-duplicate-recipes` for intentional overrides)
- All recipes functional

**Error Conditions**:
- If `just claude` fails → check import path, portable module syntax
- If recipe override doesn't work → verify `set allow-duplicate-recipes` or restructure imports
- If `just --list` missing recipes → check import path resolution

**Validation**:
- `just --list` shows both imported and project-specific recipes
- `just lint` works (imported recipe)
- `just release --help` works (project-specific recipe, if exists)
- `just precommit` passes (end-to-end validation)
- `.cache/just-help.txt` exists and matches `just --list` output
