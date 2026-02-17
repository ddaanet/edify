"""Tests for validate-runbook.py CLI scaffold."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

from tests.fixtures.validate_runbook_fixtures import (
    VALID_TDD,
    VIOLATION_LIFECYCLE_DUPLICATE_CREATE,
    VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE,
    VIOLATION_MODEL_TAGS,
    VIOLATION_TEST_COUNTS,
    VIOLATION_TEST_COUNTS_PARAMETRIZED,
)

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "validate-runbook.py"

_spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
main = _mod.main


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


def test_lifecycle_modify_before_create(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lifecycle: modify-before-create exits 1 with FAIL report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "lifecycle-violation.md"
    runbook.write_text(VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "lifecycle", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 1

    report_path = (
        tmp_path
        / "plans"
        / "lifecycle-violation"
        / "reports"
        / "validation-lifecycle.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** FAIL" in content
    assert "src/widget.py" in content
    assert "Cycle 1.1" in content
    assert "no prior creation found" in content
    assert "Failed: 1" in content


def test_lifecycle_happy_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lifecycle on valid runbook exits 0 and writes a PASS report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "valid-tdd.md"
    runbook.write_text(VALID_TDD)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "lifecycle", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = (
        tmp_path / "plans" / "valid-tdd" / "reports" / "validation-lifecycle.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


def test_lifecycle_duplicate_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Lifecycle: duplicate creation exits 1 with FAIL report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "dup-create.md"
    runbook.write_text(VIOLATION_LIFECYCLE_DUPLICATE_CREATE)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "lifecycle", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 1

    report_path = (
        tmp_path / "plans" / "dup-create" / "reports" / "validation-lifecycle.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** FAIL" in content
    assert "src/module.py" in content
    assert "Cycle 1.1" in content
    assert "Cycle 2.1" in content
    assert "Failed: 1" in content


def test_test_counts_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test-counts on VALID_TDD fixture exits 0 and writes PASS report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "valid-tdd.md"
    runbook.write_text(VALID_TDD)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "test-counts", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = (
        tmp_path / "plans" / "valid-tdd" / "reports" / "validation-test-counts.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


def test_test_counts_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test-counts on VIOLATION_TEST_COUNTS exits 1 with FAIL report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "test-counts-violation.md"
    runbook.write_text(VIOLATION_TEST_COUNTS)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "test-counts", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 1

    report_path = (
        tmp_path
        / "plans"
        / "test-counts-violation"
        / "reports"
        / "validation-test-counts.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** FAIL" in content
    assert "5" in content
    assert "3" in content
    assert "test_alpha" in content
    assert "test_beta" in content
    assert "test_gamma" in content
    assert "Failed: 1" in content


def test_test_counts_parametrized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Parametrized test names test_foo[p1]/[p2] count as 1 unique test."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "parametrized-runbook.md"
    runbook.write_text(VIOLATION_TEST_COUNTS_PARAMETRIZED)

    monkeypatch.setattr(sys, "argv", ["validate-runbook", "test-counts", str(runbook)])
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = (
        tmp_path
        / "plans"
        / "parametrized-runbook"
        / "reports"
        / "validation-test-counts.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


def test_red_plausibility_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Red-plausibility on VALID_TDD exits 0 and writes a PASS report."""
    monkeypatch.chdir(tmp_path)
    runbook = tmp_path / "valid-tdd.md"
    runbook.write_text(VALID_TDD)

    monkeypatch.setattr(
        sys, "argv", ["validate-runbook", "red-plausibility", str(runbook)]
    )
    try:
        main()
        exit_code = 0
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    assert exit_code == 0

    report_path = (
        tmp_path / "plans" / "valid-tdd" / "reports" / "validation-red-plausibility.md"
    )
    assert report_path.exists(), f"Report not found at {report_path}"
    content = report_path.read_text()
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content
    assert "Ambiguous: 0" in content


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
