"""Tests for verify-red.sh — RED gate script contract."""

import os
import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).parent.parent / "agent-core/skills/orchestrate/scripts/verify-red.sh"
)


def test_script_exists_and_is_executable() -> None:
    """Script must exist and be marked executable."""
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"
    assert os.access(SCRIPT, os.X_OK), f"Script not executable: {SCRIPT}"


def test_verify_red_confirms_failing_test(tmp_path: Path) -> None:
    """Script exits 0 and prints RED CONFIRMED when test fails."""
    test_file = tmp_path / "test_failing.py"
    test_file.write_text("def test_example(): assert False\n")

    result = subprocess.run(
        [str(SCRIPT), str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"Expected exit 0 for failing test, got {result.returncode}\n"
        f"stdout: {result.stdout}"
    )
    assert "RED" in result.stdout or "CONFIRMED" in result.stdout, (
        f"Expected 'RED' or 'CONFIRMED' in stdout, got: {result.stdout!r}"
    )


def test_verify_red_rejects_passing_test(tmp_path: Path) -> None:
    """Script exits 1 and indicates rejection when test passes."""
    test_file = tmp_path / "test_passing.py"
    test_file.write_text("def test_example(): assert True\n")

    result = subprocess.run(
        [str(SCRIPT), str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1, (
        f"Expected exit 1 for passing test, got {result.returncode}\n"
        f"stdout: {result.stdout}"
    )
    assert any(word in result.stdout for word in ("FAIL", "REJECTED", "passed")), (
        f"Expected failure indication in stdout, got: {result.stdout!r}"
    )


def test_verify_red_rejects_missing_test_file(tmp_path: Path) -> None:
    """Script exits 1 with error message when test file does not exist."""
    nonexistent = tmp_path / "nonexistent_test.py"

    result = subprocess.run(
        [str(SCRIPT), str(nonexistent)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1, (
        f"Expected exit 1 for missing file, got {result.returncode}\n"
        f"stdout: {result.stdout}"
    )
    assert result.stdout.strip(), "Expected error message in stdout, got empty output"
