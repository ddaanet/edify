# Phase 1: Script infrastructure + `model-tags` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (new)
- `tests/test_validate_runbook.py` (new)

**Dependency:** Cycles 1.2–1.3 depend on Cycle 1.1 (importlib block, report writer, argparse scaffold).

**D-7 import:** All cycles use `importlib.util.spec_from_file_location("prepare_runbook", Path(__file__).parent / "prepare-runbook.py")` to import `parse_frontmatter`, `extract_cycles`, `extract_sections`, `assemble_phase_files`, `extract_file_references`, `extract_step_metadata`.

---

## Cycle 1.1: Script scaffold — argparse, importlib, report writer, exit codes

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_scaffold_cli`
**Assertions:**
- Running script with `--help` exits with code 0
- Stdout contains all four subcommand names: `model-tags`, `lifecycle`, `test-counts`, `red-plausibility`
- Running script with no subcommand exits with code 1

**Expected failure:** `subprocess.CalledProcessError` or `FileNotFoundError` — script does not exist.

**Why it fails:** `agent-core/bin/validate-runbook.py` does not exist yet.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_scaffold_cli -v`

---

**GREEN Phase:**

**Implementation:** Create `agent-core/bin/validate-runbook.py` with argparse structure, importlib import block, report writer function, and exit-code conventions.

**Behavior:**
- Shebang `#!/usr/bin/env python3` and `if __name__ == '__main__':` guard
- Argparse with 4 subcommands: `model-tags`, `lifecycle`, `test-counts`, `red-plausibility`; each accepts a `path` positional argument
- Missing subcommand → print usage to stderr, exit 1
- Importlib block loads `prepare-runbook.py` from same directory: `parse_frontmatter`, `extract_cycles`, `extract_sections`, `assemble_phase_files`, `extract_file_references`, `extract_step_metadata`
- `write_report(subcommand, path, violations, ambiguous=None)` writes report to `plans/<job>/reports/validation-{subcommand}.md`; `<job>` is `Path(path).parent.name` (directory case) or `Path(path).stem` (single-file case)
- Subcommand handlers are stubs (pass-through to `sys.exit(0)`) after scaffold

**Approach:** Pure argparse (not click). `add_subparsers(dest='subcommand', required=True)` causes exit 2 on missing subcommand — override to exit 1 via error handler or check `args.subcommand is None`. Report directory is created with `mkdir(parents=True, exist_ok=True)`.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Create file with shebang, imports, importlib block, `write_report` function, argparse setup, stub subcommand handlers, `main()`, `if __name__ == '__main__':` guard
  Location hint: New file (~45 lines)

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_scaffold_cli -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 1.2: model-tags — happy path (no violations, exit 0, report written)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` lines 1–50 — understand importlib setup and `write_report` signature established in Cycle 1.1.

**RED Phase:**

**Test:** `test_model_tags_happy_path`
**Assertions:**
- Running `model-tags` on a fixture with no artifact-type file references exits with code 0
- Report file exists at expected path
- Report contains `**Result:** PASS`
- Report `Summary` section contains `Failed: 0`

**Fixture:** `VALID_TDD` — valid TDD runbook with non-architectural file references and sonnet model tag.

**Expected failure:** `AssertionError` — `model-tags` handler is still a stub (exit 0 without writing report), or `FileNotFoundError` if report not written.

**Why it fails:** `model-tags` handler has no logic; report not written.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_model_tags_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_model_tags(content, path)` function and wire to `model-tags` subcommand handler.

**Behavior:**
- Reads runbook: if `path` is a directory, call `assemble_phase_files(path)` to get content; if file, read directly
- For each cycle/step in content: extract `**Execution Model**:` using `extract_step_metadata(step_content)`; extract `File:` references from `**Changes:**` section via regex `r'- File: `?([^`\n]+)`?'`
- Artifact-type paths requiring opus: `agent-core/skills/`, `agent-core/fragments/`, `agent-core/agents/`, and files matching `agents/decisions/workflow-*.md`
- No violations → write PASS report, exit 0

**Approach:** Iterate extracted cycles from `extract_cycles(content)`. For each cycle, get its text block. Extract model with `extract_step_metadata`. Find File references with `re.findall`. Check each file path against ARTIFACT_PREFIXES. No violation if model is `opus` or file is not an artifact type.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `ARTIFACT_PREFIXES` constant and `check_model_tags(content, path)` function; wire to `model-tags` handler in `main()`
  Location hint: After importlib block, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_model_tags_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

## Cycle 1.3: model-tags — violation detection (skill/fragment/agent file with non-opus tag, exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand `check_model_tags` return type (list of violation dicts) from Cycle 1.2.

**RED Phase:**

**Test:** `test_model_tags_violation`
**Assertions:**
- Running `model-tags` on `VIOLATION_MODEL_TAGS` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section names the artifact-type file path and current model (`haiku`)
- Report contains `**Expected:** opus`
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_MODEL_TAGS` — cycle with `File: agent-core/skills/myskill/SKILL.md` in Changes and `**Execution Model**: Haiku`.

**Expected failure:** `AssertionError` — current implementation from 1.2 detects no violations (logic present but violation branch not triggered, or returns exit 0 for all inputs).

**Why it fails:** The 1.2 GREEN may check artifact paths but not correctly flag non-opus models, or ARTIFACT_PREFIXES not matching correctly.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_model_tags_violation -v`

---

**GREEN Phase:**

**Implementation:** Complete violation detection in `check_model_tags`.

**Behavior:**
- When artifact-type file found and model is not `opus`: append violation dict with `file`, `current_model`, `expected_model="opus"`, `location` (cycle/step identifier)
- `write_report` formats violation dicts into Violations section per report format spec
- Non-empty violations list → write FAIL report, exit 1

**Approach:** The violation condition is `file_matches_artifact_prefix AND model_lower != 'opus'`. `workflow-*.md` requires `fnmatch.fnmatch(path, 'agents/decisions/workflow-*.md')` or glob-style check. Exit code: `sys.exit(0)` if no violations, `sys.exit(1)` if violations.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Complete violation detection in `check_model_tags`; update `write_report` to format violation dicts; update handler to call `sys.exit(1)` on violations
  Location hint: Inside `check_model_tags` and `write_report` functions

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_model_tags_violation -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.
