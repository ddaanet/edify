"""Fetch plan mode usage limits from Claude OAuth API with caching."""

import json
from typing import Any, cast

from edify.account.usage import UsageCache
from edify.statusline.models import PlanUsageData


def get_plan_usage() -> PlanUsageData | None:
    """Fetch plan mode usage limits from Claude OAuth API.

    Uses UsageCache to fetch 5h and 7d limits from the OAuth API, parsing
    percentages and reset times.

    Returns:
        PlanUsageData with 5h/7d percentages and reset times, or None on error.
    """
    try:
        cache = UsageCache()
        usage_data = cache.get()

        if not usage_data or not isinstance(usage_data, dict):
            return None

        percent_5h: Any = usage_data.get("usage_5h_percent", 0)
        reset_5h: Any = usage_data.get("usage_5h_reset", "—")
        percent_7d: Any = usage_data.get("usage_7d_percent", 0)

        return PlanUsageData(
            hour5_pct=float(cast("float", percent_5h)) if percent_5h else 0.0,
            hour5_reset=str(cast("str", reset_5h)) if reset_5h else "—",
            day7_pct=float(cast("float", percent_7d)) if percent_7d else 0.0,
        )
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return None
    except Exception:  # noqa: BLE001 - D8: fail-safe, return None for any unexpected error
        return None
