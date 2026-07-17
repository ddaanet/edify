"""Tests for _resolve_api_key() env var → config file fallback chain."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import Anthropic
from pytest_mock import MockerFixture

from edify.exceptions import ApiAuthenticationError
from edify.token_cache import TokenCache, create_cache_engine
from edify.tokens import ModelId
from edify.tokens_cli import _resolve_api_key, handle_tokens


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


class TestResolvedKeyReachesCounting:
    """The key chosen by _resolve_api_key must be the one used to count."""

    def test_counting_uses_client_built_from_resolved_key(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        """Env var wins for counting too, not just for alias resolution.

        Given: ANTHROPIC_API_KEY set, and a stale key in the config file
        When: handle_tokens counts a file
        Then: Exactly one client is built, from the env key, and that same
        client performs the count — the config key is never used
        """
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-from-env")
        mocker.patch(
            "edify.tokens_cli.get_api_key", return_value="sk-ant-stale-config"
        )

        sentinel_client = Mock(spec=Anthropic)
        make_client = mocker.patch(
            "edify.tokens_cli.make_client",
            autospec=True,
            return_value=sentinel_client,
        )
        mocker.patch(
            "edify.tokens_cli.resolve_model_alias",
            return_value=ModelId("claude-sonnet-4-5-20250929"),
        )
        mocker.patch(
            "edify.token_cache.get_default_cache",
            return_value=TokenCache(create_cache_engine(":memory:")),
        )
        count = mocker.patch(
            "edify.token_cache._count_tokens_for_content", return_value=7
        )

        test_file = tmp_path / "test.md"
        test_file.write_text("Hello world")

        handle_tokens("sonnet", [str(test_file)])

        make_client.assert_called_once_with("sk-ant-from-env")
        assert count.call_args.args[2] is sentinel_client
