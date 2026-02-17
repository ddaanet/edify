"""Tests for validate-runbook.py CLI scaffold."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "validate-runbook.py"

_spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
main = _mod.main

VIOLATION_MODEL_TAGS = """\
---
title: Violation Runbook
---

# Phase 1: Skills setup (type: tdd)

---

## Cycle 1.1: add skill

**Execution Model**: Haiku

**GREEN Phase:**

**Changes:**
- File: `agent-core/skills/myskill/SKILL.md`
  Action: Create

---
"""

VALID_TDD = """\
---
title: Example Runbook
---

# Phase 1: Core module (type: tdd)

**Target files:**
- `src/module.py` (new)

---

## Cycle 1.1: scaffold

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_foo`

Expects `ImportError` on `src.module`.

**Expected failure:** `ImportError`

**Verify RED:** `pytest tests/test_example.py::test_foo -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/module.py`
  Action: Create

**Verify GREEN:** `pytest tests/test_example.py::test_foo -v`

---

## Cycle 1.2: extend

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_bar`

**Verify RED:** `pytest tests/test_example.py::test_bar -v`

---

**GREEN Phase:**

**Changes:**
- File: `src/module.py`
  Action: Modify

**Verify GREEN:** `pytest tests/test_example.py::test_bar -v`

**Checkpoint:** All 1 tests pass.

---
"""


def test_model_tags_happy_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Model-tags on a valid runbook exits 0 and writes a PASS report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "my-runbook.md"
    runbook.write_text(VALID_TDD)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "model-tags", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = (
        tmp_path / "plans" / "my-runbook" / "reports" / "validation-model-tags.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


def test_model_tags_violation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-opus artifact file triggers exit 1 and FAIL report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "violation-runbook.md"
    runbook.write_text(VIOLATION_MODEL_TAGS)

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
        / "violation-runbook"
        / "reports"
        / "validation-model-tags.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** FAIL" in content
    assert "agent-core/skills/myskill/SKILL.md" in content
    assert "haiku" in content.lower()
    assert "**Expected:** opus" in content
    assert "Failed: 1" in content


def test_scaffold_cli() -> None:
    """Script exposes four subcommands and exits 1 when invoked without one."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for subcommand in ("model-tags", "lifecycle", "test-counts", "red-plausibility"):
        assert subcommand in result.stdout

    result_no_args = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result_no_args.returncode == 1
