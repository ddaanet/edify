"""Parse model override environment variables from file."""

import re
from pathlib import Path


def read_overrides(path: Path) -> dict[str, str]:
    """Read and parse bash env var file into dict.

    Parses lines formatted as "export VAR=value" and returns a dictionary
    of environment variable names to values.

    Args:
        path: Path to the override file containing export statements.

    Returns:
        Dictionary mapping environment variable names to their values.
    """
    overrides = {}
    content = path.read_text()

    for raw_line in content.strip().split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Match "export VAR=value" pattern
        match = re.match(r"export\s+(\w+)=(.+)", line)
        if match:
            var_name, var_value = match.groups()
            overrides[var_name] = var_value

    return overrides


def write_overrides(path: Path, env_vars: dict[str, str]) -> None:
    r"""Write env vars dict to bash export statements.

    Writes environment variables as "export VAR=value\n" lines to a file.

    Args:
        path: Path to write the override file to.
        env_vars: Dictionary mapping variable names to values.
    """
    lines = [f"export {key}={value}\n" for key, value in env_vars.items()]
    path.write_text("".join(lines))
