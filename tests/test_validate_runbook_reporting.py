"""Tests for validate-runbook.py report outcomes.

Covers the three outcomes a reader must be able to tell apart: a check that
ran and found nothing (PASS), a check that had no subject matter
(NOT-APPLICABLE), and a check that did not run (SKIPPED).
"""

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from tests.fixtures.validate_runbook_fixtures import VALID_TDD

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "validate-runbook.py"

GENERAL_RUNBOOK = """\
---
title: General Runbook
---

# Phase 1: docs (type: general)

## Step 1.1: Update README

**Execution Model**: Sonnet

**Changes:**
- File: `README.md`
  Action: Modify
"""

CYCLE_BASED = ["model-tags", "lifecycle", "test-counts", "red-plausibility"]


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _run(
    tmp_path: Path, runbook: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, str(runbook)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


def _report(tmp_path: Path, subcommand: str, stem: str) -> str:
    return (
        tmp_path / "plans" / stem / "reports" / f"validation-{subcommand}.md"
    ).read_text()


@pytest.mark.parametrize("subcommand", CYCLE_BASED)
def test_cycle_based_check_is_not_applicable_without_cycles(
    tmp_path: Path, subcommand: str
) -> None:
    """A TDD-only check on a general runbook reports NOT-APPLICABLE, not PASS.

    An empty violation list from a check with no subject matter must not be
    reported as conformance.
    """
    runbook = tmp_path / "general.md"
    runbook.write_text(GENERAL_RUNBOOK)

    result = _run(tmp_path, runbook, subcommand)

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, subcommand, "general")
    assert "**Result:** NOT-APPLICABLE" in report
    assert "**Result:** PASS" not in report
    assert "declares no cycles" in report


@pytest.mark.parametrize("subcommand", CYCLE_BASED)
def test_cycle_based_check_runs_when_cycles_present(
    tmp_path: Path, subcommand: str
) -> None:
    """The same check on a TDD runbook reports a real outcome, never N/A.

    Pairs with the negative above: without this, a bug that always returned
    NOT-APPLICABLE would pass the suite.
    """
    runbook = tmp_path / "tdd.md"
    runbook.write_text(VALID_TDD)

    _run(tmp_path, runbook, subcommand)

    report = _report(tmp_path, subcommand, "tdd")
    assert "NOT-APPLICABLE" not in report


def test_skip_records_reason_and_disclaims_conformance(tmp_path: Path) -> None:
    """A skipped check states why it was skipped and that it did not run."""
    runbook = tmp_path / "tdd.md"
    runbook.write_text(VALID_TDD)

    result = _run(tmp_path, runbook, "model-tags", "--skip-model-tags", "no venv")

    assert result.returncode == 0, result.stderr
    report = _report(tmp_path, "model-tags", "tdd")
    assert "**Result:** SKIPPED" in report
    assert "**Skipped because:** no venv" in report
    assert "did NOT run" in report


def test_skip_without_reason_is_rejected(tmp_path: Path) -> None:
    """The skip flag requires a reason — it is not a bare boolean escape."""
    runbook = tmp_path / "tdd.md"
    runbook.write_text(VALID_TDD)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "model-tags", str(runbook), "--skip-model-tags"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "expected one argument" in result.stderr


def test_no_cycles_reason_is_none_for_non_cycle_check() -> None:
    """A non-cycle check applies to any runbook, so it never reports N/A."""
    mod = _load_module()
    assert mod._no_cycles_reason("verify-green-paths", GENERAL_RUNBOOK) is None
