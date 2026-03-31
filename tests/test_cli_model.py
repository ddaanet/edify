"""Tests for the model CLI command group."""

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from edify.cli import cli


def test_model_list(tmp_path: Path) -> None:
    """Test that model list command outputs model names."""
    # Create a mock config file with a sample model
    config_dir = tmp_path / ".config" / "litellm"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("""model_list:
  - model_name: claude-3-haiku  # haiku,sonnet - arena:5 $0.25/$1.25
    litellm_params:
      model: claude-3-5-sonnet-20241022
  - model_name: gpt-4  # sonnet - arena:10 $0.03/$0.06
    litellm_params:
      model: gpt-4
""")

    runner = CliRunner()
    with patch("pathlib.Path.home", return_value=tmp_path):
        result = runner.invoke(cli, ["model", "list"])
    assert result.exit_code == 0
    assert "claude-3-haiku" in result.output
    assert "gpt-4" in result.output


def test_model_set(tmp_path: Path) -> None:
    """Test that model set command writes override file."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    runner = CliRunner()
    with patch("pathlib.Path.home", return_value=tmp_path):
        result = runner.invoke(cli, ["model", "set", "claude-3-haiku"])
    assert result.exit_code == 0
    override_file = claude_dir / "model-override"
    assert override_file.exists()
    assert "ANTHROPIC_MODEL=" in override_file.read_text()


def test_model_reset(tmp_path: Path) -> None:
    """Test that model reset command deletes override file."""
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    override_file = claude_dir / "model-override"
    override_file.write_text("export ANTHROPIC_MODEL=claude-3-haiku\n")

    runner = CliRunner()
    with patch("pathlib.Path.home", return_value=tmp_path):
        result = runner.invoke(cli, ["model", "reset"])
    assert result.exit_code == 0
    assert not override_file.exists()
