"""Token counting functionality using Anthropic API."""

import contextlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import NewType

from anthropic import Anthropic, APIError, AuthenticationError, RateLimitError
from pydantic import BaseModel

from claudeutils.exceptions import (
    ApiAuthenticationError,
    ApiError,
    ApiRateLimitError,
    FileReadError,
    ModelResolutionError,
)
from claudeutils.user_config import get_api_key

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
                models = cache_data.models

                # Filter models containing the alias (case-insensitive)
                matching_models = [m for m in models if model.lower() in m.id.lower()]

                if matching_models:
                    # Sort by created_at descending and return latest
                    matching_models.sort(key=lambda m: m.created_at, reverse=True)
                    return ModelId(matching_models[0].id)
        except ValueError as e:
            logger.warning(
                "Corrupted cache file at %s, will refresh from API: %s",
                cache_file,
                e,
            )

    # Cache miss or expired - query API
    try:
        models_response = client.models.list()
    except APIError as e:
        raise ModelResolutionError(model) from e

    # Convert API response to dict format
    models_list = [
        ModelInfo(
            id=model_obj.id,
            created_at=model_obj.created_at,
        )
        for model_obj in models_response
    ]

    # Write cache
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_to_write = CacheData(fetched_at=datetime.now(tz=UTC), models=models_list)
        cache_file.write_text(cache_to_write.model_dump_json())
        logger.debug("Cached models list to %s", cache_file)
    except OSError as e:
        logger.warning("Failed to write cache at %s: %s", cache_file, e)

    # Filter for matching models
    matching_models = [m for m in models_list if model.lower() in m.id.lower()]

    if matching_models:
        matching_models.sort(key=lambda m: m.created_at, reverse=True)
        return ModelId(matching_models[0].id)

    return ModelId(model)


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

    if not content:
        return 0

    try:
        response = client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": content}],
        )
    except AuthenticationError as e:
        raise ApiAuthenticationError from e
    except RateLimitError as e:
        raise ApiRateLimitError from e
    except APIError as e:
        raise ApiError(str(e)) from e

    return response.input_tokens


def count_tokens_for_files(paths: list[Path], model: ModelId) -> list[TokenCount]:
    """Count tokens in multiple files using Anthropic API with caching.

    Args:
        paths: List of paths to count tokens for
        model: Model to use for token counting

    Returns:
        List of TokenCount objects with per-file counts
    """
    api_key = get_api_key()
    client = Anthropic(api_key=api_key) if api_key else Anthropic()

    from claudeutils.token_cache import cached_count_tokens_for_file, get_default_cache

    cache = None
    with contextlib.suppress(OSError):
        cache = get_default_cache()

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
