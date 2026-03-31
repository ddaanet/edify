"""User configuration for edify.

Reads config from ~/.config/edify/config.toml (or platform equivalent).
"""

import logging
import tomllib
from pathlib import Path

import platformdirs

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(platformdirs.user_config_dir("edify"))
CONFIG_FILE = CONFIG_DIR / "config.toml"


def get_api_key() -> str | None:
    """Read Anthropic API key from user config file.

    Reads [anthropic] api_key from config.toml. Returns None if file doesn't
    exist, section is missing, or key is empty.
    """
    if not CONFIG_FILE.exists():
        return None

    try:
        data = tomllib.loads(CONFIG_FILE.read_text())
    except (OSError, tomllib.TOMLDecodeError) as e:
        logger.warning("Failed to read config %s: %s", CONFIG_FILE, e)
        return None

    key = data.get("anthropic", {}).get("api_key", "")
    return key if key.strip() else None
