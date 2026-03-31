# SP-2 Verification — Remaining `claudeutils` References

## Summary

SP-2 (package rename `claudeutils` → `edify`) is ready for execution. Only 2 stragglers remain in pyproject.toml (GitHub repo URLs, intentionally deferred per design). Source code, tests, plugin files, and documentation are clean.

## Verification Results

### 1. Full-Tree Grep (Extensionless)

Search: `grep -r 'claudeutils' . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=scratch --exclude-dir=.mypy_cache --exclude-dir=list --exclude='package-lock.json' --exclude='uv.lock'`

**Scope:** All files except .git, build artifacts, caches, venv, scratch, and generated lockfiles.

**Results:**
- Total matches outside plan/tmp: **3**
- Expected (plan self-references): 1 (agents/session.md context note)
- Stragglers: **2** (pyproject.toml URLs)

### 2. Import Consistency Check

#### `from claudeutils.*` in source code
Command: `grep -r 'from claudeutils\.' src/ tests/ --include='*.py'`
Result: **0** ✓ CLEAN

#### `import claudeutils` in source code
Command: `grep -r 'import claudeutils' src/ tests/ --include='*.py'`
Result: **0** ✓ CLEAN

#### Internal imports in edify package
- `src/edify/cli.py` — verified: imports from `edify.*`
- All test files — verified: imports from `edify.*` (or no package imports)

### 3. Plugin Files Check

#### Runtime refs in plugin/ (deferred from SP-1)
Command: `grep -r 'claudeutils' plugin/bin/ plugin/hooks/ --include='*.py' --include='*.sh'`
Result: **0** ✓ CLEAN

**Status:** All runtime refs successfully updated in SP-1. No remaining refs in:
- `plugin/bin/compress-key.py` ✓
- `plugin/bin/when-resolve.py` ✓
- `plugin/bin/prepare-runbook.py` ✓
- `plugin/hooks/userpromptsubmit-shortcuts.py` ✓
- `plugin/hooks/pretooluse-recipe-redirect.py` ✓
- `plugin/hooks/sessionstart-health.sh` ✓

#### .just files check
Command: `grep -r 'claudeutils' plugin/portable.just`
Result: **0** ✓ CLEAN

- `plugin/portable.just` — verified: all `claudeutils validate` → `edify validate`
- `justfile` — verified: no `claudeutils` refs

### 4. Configuration & Protected Files

#### pyproject.toml
Location: `/Users/david/code/claudeutils/pyproject.toml`

- **Line 2:** `name = "edify"` ✓ CORRECT
- **Line 22:** `edify = "edify.cli:main"` ✓ CORRECT
- **Lines 18-19:** GitHub repo URLs still reference `claudeutils` (STRAGGLERS)
  - `Homepage = "https://github.com/ddaanet/claudeutils"`
  - `Repository = "https://github.com/ddaanet/claudeutils"`

**Rationale:** These URLs will be updated when GitHub repos are renamed (SP-2 Phase 3). Keeping them now preserves accurate upstream reference until repo rename is executed.

#### Protected files
- `.claude/settings.json` — verified: contains only `edify` references ✓
- `.envrc` — verified: no package/CLI references ✓

### 5. Documentation & Session Files

#### agents/session.md
- **Intentional reference (line 10):** Context note describing deferred SP-2 work
  - Content: "Submodule files with runtime `claudeutils` refs (3 Python imports, subprocess call, pretooluse error msgs, portable.just validators, sessionstart pip install) — change only when parent package renames in SP-2"
  - Status: Keep as-is (contextual reminder of scope) ✓

#### Plan artifacts
- `plans/edify-rename/*.md` — intentionally self-referential, excluded from scope ✓

### 6. Lockfiles & Generated Content

- `package-lock.json` — excluded (generated, expected to contain old references)
- `uv.lock` — excluded (generated, expected to contain old references)
- `.venv/` — excluded (installed package, expected to contain old references)
- `.mypy_cache/` — excluded (cache, expected to contain old references)

## Stragglers Found

### File: `/Users/david/code/claudeutils/pyproject.toml`

| Line | Content | Status |
|------|---------|--------|
| 18 | `Homepage = "https://github.com/ddaanet/claudeutils"` | STRAGGLER (deferred to repo rename) |
| 19 | `Repository = "https://github.com/ddaanet/claudeutils"` | STRAGGLER (deferred to repo rename) |

**Action:** These URLs should be updated when GitHub repositories are renamed as part of SP-2 Phase 3. They can be updated in-tree now (lines easily edited) OR deferred to the repo rename phase. Current status: intentional defer based on SP-2 design.

## Expected Skips

| Category | Count | Status |
|----------|-------|--------|
| Plan self-references (`plans/edify-rename/`) | 30+ | EXPECTED (scope documentation) |
| Session context notes (`agents/session.md`) | 1 | EXPECTED (deferred scope indicator) |
| Generated lockfiles | 2 | EXPECTED |
| Venv/build artifacts | 3395+ | EXPECTED |
| Scratch/debug files (`tmp/`, `scratch/`) | 50+ | EXPECTED (ephemeral) |

## Overall Verdict

**CLEAN** — Source code, tests, imports, and plugin files are ready for SP-2 execution.

**Stragglers identified:** 2 GitHub URLs in pyproject.toml (intentional defer per design).

**Recommendation:** Proceed with SP-2 execution. The 2 remaining refs are configuration-level URLs that will be updated when GitHub repos are renamed.

## Test Verification

Run before starting SP-2:
```bash
just precommit
```

Expected result: All tests pass (1820/1821 passing, 1 xfail pre-existing).

After SP-2 completion, verify:
```bash
grep -r 'claudeutils' . --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude='package-lock.json' --exclude='uv.lock' | wc -l
# Should be only plan artifacts + session.md context note (~30 lines)
```

## Execution Readiness

- Source code imports: ✓ CLEAN
- Test imports: ✓ CLEAN
- Plugin runtime refs: ✓ CLEAN
- CLI entry point: ✓ CORRECT
- Package name: ✓ CORRECT
- Documentation: ✓ CONSISTENT

**SP-2 ready to proceed.**
