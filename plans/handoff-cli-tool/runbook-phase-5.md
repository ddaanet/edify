### Phase 5: Commit parser + vet check (type: tdd, model: sonnet)

Markdown stdin parser (commit-specific format) and scripted vet check.

---

## Cycle 5.1: Parse commit markdown stdin — all sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_commit_input[files]`, `test_parse_commit_input[options]`, `test_parse_commit_input[submodule]`, `test_parse_commit_input[message]`, `test_parse_commit_input_edge_cases`
**File:** `tests/test_session_commit.py`

**Input fixture:**
```markdown
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet
- amend

## Submodule agent-core
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet check
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
```

**Assertions — Files:**
- `result.files == ["src/commit/cli.py", "src/commit/gate.py", "agent-core/fragments/vet-requirement.md"]`

**Assertions — Options:**
- `result.options == {"no-vet", "amend"}`
- Input with unknown option `"foobar"` raises `CommitInputError` with message containing "Unknown option"
- Input without `## Options` → `result.options == set()`

**Assertions — Submodule:**
- `result.submodules` is dict mapping path → message: `{"agent-core": "🤖 Update vet-requirement fragment\n\n- Add scripted gate classification reference"}`
- Multiple `## Submodule <path>` sections each parsed independently
- Blockquote `> ` prefix stripped from message lines

**Assertions — Message:**
- `result.message == "✨ Add commit CLI with scripted vet check\n\n- Structured markdown I/O\n- Submodule-aware commit pipeline"`
- Blockquote `> ` prefix stripped
- `## ` lines within blockquote treated as message body (not section boundaries)
- Missing `## Message` → `CommitInputError`
- Missing `## Files` → `CommitInputError`

**Expected failure:** `ImportError` — no commit parser module

**Why it fails:** No `session/commit/parse.py`

**Verify RED:** `pytest tests/test_session_commit.py -k "parse_commit" -v`

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/parse.py`

**Behavior:**
- `CommitInput` dataclass: `files: list[str]`, `options: set[str]`, `submodules: dict[str, str]`, `message: str`
- `parse_commit_input(text: str) -> CommitInput` — section-based parsing
- Split on `## ` at line start. Known section names: `Files`, `Options`, `Submodule <path>`, `Message`
- `## Message` is always last — everything from `## Message` to EOF is message body
- Blockquote stripping: remove leading `> ` or `>` from each line
- Valid options: `no-vet`, `just-lint`, `amend`. Unknown → raise `CommitInputError`
- `CommitInputError` exception for missing required sections or unknown options

**Approach:** Sequential parsing — find each `## ` boundary, classify section, delegate to section-specific parser. Message section greedily consumes to EOF (safe for `## ` in blockquotes).

**Changes:**
- File: `src/claudeutils/session/commit/parse.py`
  Action: Create with `CommitInput`, `CommitInputError`, `parse_commit_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 5.2: Input validation — clean files check (C-3)

**RED Phase:**

**Test:** `test_validate_files_dirty`, `test_validate_files_clean_error`, `test_validate_files_amend`
**File:** `tests/test_session_commit.py`

Tests use real git repos via `tmp_path`.

**Assertions:**
- `validate_files(files, amend=False)` with all files appearing in `git status --porcelain` → returns normally (no error)
- `validate_files(files, amend=False)` with a clean file (not in `git status --porcelain`) → raises `CleanFileError` with:
  - `clean_files` attribute listing the clean file paths
  - String representation matching exact format: `**Error:** Listed files have no uncommitted changes\n- <path>\n\nSTOP: Do not remove files and retry.`
- `validate_files(files, amend=True)` with a file that's clean in working tree but present in HEAD commit (via `git diff-tree`) → returns normally (amend allows HEAD-committed files)
- `validate_files(files, amend=True)` with a file in neither working tree changes nor HEAD commit → raises `CleanFileError`

**Expected failure:** `ImportError`

**Why it fails:** No validation function

**Verify RED:** `pytest tests/test_session_commit.py::test_validate_files_dirty -v`

---

**GREEN Phase:**

**Implementation:** Add `validate_files()` to `src/claudeutils/session/commit/gate.py`

**Behavior:**
- `CleanFileError` exception with `clean_files: list[str]` attribute
- `validate_files(files: list[str], amend: bool = False) -> None`
- Get dirty files: `_git("status", "--porcelain")` → parse paths (column 3+)
- If amend: also get HEAD files: `_git("diff-tree", "--no-commit-id", "--name-only", "HEAD")`
- For each file in `files`: check presence in dirty set (or HEAD set if amend)
- Collect clean files → raise `CleanFileError` with STOP directive

**Changes:**
- File: `src/claudeutils/session/commit/gate.py`
  Action: Create with `CleanFileError`, `validate_files()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

## Cycle 5.3: Scripted vet check (C-1)

**RED Phase:**

**Test:** `test_vet_check_no_config`, `test_vet_check_pass`, `test_vet_check_unreviewed`, `test_vet_check_stale`
**File:** `tests/test_session_commit.py`

Tests use `tmp_path` with pyproject.toml and plan report directories.

**Assertions:**
- `vet_check(files)` with no `[tool.claudeutils.commit]` section in pyproject.toml → passes (opt-in, returns `VetResult(passed=True)`)
- `vet_check(files)` with `require-review = ["src/**/*.py"]` and file `src/foo.py` in files, with report `plans/bar/reports/vet-review.md` newer than `src/foo.py` → passes
- `vet_check(files)` with matching pattern but no report file → fails with `VetResult(passed=False, reason="unreviewed", unreviewed_files=["src/foo.py"])`
- `vet_check(files)` with report older than newest matching file → fails with `VetResult(passed=False, reason="stale", stale_info=...)`
- Files not matching any pattern are not checked (non-production files pass freely)

**Expected failure:** `ImportError`

**Why it fails:** No vet check function

**Verify RED:** `pytest tests/test_session_commit.py::test_vet_check_no_config -v`

---

**GREEN Phase:**

**Implementation:** Add vet check to `src/claudeutils/session/commit/gate.py`

**Behavior:**
- `VetResult` dataclass: `passed: bool`, `reason: str | None`, `unreviewed_files: list[str]`, `stale_info: str | None`
- `vet_check(files: list[str]) -> VetResult`
- Read `pyproject.toml` (cwd-relative), parse `[tool.claudeutils.commit].require-review` patterns
- No section or no patterns → return `VetResult(passed=True)`
- Match files against patterns using `fnmatch` or `pathlib.PurePath.match`
- For matched files: discover reports in `plans/*/reports/` matching `*vet*` or `*review*` (excluding `tmp/`)
- No reports → unreviewed. Reports exist → check freshness: `mtime` of newest production file vs newest report
- Stale (production newer) → fail with stale info

**Changes:**
- File: `src/claudeutils/session/commit/gate.py`
  Action: Add `VetResult`, `vet_check()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

**Phase 5 Checkpoint:** `just precommit` — parser and vet check tests pass.
