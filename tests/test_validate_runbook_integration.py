"""Integration tests for validate-runbook.py: directory input and skip flags."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "validate-runbook.py"

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
