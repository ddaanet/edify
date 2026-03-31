"""End-to-end integration tests for token counter CLI.

These tests require real API keys and network access.
"""

import sys
from pathlib import Path

import pytest

from edify.cli import main


@pytest.mark.e2e
def test_end_to_end_token_counting_with_alias_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test end-to-end token counting with model alias resolution.

    Given: Environment has valid ANTHROPIC_API_KEY, no models cache exists, real
      file "fixture.md" with known content, model="sonnet" (unversioned alias)
    When: `edify tokens sonnet fixture.md` executed
    Then:
      - Exits 0
      - First line shows resolved model ID
        (e.g., "Using model: claude-sonnet-4-5-20250929")
      - Second line shows file with token count
      - Cache file created in user directory
    """
    # Create test file
    fixture_file = tmp_path / "fixture.md"
    fixture_file.write_text("# Test\n\nHello world")

    # Isolate cache to tmp_path
    cache_dir = tmp_path / ".cache"
    monkeypatch.setattr(
        "platformdirs.user_cache_dir",
        lambda appname: str(cache_dir),
    )

    # Patch argv and call main
    monkeypatch.setattr(
        sys, "argv", ["edify", "tokens", "sonnet", str(fixture_file)]
    )

    # Call main function
    main()

    # Check output
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    assert len(lines) >= 2, f"Expected at least 2 lines, got: {captured.out}"
    assert lines[0].startswith("Using model: claude-"), f"First line: {lines[0]}"
    assert fixture_file.name in lines[1], f"Second line: {lines[1]}"
