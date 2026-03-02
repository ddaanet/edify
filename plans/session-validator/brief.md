# Brief: Session.md Validator

## Discussion Conclusions (2026-03-02)

### Parsing Consolidation (NFR-4)

Three independent `TASK_PATTERN` regex definitions parse session.md task lines:
- `validation/session_structure.py:11`
- `validation/tasks.py:16`
- `worktree/session.py:30`

Consolidated into `validation/task_parsing.py` — single `TASK_PATTERN` and `ParsedTask` dataclass. All three consumers updated to permissive regex. 25 tests (test-after — see TDD note below).

### Execute Flag Lint Absorbed (FR-7)

Execute-flag-lint task absorbed into session-validator as FR-7: task command semantic validation.

### Task Status Marker Update

Decision from 2026-03-01 (`agents/decisions/operational-tooling.md`):
- `[✗]` → `[†]` (dagger, U+2020) — `✗` visually confusable with `x`
- `[–]` → `[-]` (ASCII hyphen) — `–` (en dash) visually confusable with `-`, and `-` is what humans type

Updated across: 4 source files, 4 test files, `execute-rule.md` fragment, decision file. All existing regexes now permissive.

### Permissive Parse + Section-Aware Validation

**Key design decision:** The parse layer (`task_parsing.py`) matches any single character in checkbox position — `[.]` not `[specific chars]`. Its job is extraction, not validation.

The validation layer uses parse results + section context:
- Lines in task sections (`## In-tree Tasks`, `## Worktree Tasks`) that don't parse at all → error
- Lines that parse but have invalid checkbox (`VALID_CHECKBOXES` set) → error
- Lines that parse but have invalid model tier → error

**Anti-pattern identified:** Current validators silently skip non-matching lines. A typo like `- [] **Task**` or `- Task without formatting` in a task section vanishes from all tooling. Section-aware validation means: inside a task section, every non-blank non-indented line MUST be a valid task line or it's an error.

### TDD Note

Shared parsing module tests are test-after (22/22 passed first run — implementation context was loaded from prior exploration). Remaining validators (FR-1 through FR-7) should delegate to test-driver agent for actual TDD.

## Implementation State

**Completed:**
- `src/claudeutils/validation/task_parsing.py` — shared parsing module with `ParsedTask`, `TASK_PATTERN`, `VALID_CHECKBOXES`, `VALID_MODELS`
- `tests/test_validation_task_parsing.py` — 25 tests
- All consumer regexes updated to permissive `[.]`
- Status markers updated across codebase
- `plans/session-validator/classification.md` — Moderate, production
- `plans/session-validator/recall-artifact.md` — 9 entries

**Remaining (FR coverage):**
- FR-1: Section schema (allowed sections, ordering) — new
- FR-2: Task format extensions (worktree markers, model tier via shared parsing) — partial (name format exists in `tasks.py`)
- FR-3: Reference validity — partial (ref files + tmp/ exists, backtick paths in metadata new)
- FR-4: Worktree marker cross-reference — new
- FR-5: Status line validation (H1 format, bold status) — new
- FR-6: Plan archive coverage — new
- FR-7: Command semantic validation — new
- NFR-2: `--fix` flag — new
- CLI wiring for new validators

**Approach:** Tier 2 inline execution. Section-aware validation pattern. Delegate to test-driver for TDD on remaining FRs.
