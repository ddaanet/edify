"""Test model overrides file reading."""

import tempfile
from pathlib import Path

from edify.model import read_overrides, write_overrides


def test_read_overrides() -> None:
    """read_overrides() parses bash env var file into dict."""
    # Create a sample override file with export statements
    overrides_content = """export ANTHROPIC_API_KEY=sk-test-key
export ANTHROPIC_BASE_URL=https://example.com
export LITELLM_API_KEY=sk-litellm-key
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        override_file = Path(tmpdir) / "claude-model-overrides"
        override_file.write_text(overrides_content)

        result = read_overrides(override_file)

        assert isinstance(result, dict)
        assert result["ANTHROPIC_API_KEY"] == "sk-test-key"
        assert result["ANTHROPIC_BASE_URL"] == "https://example.com"
        assert result["LITELLM_API_KEY"] == "sk-litellm-key"


def test_write_overrides() -> None:
    """write_overrides() writes env vars dict to bash export statements."""
    env_vars = {
        "ANTHROPIC_API_KEY": "sk-test-key",
        "ANTHROPIC_BASE_URL": "https://example.com",
        "LITELLM_API_KEY": "sk-litellm-key",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        override_file = Path(tmpdir) / "claude-model-overrides"

        write_overrides(override_file, env_vars)

        content = override_file.read_text()
        assert "export ANTHROPIC_API_KEY=sk-test-key\n" in content
        assert "export ANTHROPIC_BASE_URL=https://example.com\n" in content
        assert "export LITELLM_API_KEY=sk-litellm-key\n" in content
