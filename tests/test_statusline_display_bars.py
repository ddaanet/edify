"""Tests for StatuslineFormatter - bar and context display."""

import pytest

from edify.statusline import StatuslineFormatter


@pytest.mark.parametrize(
    ("tokens", "expected_colors", "expected_chars"),
    [
        # Empty bar (no brackets, matches shell)
        (0, [], []),
        # Single block tests (brgreen)
        # Shell formula: idx = ((partial * 8 + 12500) / 25000)
        # 12500: idx = 4 → ▋
        (12500, ["\033[92m"], ["▋"]),
        (25000, ["\033[92m"], ["█"]),  # Full block
        # Two blocks (brgreen + green)
        # 37500: 1 full + 12500 partial, idx = 4 → ▋
        (37500, ["\033[92m", "\033[32m"], ["█", "▋"]),
        (50000, ["\033[92m", "\033[32m"], ["█"]),
        # Three blocks (brgreen + green + blue)
        (62500, ["\033[92m", "\033[32m", "\033[34m"], []),
        # Four blocks (brgreen + green + blue + yellow)
        (87500, ["\033[92m", "\033[32m", "\033[34m", "\033[33m"], []),
        (100000, ["\033[92m", "\033[32m", "\033[34m", "\033[33m"], ["█"]),
        # Five blocks (brgreen + green + blue + yellow + red)
        (112500, ["\033[92m", "\033[32m", "\033[34m", "\033[33m", "\033[31m"], []),
        # 143750: 5 full + 18750 partial, idx = ((18750*8+12500)/25000) = 6 → ▉
        (143750, ["\033[92m", "\033[32m", "\033[34m", "\033[33m", "\033[31m"], ["▉"]),
        # Six blocks with critical coloring
        (
            137500,
            [
                "\033[92m",
                "\033[32m",
                "\033[34m",
                "\033[33m",
                "\033[31m",
                "\033[91m",
                "\033[5m",
            ],
            [],
        ),
    ],
)
def test_horizontal_token_bar(
    tokens: int, expected_colors: list[str], expected_chars: list[str]
) -> None:
    """Test horizontal token bar with Unicode blocks.

    No brackets (matches shell).
    """
    formatter = StatuslineFormatter()
    result = formatter.horizontal_token_bar(tokens)

    if tokens == 0:
        assert result == ""
        return

    # Check for expected colors
    for color in expected_colors:
        assert color in result

    # Check for expected characters
    for char in expected_chars:
        assert char in result

    # All results should have reset code
    assert "\033[0m" in result


@pytest.mark.parametrize(
    ("tokens", "expected_count", "expected_color"),
    [
        (1500, "1k", "\033[92m"),  # BRGREEN - integer kilos (matches shell)
        (45000, "45k", "\033[32m"),  # GREEN
        (1200000, "1.2M", "\033[91m"),  # BRRED
    ],
)
def test_format_context(tokens: int, expected_count: str, expected_color: str) -> None:
    """Test format_context with emoji, colored count, and bar (no brackets)."""
    formatter = StatuslineFormatter()
    result = formatter.format_context(tokens)

    # Check emoji and count
    assert "🧠" in result
    assert expected_count in result
    assert expected_color in result

    # No enclosing brackets around bar (matches shell reference)
    # Note: ANSI codes contain [ character, so check for actual bracket patterns
    assert not result.endswith("]"), "Result should not end with bracket"
    assert "[]" not in result, "Result should not have empty brackets"

    # Extra check for critical color (1.2M case)
    if tokens == 1200000:
        assert "\033[5m" in result  # BLINK


def test_format_context_integer_kilos() -> None:
    """Test format_context uses integer kilos (truncation, not rounding).

    Verifies boundary behavior for kilo thresholds.
    """
    formatter = StatuslineFormatter()

    # 1999 → "1k" (truncation, not rounding)
    result = formatter.format_context(1999)
    assert "1k" in result

    # 999 → "999" (below kilo threshold)
    result = formatter.format_context(999)
    assert "999" in result
    assert "k" not in result

    # 1000 → "1k" (exact boundary)
    result = formatter.format_context(1000)
    assert "1k" in result

    # 50500 → "50k" (not "50.5k")
    result = formatter.format_context(50500)
    assert "50k" in result
    assert "50.5" not in result
