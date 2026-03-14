# Cycle 5.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Markdown stdin parser (commit-specific format) and scripted vet check.

---

---

**GREEN Phase:**

**Implementation:** Add vet check to `src/claudeutils/session/commit_gate.py`

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
- File: `src/claudeutils/session/commit_gate.py`
  Action: Add `VetResult`, `vet_check()`
  Note: Hardcode `agent-core/bin/**`, `agent-core/skills/**/*.sh` patterns (not configurable). Config model for submodule patterns (unified parent config vs per-repo pyproject.toml) deferred to separate plan.

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---

**Phase 5 Checkpoint:** `just precommit` — parser and vet check tests pass.
