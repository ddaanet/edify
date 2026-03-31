"""CLI commands for account management."""

from pathlib import Path
from typing import cast

import click

from edify.account.keychain import Keychain
from edify.account.providers import (
    AnthropicProvider,
    OpenRouterProvider,
)
from edify.account.state import get_account_state


@click.group()
def account() -> None:
    """Manage Claude account configuration."""


@account.command()
def status() -> None:
    """Display current account status."""
    state = get_account_state()
    issues = state.validate_consistency()
    click.echo(f"Mode: {state.mode}")
    click.echo(f"Provider: {state.provider}")
    if issues:
        click.echo("Issues:")
        for issue in issues:
            click.echo(f"  - {issue}")
    else:
        click.echo("No issues found")


@account.command()
def plan() -> None:
    """Switch to plan mode and write account configuration files."""
    # Create keychain adapter for provider
    keychain = Keychain()

    class KeychainAdapter:
        """Adapter to convert Keychain to KeyStore protocol."""

        def __init__(self, keychain: Keychain) -> None:
            self.keychain = keychain

        def get_anthropic_api_key(self) -> str:
            """Get Anthropic API key from keychain."""
            return (
                self.keychain.find(account="anthropic", service="com.anthropic.claude")
                or ""
            )

        def get_openrouter_api_key(self) -> str:
            """Get OpenRouter API key from keychain."""
            return (
                self.keychain.find(account="openrouter", service="com.anthropic.claude")
                or ""
            )

    # Create provider and get credentials
    keystore = KeychainAdapter(keychain)
    provider = AnthropicProvider(keystore)
    env_vars = provider.claude_env_vars()

    # Format environment variables
    env_lines = [f"{key}={value}" for key, value in env_vars.items()]
    env_content = "\n".join(env_lines)

    # Write configuration files
    account_mode_file = Path.home() / ".claude" / "account-mode"
    claude_env_file = Path.home() / ".claude" / "claude-env"

    account_mode_file.parent.mkdir(parents=True, exist_ok=True)
    account_mode_file.write_text("plan")
    claude_env_file.write_text(env_content)

    click.echo("Switched to plan mode")


@account.command()
@click.option("--provider", default="anthropic", help="API provider to use")
def api(provider: str) -> None:
    """Switch to API mode and select provider."""
    # Create keychain adapter for provider
    keychain = Keychain()

    class KeychainAdapter:
        """Adapter to convert Keychain to KeyStore protocol."""

        def __init__(self, keychain: Keychain) -> None:
            self.keychain = keychain

        def get_anthropic_api_key(self) -> str:
            """Get Anthropic API key from keychain."""
            return (
                self.keychain.find(account="anthropic", service="com.anthropic.claude")
                or ""
            )

        def get_openrouter_api_key(self) -> str:
            """Get OpenRouter API key from keychain."""
            return (
                self.keychain.find(account="openrouter", service="com.anthropic.claude")
                or ""
            )

    keystore = KeychainAdapter(keychain)

    # Factory function to create provider based on name
    provider_map = {
        "anthropic": AnthropicProvider,
        "openrouter": OpenRouterProvider,
    }
    provider_class = cast("type", provider_map.get(provider, AnthropicProvider))
    provider_instance = provider_class(keystore)

    # Get provider credentials
    env_vars = provider_instance.claude_env_vars()

    # Format environment variables
    env_lines = [f"{key}={value}" for key, value in env_vars.items()]
    env_content = "\n".join(env_lines)

    # Write configuration files
    account_mode_file = Path.home() / ".claude" / "account-mode"
    provider_file = Path.home() / ".claude" / "account-provider"
    claude_env_file = Path.home() / ".claude" / "claude-env"

    account_mode_file.parent.mkdir(parents=True, exist_ok=True)
    account_mode_file.write_text("api")
    provider_file.write_text(provider)
    claude_env_file.write_text(env_content)

    click.echo(f"Switched to API mode with provider: {provider}")
