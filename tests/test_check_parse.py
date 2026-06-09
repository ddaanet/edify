"""Tests for CrossHair output parsing and check result types."""

from edify.check import CheckResult, CheckStatus, Finding


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
