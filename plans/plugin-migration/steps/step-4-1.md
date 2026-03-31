# Step 4.1

**Plan**: `plans/plugin-migration/runbook-phase-4.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Extract portable recipes and update root justfile.

**Depends on D-5 redesign:** Current D-5 specifies a single `portable.just`. Thematic modules are the better design — consumers import only what they need. Module boundaries need design work before this phase executes. If D-5 redesign has not occurred by execution time, proceed with single `portable.just` as originally designed.

---

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
