"""Tests for user_config module — config file API key reading."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from edify.user_config import get_api_key


@pytest.fixture
def config_dir(tmp_path: Path, mocker: MockerFixture) -> Path:
    """Redirect CONFIG_FILE to a tmp_path-based location."""
    config_file = tmp_path / "config.toml"
    mocker.patch("edify.user_config.CONFIG_FILE", config_file)
    return tmp_path


def _write_config(config_dir: Path, content: str) -> None:
    (config_dir / "config.toml").write_text(content)


class TestGetApiKey:
    """Config file API key reading."""

    def test_returns_none_when_file_missing(self, config_dir: Path) -> None:
        """No config file on disk → None."""
        result = get_api_key()
        assert result is None

    def test_returns_key_from_valid_config(self, config_dir: Path) -> None:
        """Valid [anthropic] api_key → returns the key string."""
        _write_config(config_dir, '[anthropic]\napi_key = "sk-ant-real-key"\n')
        result = get_api_key()
        assert result == "sk-ant-real-key"

    def test_returns_none_for_malformed_toml(self, config_dir: Path) -> None:
        """Unparseable TOML → None, no exception raised."""
        _write_config(config_dir, "not valid [[ toml {{{")
        result = get_api_key()
        assert result is None

    def test_returns_none_for_whitespace_only_key(self, config_dir: Path) -> None:
        """api_key = "   " → None (covers empty string too via strip)."""
        _write_config(config_dir, '[anthropic]\napi_key = "   "\n')
        result = get_api_key()
        assert result is None

    def test_returns_none_when_anthropic_section_missing(
        self, config_dir: Path
    ) -> None:
        """Config exists but no [anthropic] section → None."""
        _write_config(config_dir, '[other]\nfoo = "bar"\n')
        result = get_api_key()
        assert result is None
