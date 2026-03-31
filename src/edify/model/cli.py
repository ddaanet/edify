"""CLI commands for model management."""

from pathlib import Path

import click

from edify.model import load_litellm_config, write_overrides


@click.group()
def model() -> None:
    """Manage Claude models and configuration."""


@model.command("list")
def list_models() -> None:
    """List available models from LiteLLM configuration."""
    config_path = Path.home() / ".config" / "litellm" / "config.yaml"
    if config_path.exists():
        models = load_litellm_config(config_path)
        for m in models:
            click.echo(m.name)
    else:
        click.echo("No LiteLLM configuration found")


@model.command("set")
@click.argument("model_name")
def set_model(model_name: str) -> None:
    """Set the default model by writing to override file."""
    claude_dir = Path.home() / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    override_file = claude_dir / "model-override"
    write_overrides(override_file, {"ANTHROPIC_MODEL": model_name})


@model.command("reset")
def reset_model() -> None:
    """Reset the default model by deleting override file."""
    override_file = Path.home() / ".claude" / "model-override"
    if override_file.exists():
        override_file.unlink()
