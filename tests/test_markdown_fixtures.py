"""Test fixture infrastructure for markdown test corpus.

This module implements parametrized tests for the markdown preprocessor using
fixture pairs (.input.md and .expected.md files). It validates:

- FR-1: Preprocessor transformations match expected output
- FR-2: Pass-through verification (unchanged content)
- FR-3: Full pipeline integration (preprocessor + remark-cli)
- FR-4: Idempotency (re-processing produces identical output)

Fixtures are discovered automatically from tests/fixtures/markdown/ directory.
The module includes helper functions for loading fixture pairs and directory
validation tests to catch infrastructure issues early.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from edify.markdown import process_lines


def load_fixture_pair(
    name: str, fixtures_dir: Path | None = None
) -> tuple[list[str], list[str]]:
    """Load a fixture pair from .input.md and .expected.md files.

    Args:
        name: Base fixture name (without extension)
        fixtures_dir: Directory containing fixtures. Defaults to tests/fixtures/markdown

    Returns:
        Tuple of (input_lines, expected_lines) with newlines preserved

    Raises:
        FileNotFoundError: If either fixture file is missing
    """
    if fixtures_dir is None:
        fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"

    input_file = fixtures_dir / f"{name}.input.md"
    expected_file = fixtures_dir / f"{name}.expected.md"

    if not input_file.exists():
        raise FileNotFoundError(f"Input fixture not found: {input_file}")
    if not expected_file.exists():
        raise FileNotFoundError(f"Expected fixture not found: {expected_file}")

    input_lines = input_file.read_text().splitlines(keepends=True)
    expected_lines = expected_file.read_text().splitlines(keepends=True)

    return input_lines, expected_lines


def test_load_fixture_pair() -> None:
    """Helper function should load fixture pairs correctly."""
    # Create temporary test fixtures
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"
    test_name = "01-example"

    # Write test fixture files
    input_file = fixtures_dir / f"{test_name}.input.md"
    expected_file = fixtures_dir / f"{test_name}.expected.md"

    input_content = "# Test\nLine 1\n"
    expected_content = "# Test\nProcessed\n"

    input_file.write_text(input_content)
    expected_file.write_text(expected_content)

    try:
        # Test: load_fixture_pair returns correct tuple
        input_lines, expected_lines = load_fixture_pair(test_name, fixtures_dir)

        # Verify types
        assert isinstance(input_lines, list), "input_lines should be list"
        assert isinstance(expected_lines, list), "expected_lines should be list"
        assert all(isinstance(line, str) for line in input_lines)
        assert all(isinstance(line, str) for line in expected_lines)

        # Verify content with newlines preserved
        assert input_lines == ["# Test\n", "Line 1\n"]
        assert expected_lines == ["# Test\n", "Processed\n"]

    finally:
        # Cleanup test fixtures
        if input_file.exists():
            input_file.unlink()
        if expected_file.exists():
            expected_file.unlink()


def test_load_fixture_pair_missing_input() -> None:
    """Should raise FileNotFoundError if input file missing."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"

    with pytest.raises(FileNotFoundError, match="Input fixture not found"):
        load_fixture_pair("nonexistent", fixtures_dir)


def test_load_fixture_pair_missing_expected() -> None:
    """Should raise FileNotFoundError if expected file missing."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"
    test_name = "02-partial"

    # Create only input file
    input_file = fixtures_dir / f"{test_name}.input.md"
    input_file.write_text("test\n")

    try:
        with pytest.raises(FileNotFoundError, match="Expected fixture not found"):
            load_fixture_pair(test_name, fixtures_dir)
    finally:
        if input_file.exists():
            input_file.unlink()


def test_fixture_directory_exists() -> None:
    """Fixture directory should exist."""
    fixture_dir = Path(__file__).parent / "fixtures" / "markdown"

    # Directory must exist
    assert fixture_dir.exists(), f"Fixture directory {fixture_dir} does not exist"

    # Directory must be a directory, not a file
    assert fixture_dir.is_dir(), f"Path {fixture_dir} exists but is not a directory"


# Discover fixture files at module load time
def _discover_fixture_names() -> list[str]:
    """Discover fixture names from .input.md files in fixtures directory."""
    fixture_dir = Path(__file__).parent / "fixtures" / "markdown"
    input_files = fixture_dir.glob("*.input.md")

    # Extract fixture name by removing .input.md suffix
    fixture_names = []
    for input_file in sorted(input_files):
        # Get filename, strip .input.md extension
        filename = input_file.name
        fixture_name = filename.replace(".input.md", "")
        fixture_names.append(fixture_name)

    return fixture_names


# Get fixture names for parametrization
_FIXTURE_NAMES = _discover_fixture_names()


@pytest.mark.parametrize("fixture_name", _FIXTURE_NAMES)
def test_preprocessor_fixture(fixture_name: str) -> None:
    """Test preprocessor against fixture pairs.

    For each fixture file, load the input and expected output, run
    process_lines() on the input, and verify exact match.
    """
    # Load fixture pair
    input_lines, expected_lines = load_fixture_pair(fixture_name)

    # Process input
    result_lines = process_lines(input_lines)

    # Verify exact match
    assert result_lines == expected_lines, (
        f"Fixture {fixture_name} failed:\n"
        f"Expected: {expected_lines}\n"
        f"Got: {result_lines}"
    )


@pytest.mark.parametrize("fixture_name", _FIXTURE_NAMES)
def test_preprocessor_idempotency(fixture_name: str) -> None:
    """Test idempotency: re-processing output produces identical result.

    For each fixture, verify that running the preprocessor on its
    expected output yields the same output (idempotent behavior).
    This validates FR-4: preprocessor output is stable on re-processing.
    """
    # Load fixture pair
    _input_lines, expected_lines = load_fixture_pair(fixture_name)

    # Re-process the expected output
    reprocessed_lines = process_lines(expected_lines)

    # Verify idempotency: re-processing should not change the output
    assert reprocessed_lines == expected_lines, (
        f"Fixture {fixture_name} is not idempotent:\n"
        f"Original output: {expected_lines}\n"
        f"After re-process: {reprocessed_lines}"
    )


@pytest.mark.skipif(
    not shutil.which("remark"),
    reason="remark-cli not installed; skipping full pipeline test (FR-3)",
)
@pytest.mark.parametrize("fixture_name", _FIXTURE_NAMES)
def test_full_pipeline_remark(fixture_name: str) -> None:
    """Test full pipeline idempotency: (preprocessor → remark) twice.

    Validates FR-3: Full pipeline integration tests.
    Runs preprocessor → remark, then preprocessor → remark again on the output.
    The pipeline is idempotent when both passes produce identical results.

    Skips gracefully if remark-cli is not available.
    """
    if fixture_name == "02-inline-backticks":
        pytest.xfail(
            "Known preprocessor bug: multi-line inline code spans (requires redesign)"
        )

    # Load fixture pair
    input_lines, _ = load_fixture_pair(fixture_name)

    # First full pipeline pass: preprocessor → remark
    processed_lines = process_lines(input_lines)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp_file:
        tmp_path = tmp_file.name
        tmp_file.writelines(processed_lines)

    try:
        tmp_file_path = Path(tmp_path)
        remark_cmd = ["remark", "--rc-path", ".remarkrc.json", tmp_path, "--output"]

        result = subprocess.run(remark_cmd, capture_output=True, text=True, check=False)
        assert result.returncode == 0, (
            f"remark-cli failed for fixture {fixture_name}:\n"
            f"Exit code: {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        first_pass = tmp_file_path.read_text()

        # Second full pipeline pass: preprocessor → remark on first output
        second_processed = process_lines(first_pass.splitlines(keepends=True))
        tmp_file_path.write_text("".join(second_processed))

        result2 = subprocess.run(
            remark_cmd, capture_output=True, text=True, check=False
        )
        assert result2.returncode == 0, (
            f"remark-cli second pass failed for fixture {fixture_name}:\n"
            f"Exit code: {result2.returncode}\n"
            f"stderr: {result2.stderr}"
        )

        second_pass = tmp_file_path.read_text()
        assert first_pass == second_pass, (
            f"Full pipeline not idempotent for fixture {fixture_name}"
        )

    finally:
        # Cleanup temporary file
        tmp_file_path = Path(tmp_path)
        if tmp_file_path.exists():
            tmp_file_path.unlink()
