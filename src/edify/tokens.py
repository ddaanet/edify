"""Token counting functionality using Anthropic API."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import NewType

from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError
from pydantic import BaseModel

from edify.exceptions import (
    ApiAuthenticationError,
    ApiError,
    ApiRateLimitError,
    FileReadError,
    ModelResolutionError,
)

logger = logging.getLogger(__name__)

ModelId = NewType("ModelId", str)
CACHE_TTL_HOURS = 24


class ModelInfo(BaseModel):
    """Model information stored in cache."""

    id: str
    created_at: datetime


class CacheData(BaseModel):
    """Cache file structure."""

    fetched_at: datetime
    models: list[ModelInfo]


class TokenCount(BaseModel):
    """Token count for a single file."""

    path: str
    count: int


# Claude Code / Plan OAuth tokens authenticate via Bearer, not the x-api-key header.
_OAUTH_TOKEN_PREFIX = "sk-ant-oat"  # noqa: S105 - public token-format prefix, not a secret


def make_client(api_key: str | None) -> Anthropic:
    """Build an Anthropic client with the correct auth scheme.

    OAuth tokens (``sk-ant-oat*``, e.g. Claude Code / Plan credentials)
    authenticate via ``Authorization: Bearer`` (``auth_token``); standard API
    keys use ``x-api-key`` (``api_key``). Passing an OAuth token as ``api_key``
    returns 401, so route by prefix.
    """
    if not api_key:
        return Anthropic()
    if api_key.startswith(_OAUTH_TOKEN_PREFIX):
        return Anthropic(auth_token=api_key)
    return Anthropic(api_key=api_key)


def _list_models(model: str, client: Anthropic) -> list[ModelInfo]:
    """Fetch the models list, mapping API failures to edify errors.

    AuthenticationError and RateLimitError subclass APIError; they mean the API
    answered and refused, so they must not be reported as an outage.
    """
    try:
        models_response = client.models.list()
    except AuthenticationError as e:
        raise ApiAuthenticationError(str(e)) from e
    except RateLimitError as e:
        raise ApiRateLimitError from e
    except APIError as e:
        raise ModelResolutionError(model) from e

    return [
        ModelInfo(id=model_obj.id, created_at=model_obj.created_at)
        for model_obj in models_response
    ]


def _latest_match(models: list[ModelInfo], alias: str) -> ModelId | None:
    """Return the most recently created model whose ID contains the alias."""
    matching = [m for m in models if alias.lower() in m.id.lower()]
    if not matching:
        return None
    matching.sort(key=lambda m: m.created_at, reverse=True)
    return ModelId(matching[0].id)


def resolve_model_alias(model: str, client: Anthropic, cache_dir: Path) -> ModelId:
    """Resolve model alias to full model ID.

    If model starts with "claude-", check if it's a full ID (with date
    suffix) and return. Otherwise, resolve via API or cache. Model alias
    matching is case-insensitive.

    Args:
        model: Model alias or ID to resolve (case-insensitive)
        client: Anthropic API client
        cache_dir: Directory for caching model lists

    Returns:
        Resolved full model ID

    Raises:
        ApiAuthenticationError: If the credential is missing or rejected
        ApiRateLimitError: If the API rate limit is exceeded
        ModelResolutionError: If API is unreachable and model alias cannot be resolved
    """
    # Check if it's a full model ID with date suffix (last part is 8 digits)
    if model.startswith("claude-"):
        parts = model.split("-")
        if parts[-1].isdigit() and len(parts[-1]) == 8:
            # Full model ID with date suffix, return as-is
            return ModelId(model)

    # Try to load from cache if it's fresh (< 24 hours old)
    cache_file = cache_dir / "models_cache.json"
    if cache_file.exists():
        try:
            cache_data = CacheData.model_validate_json(cache_file.read_text())

            # Check if cache is still fresh based on fetched_at timestamp
            fetched_at = cache_data.fetched_at
            age_seconds = datetime.now(tz=UTC).timestamp() - fetched_at.timestamp()

            # Cache is valid if fetched_at is fresh (ignore file mtime)
            if age_seconds < CACHE_TTL_HOURS * 3600:
                cached_match = _latest_match(cache_data.models, model)
                if cached_match is not None:
                    return cached_match
        except ValueError as e:
            logger.warning(
                "Corrupted cache file at %s, will refresh from API: %s",
                cache_file,
                e,
            )

    # Cache miss or expired - query API
    models_list = _list_models(model, client)

    # Write cache
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_to_write = CacheData(fetched_at=datetime.now(tz=UTC), models=models_list)
        cache_file.write_text(cache_to_write.model_dump_json())
        logger.debug("Cached models list to %s", cache_file)
    except OSError as e:
        logger.warning("Failed to write cache at %s: %s", cache_file, e)

    return _latest_match(models_list, model) or ModelId(model)


def _count_tokens_for_content(content: str, model: ModelId, client: Anthropic) -> int:
    """Count tokens for already-read content via Anthropic API.

    Returns 0 for empty content. Callers handle file I/O.
    """
    if not content:
        return 0

    try:
        response = client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": content}],
        )
    except AuthenticationError as e:
        raise ApiAuthenticationError(str(e)) from e
    except RateLimitError as e:
        raise ApiRateLimitError from e
    except APIError as e:
        raise ApiError(str(e)) from e

    return response.input_tokens


def count_tokens_for_file(path: Path, model: ModelId, client: Anthropic) -> int:
    """Count tokens in a file using Anthropic API.

    Args:
        path: Path to the file to count tokens for
        model: Model to use for token counting
        client: Anthropic API client

    Returns:
        Number of tokens in the file

    Raises:
        FileReadError: If file cannot be read
        ApiAuthenticationError: If API authentication fails
        ApiRateLimitError: If API rate limit is exceeded
    """
    try:
        content = path.read_text()
    except (PermissionError, OSError, UnicodeDecodeError) as e:
        raise FileReadError(str(path), str(e)) from e

    return _count_tokens_for_content(content, model, client)


def count_tokens_for_files(
    paths: list[Path], model: ModelId, client: Anthropic
) -> list[TokenCount]:
    """Count tokens in multiple files using Anthropic API with caching.

    Args:
        paths: List of paths to count tokens for
        model: Model to use for token counting
        client: Anthropic API client, authenticated by the caller

    Returns:
        List of TokenCount objects with per-file counts
    """
    from edify.token_cache import cached_count_tokens_for_file, get_default_cache  # noqa: PLC0415, I001

    cache = None
    try:
        cache = get_default_cache()
    except Exception:  # noqa: BLE001
        logger.warning("Token cache unavailable, falling back to uncached counting")

    results = []
    for path in paths:
        if cache is not None:
            count = cached_count_tokens_for_file(path, model, client, cache)
        else:
            count = count_tokens_for_file(path, model, client)
        results.append(TokenCount(path=str(path), count=count))
    return results


def calculate_total(results: list[TokenCount]) -> int:
    """Calculate total tokens across multiple file results.

    Args:
        results: List of TokenCount objects

    Returns:
        Sum of all token counts
    """
    return sum(result.count for result in results)
