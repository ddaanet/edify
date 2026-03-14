# Cycle 5.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Markdown stdin parser (commit-specific format) and scripted vet check.

---

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
- Missing `## Message` → `CommitInputError` (unless `amend` + `no-edit` in Options)
- Missing `## Files` → `CommitInputError`
- `no-edit` in Options without `amend` → `CommitInputError` with message indicating `no-edit` requires `amend`
- `amend` + `no-edit` without `## Message` → valid (message not required)
- `no-edit` with `## Message` present → `CommitInputError` (contradictory input — no-edit means keep existing message)

**Expected failure:** `ImportError` — no commit parser module

**Why it fails:** No `session/commit.py`

**Verify RED:** `pytest tests/test_session_commit.py -k "parse_commit" -v`

---
