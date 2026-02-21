# Phase 3: PostToolUse Auto-Format Hook

**Type:** General | **Model:** haiku
**Target:** `agent-core/hooks/posttooluse-autoformat.sh` (new file)

## Prerequisites

- Run `which ruff` and `which docformatter` to verify tool availability before creating script
- Verify `agent-core/hooks/posttooluse-autoformat.sh` does NOT exist yet

## Key Decisions

- D-2: Bash (simple command orchestration, no complex pattern matching)
- D-3: File-specific ruff only (`ruff check --fix-only --quiet` + `ruff format --quiet`), NOT full `just format`
- PostToolUse hook receives Write|Edit events with `tool_input.file_path`
- Non-fatal: script always exits 0; formatting errors go to stderr, do not block the write
- D-1: Command hook type

## Completion Validation

Success criteria:
- `agent-core/hooks/posttooluse-autoformat.sh` exists with execute permissions
- All Step 3.2 validation checks pass
- Script handles non-.py, empty input, and missing tool gracefully
- `pytest tests/ -v` → all existing tests still pass (no regression)
