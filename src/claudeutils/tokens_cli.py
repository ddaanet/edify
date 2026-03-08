"""CLI handler for tokens subcommand."""

import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

import platformdirs
from anthropic import Anthropic, AuthenticationError

from claudeutils.exceptions import (
    ApiAuthenticationError,
    ApiRateLimitError,
    ClaudeUtilsError,
)
from claudeutils.tokens import (
    TokenCount,
    calculate_total,
    count_tokens_for_file,
    resolve_model_alias,
)
from claudeutils.user_config import get_api_key


def _resolve_api_key() -> str:
    """Resolve API key from env var or config file.

    Raises ApiAuthenticationError if neither source has a key.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.strip() == "":
        api_key = get_api_key()
    if not api_key:
        raise ApiAuthenticationError
    return api_key


def handle_tokens(model: str, files: list[str], *, json_output: bool = False) -> None:
    """Handle the tokens subcommand.

    Args:
        model: Model to use for token counting
        files: File paths to count tokens for
        json_output: Whether to output JSON format
    """
    try:
        api_key = _resolve_api_key()

        if not files:
            print("Error: at least one file is required", file=sys.stderr)
            sys.exit(1)

        file_paths = files

        client = Anthropic(api_key=api_key)
        cache_dir = Path(platformdirs.user_cache_dir("claudeutils"))
        resolved_model = resolve_model_alias(model, client, cache_dir)

        from claudeutils.token_cache import (
            cached_count_tokens_for_file,
            get_default_cache,
        )

        token_cache = None
        try:
            token_cache = get_default_cache()
        except OSError:
            logger.warning("Token cache unavailable, falling back to uncached counting")

        results = []
        for filepath_str in file_paths:
            filepath = Path(filepath_str)
            if token_cache is not None:
                count = cached_count_tokens_for_file(
                    filepath, resolved_model, client, token_cache
                )
            else:
                count = count_tokens_for_file(filepath, resolved_model, client)
            results.append(TokenCount(path=str(filepath), count=count))

        if json_output:
            total = calculate_total(results)
            output = {
                "model": resolved_model,
                "files": [{"path": r.path, "count": r.count} for r in results],
                "total": total,
            }
            print(json.dumps(output))
        else:
            print(f"Using model: {resolved_model}")
            for i, result in enumerate(results):
                print(f"{file_paths[i]}: {result.count} tokens")
            if len(results) > 1:
                total = calculate_total(results)
                print(f"Total: {total} tokens")
    except (AuthenticationError, ApiAuthenticationError) as e:
        print(f"Error: Authentication failed. {e}", file=sys.stderr)
        print(
            "Set ANTHROPIC_API_KEY or add [anthropic] api_key "
            "to ~/.config/claudeutils/config.toml",
            file=sys.stderr,
        )
        sys.exit(1)
    except ApiRateLimitError as e:
        print(f"Error: Rate limit exceeded. {e}", file=sys.stderr)
        sys.exit(1)
    except ClaudeUtilsError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
