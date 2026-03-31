"""Tests for _resolve_api_key() env var → config file fallback chain."""

import pytest
from pytest_mock import MockerFixture

from edify.exceptions import ApiAuthenticationError
from edify.tokens_cli import _resolve_api_key


class TestResolveApiKeyFallback:
    """Tests for _resolve_api_key() env var → config file fallback."""

    def test_env_var_takes_precedence_over_config(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        """Env var present → returned directly, get_api_key never called."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-from-env")
        mock_config = mocker.patch("edify.tokens_cli.get_api_key")

        result = _resolve_api_key()
        assert result == "sk-ant-from-env"
        mock_config.assert_not_called()

    def test_falls_back_to_config_when_env_empty(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        """Empty env var → config file consulted, config key returned."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "")
        mocker.patch(
            "edify.tokens_cli.get_api_key", return_value="sk-ant-from-config"
        )

        result = _resolve_api_key()
        assert result == "sk-ant-from-config"

    def test_falls_back_to_config_when_env_unset(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        """Env var absent → config file consulted, config key returned."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        mocker.patch(
            "edify.tokens_cli.get_api_key", return_value="sk-ant-from-config"
        )

        result = _resolve_api_key()
        assert result == "sk-ant-from-config"

    def test_raises_when_neither_env_nor_config(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        """No env var, no config key → ApiAuthenticationError."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        mocker.patch("edify.tokens_cli.get_api_key", return_value=None)

        with pytest.raises(ApiAuthenticationError):
            _resolve_api_key()

    def test_env_whitespace_only_falls_back_to_config(
        self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
    ) -> None:
        """Whitespace-only env var → config file consulted."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
        mocker.patch(
            "edify.tokens_cli.get_api_key", return_value="sk-ant-from-config"
        )

        result = _resolve_api_key()
        assert result == "sk-ant-from-config"
