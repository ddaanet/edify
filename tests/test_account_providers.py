"""Tests for Provider Protocol."""

from unittest.mock import Mock

from edify.account import (
    AnthropicProvider,
    LiteLLMProvider,
    OpenRouterProvider,
)


def test_anthropic_provider_env_vars() -> None:
    """Test that AnthropicProvider.claude_env_vars returns ANTHROPIC_API_KEY."""
    # Create a mock KeyStore that returns a test API key
    mock_keystore = Mock()
    mock_keystore.get_anthropic_api_key.return_value = "test-anthropic-key"

    # Create AnthropicProvider with mock keystore
    provider = AnthropicProvider(mock_keystore)

    # Get environment variables
    env_vars = provider.claude_env_vars()

    # Verify ANTHROPIC_API_KEY is present and correct
    assert "ANTHROPIC_API_KEY" in env_vars
    assert env_vars["ANTHROPIC_API_KEY"] == "test-anthropic-key"

    # Verify that the keystore method was called
    mock_keystore.get_anthropic_api_key.assert_called_once()


def test_openrouter_provider_env_vars() -> None:
    """Return both API key and base URL.

    Test that OpenRouterProvider.claude_env_vars returns both OPENROUTER_API_KEY
    and ANTHROPIC_BASE_URL.
    """
    # Create a mock KeyStore that returns a test API key
    mock_keystore = Mock()
    mock_keystore.get_openrouter_api_key.return_value = "test-openrouter-key"

    # Create OpenRouterProvider with mock keystore
    provider = OpenRouterProvider(mock_keystore)

    # Get environment variables
    env_vars = provider.claude_env_vars()

    # Verify both OPENROUTER_API_KEY and ANTHROPIC_BASE_URL are present and correct
    assert "OPENROUTER_API_KEY" in env_vars
    assert env_vars["OPENROUTER_API_KEY"] == "test-openrouter-key"
    assert "ANTHROPIC_BASE_URL" in env_vars


def test_litellm_provider_env_vars() -> None:
    """Return LiteLLM-specific variables.

    Test that LiteLLMProvider.claude_env_vars returns both LITELLM_API_KEY and
    ANTHROPIC_BASE_URL.
    """
    # Create LiteLLMProvider
    provider = LiteLLMProvider()

    # Get environment variables
    env_vars = provider.claude_env_vars()

    # Verify LITELLM_API_KEY and ANTHROPIC_BASE_URL are present
    assert "LITELLM_API_KEY" in env_vars
    assert "ANTHROPIC_BASE_URL" in env_vars
    # Verify specific localhost URL value
    assert env_vars["ANTHROPIC_BASE_URL"] == "http://localhost:4000"
