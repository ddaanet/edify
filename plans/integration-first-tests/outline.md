# Integration-First Test Plan: Outline

## Current State

- 939 tests, 117 files
- Worktree tests: already integration-first (real git via `init_repo` fixture) ✓
- CLI tests: Click CliRunner ✓
- Pure Python logic (parsing, discovery, path encoding): unit tests ✓ (appropriate)
- **Violations:** 3 areas mock subprocess in git domains where real git should be used

## Migration Targets

**Tier 1 — Subprocess mocking violations (migrate):**

| File | Mock usage | Target |
|------|-----------|--------|
| `test_learning_ages.py` | `git blame`, `git log` mocked | real git repo fixture |
| `test_learning_ages_integration.py` | `subprocess.run` patched | real git repo fixture |
| `test_validation_tasks.py` | `subprocess.run` for git history | real git repo fixture |

**Tier 2 — Evaluate (may stay mocked):**

| File | Mock usage | Rationale |
|------|-----------|-----------|
| `test_account_keychain.py` | macOS `security` command | External service, side-effecting — mock appropriate |
| `test_statusline_context.py` | subprocess for model info | Investigate: may depend on system state |

**Not migrating:** Pure Python unit tests (parsing, models, paths). These are appropriate at unit layer.

## Approach

**For Tier 1 migrations:** Extend `fixtures_worktree.py` with git repo fixtures that encode the test scenarios as real commits. Replace `@patch("subprocess.run")` with fixture-driven real git output.

**Structure per migration:**
1. `test_learning_ages.py` — Section A (parsing tests) stays unit; Section B+ (age/blame tests) migrated to real git fixture
2. `test_learning_ages_integration.py` — full pipeline tests using real git fixture (possibly merge with test_learning_ages.py into coherent suite)
3. `test_validation_tasks.py` — git history validation via real commits

**Phase approach:**
- Phase 1 (type: tdd): Migrate learning-ages tests — create git fixture, rewrite mocked git tests
- Phase 2 (type: tdd): Migrate validation-tasks tests — create git history fixture, rewrite
- Phase 3 (type: general): Statusline context evaluation + policy doc update in testing.md

## Key Decisions

- **Scope boundary:** Subprocess-domain violations only. Not adding integration coverage to pure-unit-tested Python logic.
- **Fixture strategy:** New `git_learnings_repo` and `git_history_repo` fixtures in `fixtures_worktree.py` (already the fixture home for worktree tests)
- **`test_learning_ages_integration.py`:** Currently misnamed — uses mocked subprocess, not real git. Rename to `test_learning_ages_git.py` or merge back into `test_learning_ages.py` with clear section headers.

## Open Questions

None. Scope is clear.

## Out of Scope

- Adding integration coverage to pure Python logic (parsers, models, path encoding)
- Migrating account/keychain tests (external service, side effects)
- Conformance testing or e2e API tests
