"""Tests for validate-runbook.py CLI scaffold."""

import importlib.util
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.fixtures.validate_runbook_fixtures import (
    AMBIGUOUS_RED_PLAUSIBILITY,
    LIFECYCLE_KNOWN_FILE,
    NON_MARKDOWN_ARTIFACT,
    VALID_TDD,
    VALID_VERIFY_GREEN_PATHS,
    VIOLATION_LIFECYCLE_DUPLICATE_CREATE,
    VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE,
    VIOLATION_MODEL_TAGS,
    VIOLATION_RED_IMPLAUSIBLE,
    VIOLATION_TEST_COUNTS,
    VIOLATION_TEST_COUNTS_PARAMETRIZED,
    VIOLATION_VERIFY_GREEN_PATHS,
)

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "validate-runbook.py"

_spec = importlib.util.spec_from_file_location("validate_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
main = _mod.main


_RunValidateFn = Callable[[str, str, str], tuple[int, str]]


def _invoke_and_collect(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    subcmd: str,
    name: str,
    argv: list[str],
) -> tuple[int, str]:
    """Invoke main() with argv, return (exit_code, report_content)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", argv)
    try:
        main()
        code = 0
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
    report = tmp_path / "plans" / name / "reports" / f"validation-{subcmd}.md"
    return code, report.read_text() if report.exists() else ""


@pytest.fixture
def run_validate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> _RunValidateFn:
    """Fixture returning a callable to run validate-runbook subcommands."""

    def _run(subcmd: str, name: str, text: str) -> tuple[int, str]:
        runbook = tmp_path / f"{name}.md"
        runbook.write_text(text)
        argv = ["validate-runbook", subcmd, str(runbook)]
        return _invoke_and_collect(monkeypatch, tmp_path, subcmd, name, argv)

    return _run


@pytest.fixture
def run_validate_with_args(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Callable[[str, str, str, list[str]], tuple[int, str]]:
    """Like run_validate but accepts extra CLI args."""

    def _run(
        subcmd: str, name: str, text: str, extra_args: list[str]
    ) -> tuple[int, str]:
        runbook = tmp_path / f"{name}.md"
        runbook.write_text(text)
        argv = ["validate-runbook", subcmd, str(runbook), *extra_args]
        return _invoke_and_collect(monkeypatch, tmp_path, subcmd, name, argv)

    return _run


def test_model_tags_happy_path(run_validate: _RunValidateFn) -> None:
    """Model-tags on valid runbook exits 0 with PASS report."""
    code, content = run_validate("model-tags", "valid", VALID_TDD)
    assert code == 0
    assert "**Result:** PASS" in content
    assert "Failed: 0" in content


def test_model_tags_violation(run_validate: _RunValidateFn) -> None:
    """Non-opus artifact file triggers exit 1 and FAIL report."""
    code, content = run_validate("model-tags", "violation", VIOLATION_MODEL_TAGS)
    assert code == 1
    assert "**Result:** FAIL" in content
    assert "agent-core/skills/myskill/SKILL.md" in content
    assert "**Expected:** opus" in content


def test_lifecycle_modify_before_create(run_validate: _RunValidateFn) -> None:
    """Lifecycle: modify-before-create exits 1 with FAIL report."""
    code, content = run_validate(
        "lifecycle",
        "lc-violation",
        VIOLATION_LIFECYCLE_MODIFY_BEFORE_CREATE,
    )
    assert code == 1
    assert "**Result:** FAIL" in content
    assert "src/widget.py" in content
    assert "no prior creation found" in content


def test_lifecycle_happy_path(run_validate: _RunValidateFn) -> None:
    """Lifecycle on valid runbook exits 0 with PASS report."""
    code, content = run_validate("lifecycle", "valid-lc", VALID_TDD)
    assert code == 0
    assert "**Result:** PASS" in content


def test_lifecycle_duplicate_creation(run_validate: _RunValidateFn) -> None:
    """Lifecycle: duplicate creation exits 1 with FAIL report."""
    code, content = run_validate(
        "lifecycle",
        "dup-create",
        VIOLATION_LIFECYCLE_DUPLICATE_CREATE,
    )
    assert code == 1
    assert "**Result:** FAIL" in content
    assert "src/module.py" in content


def test_test_counts_happy_path(run_validate: _RunValidateFn) -> None:
    """Test-counts on valid fixture exits 0 with PASS report."""
    code, content = run_validate("test-counts", "valid-tc", VALID_TDD)
    assert code == 0
    assert "**Result:** PASS" in content


def test_test_counts_mismatch(run_validate: _RunValidateFn) -> None:
    """Test-counts mismatch exits 1 with FAIL report."""
    code, content = run_validate("test-counts", "tc-violation", VIOLATION_TEST_COUNTS)
    assert code == 1
    assert "**Result:** FAIL" in content
    assert "test_alpha" in content
    assert "test_beta" in content
    assert "test_gamma" in content


def test_test_counts_parametrized(run_validate: _RunValidateFn) -> None:
    """Parametrized test names test_foo[p1]/[p2] count as 1 unique test."""
    code, content = run_validate(
        "test-counts",
        "param-tc",
        VIOLATION_TEST_COUNTS_PARAMETRIZED,
    )
    assert code == 0
    assert "**Result:** PASS" in content


def test_red_plausibility_happy_path(run_validate: _RunValidateFn) -> None:
    """Red-plausibility on valid fixture exits 0 with PASS report."""
    code, content = run_validate("red-plausibility", "valid-rp", VALID_TDD)
    assert code == 0
    assert "**Result:** PASS" in content
    assert "Ambiguous: 0" in content


def test_red_plausibility_violation(run_validate: _RunValidateFn) -> None:
    """Red-plausibility: created in prior GREEN causes exit 1 FAIL."""
    code, content = run_validate(
        "red-plausibility",
        "rp-violation",
        VIOLATION_RED_IMPLAUSIBLE,
    )
    assert code == 1
    assert "**Result:** FAIL" in content
    assert "widget" in content
    assert "Ambiguous: 0" in content


def test_red_plausibility_ambiguous(run_validate: _RunValidateFn) -> None:
    """Red-plausibility: exists but tests different behavior → exit 2."""
    code, content = run_validate(
        "red-plausibility",
        "rp-ambiguous",
        AMBIGUOUS_RED_PLAUSIBILITY,
    )
    assert code == 2
    assert "**Result:** AMBIGUOUS" in content
    assert "## Ambiguous" in content
    assert "Ambiguous: 1" in content


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


def test_lifecycle_known_files_not_flagged() -> None:
    """Pre-existing files in known_files skip modify-before-create violation."""
    violations = _mod.check_lifecycle(
        LIFECYCLE_KNOWN_FILE, "known-file.md", known_files={"src/existing.py"}
    )
    assert violations == [], f"Known file should not be flagged: {violations}"


def test_lifecycle_unknown_file_still_flagged() -> None:
    """Files NOT in known_files with modify-first are still flagged."""
    violations = _mod.check_lifecycle(
        LIFECYCLE_KNOWN_FILE, "unknown-file.md", known_files=set()
    )
    assert len(violations) == 1, f"Unknown file should be flagged: {violations}"
    assert "src/existing.py" in violations[0]
    assert "no prior creation found" in violations[0]


def test_model_tags_non_markdown_artifact_not_flagged(
    run_validate: _RunValidateFn,
) -> None:
    """Non-.md files under artifact paths are not flagged by model-tags."""
    code, content = run_validate("model-tags", "script-runbook", NON_MARKDOWN_ARTIFACT)
    assert code == 0, "Non-.md file under artifact path should not be flagged"
    assert "**Result:** PASS" in content


def test_verify_green_paths_violation(run_validate: _RunValidateFn) -> None:
    """Verify-green-paths flags specific pytest paths in Verify GREEN lines."""
    code, content = run_validate(
        "verify-green-paths", "specific-paths", VIOLATION_VERIFY_GREEN_PATHS
    )
    assert code == 1, "Specific pytest path in Verify GREEN should be flagged"
    assert "**Result:** FAIL" in content
    assert "tests/test_example.py" in content


def test_verify_green_paths_happy_path(run_validate: _RunValidateFn) -> None:
    """Verify-green-paths passes when Verify GREEN uses universal recipe."""
    code, content = run_validate(
        "verify-green-paths", "universal-recipe", VALID_VERIFY_GREEN_PATHS
    )
    assert code == 0, "Universal recipe in Verify GREEN should pass"
    assert "**Result:** PASS" in content


def test_lifecycle_known_file_cli(
    run_validate_with_args: Callable[[str, str, str, list[str]], tuple[int, str]],
) -> None:
    """CLI --known-file argument wires through to check_lifecycle."""
    code, content = run_validate_with_args(
        "lifecycle",
        "cli-known",
        LIFECYCLE_KNOWN_FILE,
        ["--known-file", "src/existing.py"],
    )
    assert code == 0, "Known file via CLI should not be flagged"
    assert "**Result:** PASS" in content
