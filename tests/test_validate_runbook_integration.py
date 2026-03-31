"""Integration tests for validate-runbook.py."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "validate-runbook.py"

_spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
main = _mod.main


# Minimal valid phase file content for directory input tests.
_PHASE_1_CONTENT = """\
# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: scaffold

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_dir_foo`

**Expected failure:** `ImportError`

**Verify RED:** `pytest tests/test_dir.py::test_dir_foo -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/dirmod.py`
  Action: Create

**Verify GREEN:** `pytest tests/test_dir.py::test_dir_foo -v`

---
"""

_PHASE_2_CONTENT = """\
# Phase 2: Extension (type: tdd)

---

## Cycle 2.1: extend

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_dir_bar`

**Verify RED:** `pytest tests/test_dir.py::test_dir_bar -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/dirmod.py`
  Action: Modify

**Verify GREEN:** `pytest tests/test_dir.py::test_dir_bar -v`

**Checkpoint:** All 2 tests pass.

---
"""

# Edge case fixtures: interim checkpoints and workflow decision files.

_VALID_INTERIM_CHECKPOINTS = """\
---
title: Multi-Phase Runbook with Interim Checkpoints
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: first test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_alpha`

**Verify RED:** `pytest tests/test_example.py::test_alpha -v`

---

## Cycle 1.2: second test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_beta`

**Verify RED:** `pytest tests/test_example.py::test_beta -v`

**Checkpoint:** All 2 tests pass.

---

# Phase 2: Extension (type: tdd)

---

## Cycle 2.1: third test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_gamma`

**Verify RED:** `pytest tests/test_example.py::test_gamma -v`

---

## Cycle 2.2: fourth test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_delta`

**Verify RED:** `pytest tests/test_example.py::test_delta -v`

**Checkpoint:** All 4 tests pass.

---
"""

_VIOLATION_INTERIM_CHECKPOINT = """\
---
title: Wrong Interim Checkpoint Count
---

# Phase 1: Core module (type: tdd)

---

## Cycle 1.1: first test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_alpha`

**Verify RED:** `pytest tests/test_example.py::test_alpha -v`

---

## Cycle 1.2: second test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_beta`

**Verify RED:** `pytest tests/test_example.py::test_beta -v`

**Checkpoint:** All 3 tests pass.

---

# Phase 2: Extension (type: tdd)

---

## Cycle 2.1: third test

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_gamma`

**Verify RED:** `pytest tests/test_example.py::test_gamma -v`

**Checkpoint:** All 3 tests pass.

---
"""

_VIOLATION_MODEL_TAGS_WORKFLOW = """\
---
title: Workflow Decision Violation Runbook
---

# Phase 1: Workflow updates (type: general)

---

## Cycle 1.1: update workflow decisions

**Execution Model**: Sonnet

**GREEN Phase:**

**Changes:**
- File: `agents/decisions/workflow-core.md`
  Action: Modify

---
"""


def test_integration_directory_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Directory input: exits 0, report written inside directory."""
    monkeypatch.chdir(tmp_path)
    runbook_dir = tmp_path / "my-runbook"
    runbook_dir.mkdir()
    (runbook_dir / "runbook-phase-1.md").write_text(_PHASE_1_CONTENT)
    (runbook_dir / "runbook-phase-2.md").write_text(_PHASE_2_CONTENT)

    monkeypatch.setattr(
        sys, "argv", ["validate-runbook", "model-tags", str(runbook_dir)]
    )
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = runbook_dir / "reports" / "validation-model-tags.md"
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


@pytest.mark.parametrize(
    ("subcommand", "skip_flag"),
    [
        ("model-tags", "--skip-model-tags"),
        ("lifecycle", "--skip-lifecycle"),
        ("test-counts", "--skip-test-counts"),
        ("red-plausibility", "--skip-red-plausibility"),
    ],
)
def test_integration_skip_flag(
    subcommand: str,
    skip_flag: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skip flag: exits 0, SKIPPED report written."""
    monkeypatch.chdir(tmp_path)
    runbook_dir = tmp_path / "skip-runbook"
    runbook_dir.mkdir()
    (runbook_dir / "runbook-phase-1.md").write_text(_PHASE_1_CONTENT)
    (runbook_dir / "runbook-phase-2.md").write_text(_PHASE_2_CONTENT)

    monkeypatch.setattr(
        sys,
        "argv",
        ["validate-runbook", subcommand, skip_flag, str(runbook_dir)],
    )
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = runbook_dir / "reports" / f"validation-{subcommand}.md"
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** SKIPPED" in content


def test_test_counts_interim_checkpoints_valid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Interim checkpoints with correct cumulative counts exit 0."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "interim-valid.md"
    runbook.write_text(_VALID_INTERIM_CHECKPOINTS)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "test-counts", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = (
        tmp_path / "plans" / "interim-valid" / "reports" / "validation-test-counts.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


def test_test_counts_interim_checkpoint_wrong(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Interim checkpoint claiming wrong count exits 1."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "interim-wrong.md"
    runbook.write_text(_VIOLATION_INTERIM_CHECKPOINT)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "test-counts", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 1

    report_path = (
        tmp_path / "plans" / "interim-wrong" / "reports" / "validation-test-counts.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** FAIL" in content
    # Phase 1 checkpoint claims 3 but only 2 tests seen so far
    assert "3" in content
    assert "2" in content


def test_model_tags_workflow_decision_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Workflow decision file with non-opus model triggers violation."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "workflow-violation.md"
    runbook.write_text(_VIOLATION_MODEL_TAGS_WORKFLOW)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "model-tags", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 1

    report_path = (
        tmp_path
        / "plans"
        / "workflow-violation"
        / "reports"
        / "validation-model-tags.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** FAIL" in content
    assert "agents/decisions/workflow-core.md" in content
    assert "**Expected:** opus" in content
