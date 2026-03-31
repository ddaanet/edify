"""Test CLI compose command."""

from pathlib import Path

from click.testing import CliRunner

from edify.cli import cli


def test_cli_compose_basic(tmp_path: Path) -> None:
    """Compose from config file via CLI."""
    # Create fragments
    frag1 = tmp_path / "frag1.md"
    frag1.write_text("# Part 1\n")
    frag2 = tmp_path / "frag2.md"
    frag2.write_text("# Part 2\n")

    # Create config
    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag1}
  - {frag2}
output: {tmp_path / "output.md"}
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config)])

    assert result.exit_code == 0
    assert (tmp_path / "output.md").exists()


def test_cli_compose_missing_config_file() -> None:
    """Exit with code 4 for missing config file."""
    runner = CliRunner()
    result = runner.invoke(cli, ["compose", "nonexistent.yaml"])

    assert result.exit_code == 4
    assert "Error" in result.output


def test_cli_compose_output_override(tmp_path: Path) -> None:
    """Override output path with --output option."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag}
output: {tmp_path / "default.md"}
""")

    custom_output = tmp_path / "custom.md"
    runner = CliRunner()
    result = runner.invoke(
        cli, ["compose", str(config), "--output", str(custom_output)]
    )

    assert result.exit_code == 0
    assert custom_output.exists()
    assert not (tmp_path / "default.md").exists()


def test_cli_compose_validate_warn(tmp_path: Path) -> None:
    """Use warn validation mode with --validate option."""
    frag1 = tmp_path / "exists.md"
    frag1.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag1}
  - {tmp_path / "missing.md"}
output: {tmp_path / "output.md"}
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config), "--validate", "warn"])

    assert result.exit_code == 0
    assert "WARNING" in result.output or "WARNING" in result.stderr_bytes.decode()


def test_cli_compose_verbose(tmp_path: Path) -> None:
    """Show verbose output with --verbose flag."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag}
output: {tmp_path / "output.md"}
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config), "--verbose"])

    assert result.exit_code == 0
    assert "Loading config" in result.output


def test_cli_compose_dry_run(tmp_path: Path) -> None:
    """Show plan without writing with --dry-run flag."""
    frag = tmp_path / "frag.md"
    frag.write_text("Content\n")

    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {frag}
output: {tmp_path / "output.md"}
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config), "--dry-run"])

    assert result.exit_code == 0
    assert "Dry-run" in result.output
    assert not (tmp_path / "output.md").exists()


def test_cli_compose_config_error_exit_code(tmp_path: Path) -> None:
    """Exit code 1 for configuration errors."""
    config = tmp_path / "bad.yaml"
    config.write_text("output: missing_fragments_field.md")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config)])

    assert result.exit_code == 1
    assert "Configuration error" in result.output


def test_cli_compose_fragment_error_exit_code(tmp_path: Path) -> None:
    """Exit code 2 for missing fragments in strict mode."""
    config = tmp_path / "compose.yaml"
    config.write_text(f"""
fragments:
  - {tmp_path / "missing.md"}
output: {tmp_path / "output.md"}
""")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config)])

    assert result.exit_code == 2


def test_cli_compose_invalid_config_file_exit_code() -> None:
    """Exit code 4 for invalid config file path."""
    runner = CliRunner()
    result = runner.invoke(cli, ["compose", "nonexistent.yaml"])

    # Click automatically validates exists=True
    assert result.exit_code in (2, 4)  # Click may use 2 for usage errors


def test_cli_compose_error_message_to_stderr(tmp_path: Path) -> None:
    """Print error messages to stderr."""
    config = tmp_path / "bad.yaml"
    config.write_text("invalid: config")

    runner = CliRunner()
    result = runner.invoke(cli, ["compose", str(config)])

    assert result.exit_code != 0
    # Error output should be present
    assert "error" in result.output.lower() or "Error" in result.output
