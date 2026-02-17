# Phase 5: Integration — directory input and `--skip` flags (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phases 1–4 (all 4 subcommands implemented — integration exercises them together)

**Consolidation:** Originally 2 cycles (directory input + skip flags); merged since both are same-module argparse additions testable via single parametrized test.

---

## Cycle 5.1: directory input + `--skip` flags — assembled phase files run all checks; skip flags bypass checks

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand current `assemble_phase_files` usage and subcommand dispatch from Phases 1–4.

**RED Phase:**

**Test:** `test_integration_directory_input` (and parametrized variants for skip flags — see below)

**Assertions:**

*Directory input (test_integration_directory_input):*
- Create `tmp_path` directory with `runbook-phase-1.md` and `runbook-phase-2.md` files (minimal valid TDD content)
- Create `tmp_path/reports/` directory (or allow script to create it)
- Running `model-tags <directory>` exits with code 0
- Report written to `<directory>/reports/validation-model-tags.md`
- Report contains `**Result:** PASS`

*Skip flags (test_integration_skip_flag[skip_model_tags], etc. — 4 parametrized cases):*
- Create fixture directory with valid phase files
- Running `model-tags --skip-model-tags <path>` exits with code 0 without running the check
- Report not written (or written with skipped status)
- Parametrized over: `--skip-model-tags`, `--skip-lifecycle`, `--skip-test-counts`, `--skip-red-plausibility`

**Expected failure:** `AssertionError` — `assemble_phase_files` not yet wired for directory input in current handlers (each handler takes a path but may not handle directory case), and `--skip-*` flags not yet added to argparse.

**Why it fails:** Directory detection logic and skip-flag argparse additions not yet implemented.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_integration_directory_input tests/test_validate_runbook.py::test_integration_skip_flag -v`

---

**GREEN Phase:**

**Implementation:** Add directory input handling to all subcommand handlers and `--skip-*` flags to argparse.

**Behavior:**

*Directory input:*
- Each subcommand handler: if `Path(args.path).is_dir()` → call `assemble_phase_files(Path(args.path))` to get content; derive `<job>` as directory name
- Report path: `Path(args.path) / "reports" / f"validation-{subcommand}.md"`
- `assemble_phase_files` already imported from prepare-runbook.py via importlib in Cycle 1.1

*Skip flags:*
- Add `--skip-model-tags`, `--skip-lifecycle`, `--skip-test-counts`, `--skip-red-plausibility` to each respective subcommand's argparse parser (or to the top-level parser for omnibus invocation)
- When skip flag is set: write SKIP report (`**Result:** SKIPPED`), exit 0
- Skip is per-subcommand: `model-tags --skip-model-tags` skips the model-tags check; other subcommands unaffected

**Approach:** Add `parser_model_tags.add_argument('--skip-model-tags', action='store_true')` etc. In each handler: `if args.skip_model_tags: write_report(..., skipped=True); sys.exit(0)`. Extend `write_report` to accept `skipped=True` keyword that writes `**Result:** SKIPPED` with empty violations.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `is_dir()` branching and `assemble_phase_files` call to all 4 handlers; add `--skip-*` argument to each subparser; extend `write_report` with `skipped` parameter
  Location hint: Each subcommand handler function + argparse setup block

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_integration_directory_input tests/test_validate_runbook.py::test_integration_skip_flag -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Final Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.
