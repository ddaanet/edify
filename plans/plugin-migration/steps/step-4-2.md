# Step 4.2

**Plan**: `plans/plugin-migration/runbook-phase-4.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Extract portable recipes and update root justfile.

**Depends on D-5 redesign:** Current D-5 specifies a single `portable.just`. Thematic modules are the better design — consumers import only what they need. Module boundaries need design work before this phase executes. If D-5 redesign has not occurred by execution time, proceed with single `portable.just` as originally designed.

---

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
