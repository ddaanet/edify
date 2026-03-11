"""Tests for continuation consumption protocol (peel-first-pass-remainder)."""

import re

import pytest


def parse_continuation_string(
    continuation_str: str | None,
) -> list[dict[str, str]] | None:
    """Parse [CONTINUATION: ...] format into list of entries.

    Format: [CONTINUATION: /skill1 arg1, /skill2 arg2]
    Returns list of {'skill': '...', 'args': '...'} dicts, or None if empty/malformed.
    """
    if not continuation_str:
        return None

    # Match [CONTINUATION: ...] pattern
    match = re.search(r"\[CONTINUATION:\s*(.+?)\]", continuation_str, re.DOTALL)
    if not match:
        return None

    content = match.group(1).strip()
    if not content:
        return None

    entries = []
    # Split by comma, but only if not inside nested structures
    parts = [p.strip() for p in content.split(",")]

    for part in parts:
        if not part:
            continue

        # Parse /skill args format
        space_idx = part.find(" ")
        if space_idx == -1:
            # Just skill, no args
            skill = part.lstrip("/")
            args = ""
        else:
            skill = part[:space_idx].lstrip("/")
            args = part[space_idx + 1 :].strip()

        entries.append({"skill": skill, "args": args})

    return entries or None


def peel_continuation(
    args_with_continuation: str,
) -> tuple[dict[str, str] | None, str | None]:
    """Peel first entry from continuation in args.

    Return (target_entry, remainder_str).

    Input: args with [CONTINUATION: /a, /b, /c]
    Output: ({'skill': 'a', 'args': ''}, '[CONTINUATION: /b, /c]')

    Returns:
        (None, None) if no continuation
        (target_dict, remainder_str) where remainder_str is formatted
        [CONTINUATION: ...] or None if empty
    """
    entries = parse_continuation_string(args_with_continuation)
    if not entries or len(entries) == 0:
        return (None, None)

    target = entries[0]

    # Build remainder
    if len(entries) > 1:
        remainder_entries = entries[1:]
        # Rebuild the [CONTINUATION: ...] format
        remainder_parts = []
        for entry in remainder_entries:
            if entry["args"]:
                remainder_parts.append(f"/{entry['skill']} {entry['args']}")
            else:
                remainder_parts.append(f"/{entry['skill']}")
        remainder_str = f"[CONTINUATION: {', '.join(remainder_parts)}]"
        return (target, remainder_str)
    # Last entry - no remainder
    return (target, None)


class TestParseConsumptionFormat:
    """Tests for parsing [CONTINUATION: ...] format."""

    @pytest.mark.parametrize(
        ("input_str", "expected"),
        [
            ("[CONTINUATION: /commit]", [("commit", "")]),
            ("[CONTINUATION: /handoff]", [("handoff", "")]),
            (
                "[CONTINUATION: /plan, /execute, /commit]",
                [("plan", ""), ("execute", ""), ("commit", "")],
            ),
            (
                "[CONTINUATION: /plan-adhoc foo, /orchestrate, /commit]",
                [("plan-adhoc", "foo"), ("orchestrate", ""), ("commit", "")],
            ),
            ("[CONTINUATION:  /a ,  /b  ,  /c  ]", [("a", ""), ("b", ""), ("c", "")]),
        ],
        ids=[
            "single",
            "single-with-args",
            "multiple",
            "multiple-with-args",
            "whitespace",
        ],
    )
    def test_parse_valid_entries(
        self, input_str: str, expected: list[tuple[str, str]]
    ) -> None:
        """Parse valid continuation strings."""
        entries = parse_continuation_string(input_str)
        assert entries is not None
        assert len(entries) == len(expected)
        for entry, (skill, args) in zip(entries, expected, strict=False):
            assert entry["skill"] == skill
            assert entry["args"] == args

    def test_parse_complex_args(self) -> None:
        """Parse entry with complex arguments."""
        entries = parse_continuation_string(
            "[CONTINUATION: /design plans/myplan --verbose]"
        )
        assert entries is not None
        assert entries[0]["skill"] == "design"
        assert "plans/myplan" in entries[0]["args"]
        assert "--verbose" in entries[0]["args"]

    @pytest.mark.parametrize(
        "input_str",
        ["[CONTINUATION: ]", "some regular args", "[CONTINUATION: /a, /b", None],
        ids=["empty", "no-marker", "malformed", "none"],
    )
    def test_parse_returns_none(self, input_str: str | None) -> None:
        """Return None for invalid/empty/missing continuation."""
        entries = parse_continuation_string(input_str)
        assert entries is None


class TestPeelFirstEntry:
    """Tests for peel-first-pass-remainder protocol."""

    def test_peel_single_entry(self) -> None:
        """Single entry peels to (target, None)."""
        target, remainder = peel_continuation("[CONTINUATION: /commit]")
        assert target is not None
        assert target["skill"] == "commit"
        assert target["args"] == ""
        assert remainder is None

    def test_peel_first_of_three(self) -> None:
        """First of three peels to (target, remainder with 2)."""
        target, remainder = peel_continuation("[CONTINUATION: /design, /plan, /commit]")
        assert target is not None
        assert target["skill"] == "design"
        assert remainder is not None
        assert "/plan" in remainder
        assert "/commit" in remainder

    def test_peel_with_args(self) -> None:
        """Entry with arguments preserves args in target."""
        target, remainder = peel_continuation("[CONTINUATION: /handoff, /commit]")
        assert target is not None
        assert target["skill"] == "handoff"
        assert target["args"] == ""
        assert remainder is not None
        assert "/commit" in remainder

    @pytest.mark.parametrize(
        "input_str",
        ["some args without continuation", "   "],
        ids=["no-marker", "whitespace-only"],
    )
    def test_peel_returns_none_none(self, input_str: str) -> None:
        """Return (None, None) when no valid continuation."""
        target, remainder = peel_continuation(input_str)
        assert target is None
        assert remainder is None

    def test_peel_preserves_complex_args_in_remainder(self) -> None:
        """Complex arguments preserved in remainder entries."""
        target, remainder = peel_continuation(
            "[CONTINUATION: /design foo, /plan-adhoc --verbose bar, /commit]"
        )
        assert target is not None
        assert target["skill"] == "design"
        assert target["args"] == "foo"
        assert remainder is not None
        assert "plan-adhoc" in remainder
        assert "--verbose" in remainder

    def test_peel_three_entry_sequence(self) -> None:
        """Full three-entry peel sequence exhausts to terminal."""
        target1, r1 = peel_continuation("[CONTINUATION: /a arg1, /b arg2, /c]")
        assert target1 is not None
        assert r1 is not None
        assert target1["skill"] == "a"
        assert target1["args"] == "arg1"

        target2, r2 = peel_continuation(r1)
        assert target2 is not None
        assert r2 is not None
        assert target2["skill"] == "b"
        assert target2["args"] == "arg2"
        assert "/a" not in r2

        target3, r3 = peel_continuation(r2)
        assert target3 is not None
        assert target3["skill"] == "c"
        assert r3 is None


class TestConsumptionProtocol:
    """Integration tests for the cooperative skill consumption protocol."""

    def test_skill_receives_continuation_in_additionalcontext(self) -> None:
        """First skill receives continuation from additionalContext."""
        entries = parse_continuation_string("[CONTINUATION: /plan-adhoc, /commit]")
        assert entries is not None
        assert entries[0]["skill"] == "plan-adhoc"

    def test_skill_receives_continuation_in_args_suffix(self) -> None:
        """Chained skill receives continuation in args suffix."""
        target, remainder = peel_continuation("plans/foo [CONTINUATION: /commit]")
        assert target is not None
        assert target["skill"] == "commit"
        assert remainder is None

    def test_skill_consumption_protocol_step_by_step(self) -> None:
        """Complete consumption: design peels plan, plan peels commit."""
        target, remainder = peel_continuation("[CONTINUATION: /plan, /commit]")
        assert target is not None
        assert target["skill"] == "plan"

        tail_call_args = f"plans/foo {remainder}" if remainder else "plans/foo"
        target2, remainder2 = peel_continuation(tail_call_args)
        assert target2 is not None
        assert target2["skill"] == "commit"
        assert remainder2 is None

    def test_continuation_with_embedded_path_slashes(self) -> None:
        """Path-like args with slashes parsed correctly."""
        entries = parse_continuation_string(
            "[CONTINUATION: /design plans/foo/bar, /commit]"
        )
        assert entries is not None
        assert entries[0]["skill"] == "design"
        assert "plans/foo/bar" in entries[0]["args"]
        assert entries[1]["skill"] == "commit"


class TestConsumptionEdgeCases:
    """Edge cases in consumption protocol."""

    def test_comma_separated_without_spaces(self) -> None:
        """Parse entries separated by commas without spaces."""
        entries = parse_continuation_string("[CONTINUATION: /a,/b,/c]")
        assert entries is not None
        assert [e["skill"] for e in entries] == ["a", "b", "c"]

    def test_skill_name_with_underscore(self) -> None:
        """Handle skill names with underscores."""
        target, _ = peel_continuation("[CONTINUATION: /plan_adhoc arg, /commit]")
        assert target is not None
        assert target["skill"] == "plan_adhoc"

    def test_args_with_multiple_flags(self) -> None:
        """Preserve multiple flags in arguments."""
        entries = parse_continuation_string(
            "[CONTINUATION: /design plans/foo --verbose  --quiet]"
        )
        assert entries is not None
        assert "--verbose" in entries[0]["args"]
        assert "--quiet" in entries[0]["args"]

    def test_newlines_in_continuation_string(self) -> None:
        """Handle continuation strings with embedded newlines."""
        entries = parse_continuation_string("[CONTINUATION: /plan-adhoc,\n/commit]")
        assert entries is not None
        assert len(entries) == 2

    def test_extra_whitespace_normalized(self) -> None:
        """Extra whitespace normalized in parsing."""
        target, remainder = peel_continuation(
            "[CONTINUATION:   /design   plans/foo   ,   /commit   ]"
        )
        assert target is not None
        assert target["skill"] == "design"
        assert "plans/foo" in target["args"]
        assert remainder is not None
        assert "/commit" in remainder


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
