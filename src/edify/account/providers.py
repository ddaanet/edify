"""Provider Protocol for account providers."""

from typing import Protocol


class KeyStore(Protocol):
    """Protocol for keystore implementations."""

    def get_anthropic_api_key(self) -> str:
        """Get the Anthropic API key from keystore."""
        ...

    def get_openrouter_api_key(self) -> str:
        """Get the OpenRouter API key from keystore."""
        ...


class Provider(Protocol):
    """Protocol defining the interface for account providers."""

    @property
    def name(self) -> str:
        """Get the provider name."""
        ...

    def claude_env_vars(self) -> dict[str, str]:
        """Get environment variables needed for this provider."""
        ...

    def validate(self) -> list[str]:
        """Validate provider configuration.

        Returns list of issues.
        """
        ...

    def settings_json_patch(self) -> dict[str, object]:
        """Get the patch to apply to settings.json for this provider."""
        ...


class AnthropicProvider:
    """Provider implementation for Anthropic API."""

    def __init__(self, keystore: KeyStore) -> None:
        """Initialize AnthropicProvider with keystore.

        Args:
            keystore: KeyStore instance for retrieving credentials.
        """
        self.keystore = keystore

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "anthropic"

    def claude_env_vars(self) -> dict[str, str]:
        """Get environment variables needed for this provider."""
        api_key = self.keystore.get_anthropic_api_key()
        return {"ANTHROPIC_API_KEY": api_key}

    def validate(self) -> list[str]:
        """Validate provider configuration.

        Returns list of issues.
        """
        return []

    def settings_json_patch(self) -> dict[str, object]:
        """Get the patch to apply to settings.json for this provider."""
        return {}


class OpenRouterProvider:
    """Provider implementation for OpenRouter API."""

    def __init__(self, keystore: KeyStore) -> None:
        """Initialize OpenRouterProvider with keystore.

        Args:
            keystore: KeyStore instance for retrieving credentials.
        """
        self.keystore = keystore

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "openrouter"

    def claude_env_vars(self) -> dict[str, str]:
        """Get environment variables needed for this provider."""
        api_key = self.keystore.get_openrouter_api_key()
        return {
            "OPENROUTER_API_KEY": api_key,
            "ANTHROPIC_BASE_URL": "",
        }

    def validate(self) -> list[str]:
        """Validate provider configuration.

        Returns list of issues.
        """
        return []

    def settings_json_patch(self) -> dict[str, object]:
        """Get the patch to apply to settings.json for this provider."""
        return {}


class LiteLLMProvider:
    """Provider implementation for LiteLLM proxy."""

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "litellm"

    def claude_env_vars(self) -> dict[str, str]:
        """Get environment variables needed for this provider."""
        return {
            "LITELLM_API_KEY": "none",
            "ANTHROPIC_BASE_URL": "http://localhost:4000",
        }

    def validate(self) -> list[str]:
        """Validate provider configuration.

        Returns list of issues.
        """
        return []

    def settings_json_patch(self) -> dict[str, object]:
        """Get the patch to apply to settings.json for this provider."""
        return {}
