"""API usage parsing from stats-cache.json with model tier aggregation."""

import json
from datetime import UTC, datetime
from pathlib import Path

from edify.account.switchback import read_switchback_plist
from edify.statusline.models import ApiUsageData


def aggregate_by_tier(tokens_by_model: dict[str, int]) -> dict[str, int]:
    """Aggregate token counts by model tier using keyword matching.

    Args:
        tokens_by_model: Dictionary mapping model names to token counts.

    Returns:
        Dictionary with 'opus', 'sonnet', 'haiku' keys containing aggregated counts.
    """
    result = {"opus": 0, "sonnet": 0, "haiku": 0}

    for model_name, tokens in tokens_by_model.items():
        if "opus" in model_name.lower():
            result["opus"] += tokens
        elif "sonnet" in model_name.lower():
            result["sonnet"] += tokens
        elif "haiku" in model_name.lower():
            result["haiku"] += tokens

    return result


def get_api_usage() -> ApiUsageData | None:
    """Read ~/.claude/stats-cache.json and aggregate tokens by model tier.

    Parses dailyModelTokens from stats-cache.json and aggregates today's tokens
    and last 7 days of tokens by model tier (opus/sonnet/haiku).

    Returns:
        ApiUsageData with token counts by tier for today and last 7 days.
        Returns None if stats-cache.json cannot be read.
    """
    stats_cache_path = Path.home() / ".claude" / "stats-cache.json"

    try:
        with stats_cache_path.open("r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    daily_model_tokens = data.get("dailyModelTokens", {})
    if not daily_model_tokens:
        return None

    # Get today's date in YYYY-MM-DD format
    today = datetime.now(UTC).strftime("%Y-%m-%d")

    # Aggregate today's tokens
    today_tokens = daily_model_tokens.get(today, {})
    today_aggregated = aggregate_by_tier(today_tokens)

    # Calculate most recent 7 days by sorting dates descending
    week_aggregated = {"opus": 0, "sonnet": 0, "haiku": 0}
    sorted_dates = sorted(daily_model_tokens.keys(), reverse=True)[:7]
    for date in sorted_dates:
        day_aggregated = aggregate_by_tier(daily_model_tokens[date])
        for tier in ["opus", "sonnet", "haiku"]:
            week_aggregated[tier] += day_aggregated[tier]

    return ApiUsageData(
        today_opus=today_aggregated["opus"],
        today_sonnet=today_aggregated["sonnet"],
        today_haiku=today_aggregated["haiku"],
        week_opus=week_aggregated["opus"],
        week_sonnet=week_aggregated["sonnet"],
        week_haiku=week_aggregated["haiku"],
    )


def get_switchback_time() -> str | None:
    """Get switchback time from plist and format as MM/DD HH:MM.

    Calls read_switchback_plist() to retrieve the switchback datetime
    and formats it as MM/DD HH:MM for display.

    Returns:
        Formatted switchback time string or None if plist not available.
    """
    switchback_dt = read_switchback_plist()
    if switchback_dt is None:
        return None
    return switchback_dt.strftime("%m/%d %H:%M")
