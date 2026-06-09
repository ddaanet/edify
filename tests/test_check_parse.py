"""Tests for CrossHair output parsing and check result types."""

from edify.check import (
    CheckResult,
    CheckStatus,
    Finding,
    parse_crosshair_output,
)


def test_check_result_defaults() -> None:
    """A CheckResult has empty findings and detail by default."""
    result = CheckResult(status=CheckStatus.VERIFIED, target="foo.py")
    assert result.status is CheckStatus.VERIFIED
    assert result.target == "foo.py"
    assert result.findings == ()
    assert result.detail == ""


def test_finding_fields() -> None:
    """A Finding carries a location and a message."""
    finding = Finding(location="foo.py:3", message="boom")
    assert finding.location == "foo.py:3"
    assert finding.message == "boom"


def test_exit_zero_is_verified() -> None:
    """Exit code 0 means no counterexample within budget → verified."""
    result = parse_crosshair_output(0, "", "", target="foo.py")
    assert result.status is CheckStatus.VERIFIED
    assert result.findings == ()


def test_exit_one_parses_findings() -> None:
    """Exit code 1 parses `file:line: error: msg` lines into findings."""
    stdout = (
        "foo.py:3: error: false when calling head(xs = []) (which raises "
        "IndexError: list index out of range)\n"
    )
    result = parse_crosshair_output(1, stdout, "", target="foo.py")
    assert result.status is CheckStatus.REFUTED
    assert len(result.findings) == 1
    assert result.findings[0].location == "foo.py:3"
    assert "IndexError" in result.findings[0].message


def test_exit_two_is_error_with_detail() -> None:
    """Exit code 2 is an error; stderr is preserved as detail."""
    result = parse_crosshair_output(2, "", "Traceback: boom", target="foo.py")
    assert result.status is CheckStatus.ERROR
    assert result.detail == "Traceback: boom"


def test_findings_ignore_non_error_lines() -> None:
    """Non-matching stdout lines are ignored when collecting findings."""
    stdout = "Analyzing 1 function\nfoo.py:3: error: bad\n"
    result = parse_crosshair_output(1, stdout, "", target="foo.py")
    assert len(result.findings) == 1
    assert result.findings[0].message == "bad"
