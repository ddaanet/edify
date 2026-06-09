"""Integration tests for the check CLI handler (subprocess mocked)."""

import json

import pytest
from pytest_mock import MockerFixture

from edify.check import CheckResult, CheckStatus, Finding
from edify.check_cli import handle_check, run_crosshair
from edify.exceptions import CrossHairUnavailableError


def test_run_crosshair_maps_subprocess(mocker: MockerFixture) -> None:
    """run_crosshair runs the argv and parses the result."""
    completed = mocker.Mock(returncode=1, stdout="foo.py:3: error: bad", stderr="")
    mocker.patch("edify.check_cli.subprocess.run", return_value=completed)

    result = run_crosshair("foo.py")

    assert result.status is CheckStatus.REFUTED
    assert result.findings[0].message == "bad"


def test_run_crosshair_missing_binary(mocker: MockerFixture) -> None:
    """A missing crosshair executable raises CrossHairUnavailableError."""
    mocker.patch("edify.check_cli.subprocess.run", side_effect=FileNotFoundError)
    with pytest.raises(CrossHairUnavailableError):
        run_crosshair("foo.py")


def test_handle_check_verified_exits_zero(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A verified result prints a check line and exits 0."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(status=CheckStatus.VERIFIED, target="foo.py"),
    )
    with pytest.raises(SystemExit) as exc:
        handle_check("foo.py")
    assert exc.value.code == 0
    assert "verified" in capsys.readouterr().out


def test_handle_check_refuted_exits_one_json(
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A refuted result with --json prints structured findings and exits 1."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(
            status=CheckStatus.REFUTED,
            target="foo.py",
            findings=(Finding(location="foo.py:3", message="bad"),),
        ),
    )
    with pytest.raises(SystemExit) as exc:
        handle_check("foo.py", json_output=True)
    assert exc.value.code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "refuted"
    assert payload["findings"][0]["location"] == "foo.py:3"


def test_handle_check_error_exits_two(
    mocker: MockerFixture,
) -> None:
    """An error result exits with code 2."""
    mocker.patch(
        "edify.check_cli.run_crosshair",
        return_value=CheckResult(
            status=CheckStatus.ERROR, target="foo.py", detail="boom"
        ),
    )
    with pytest.raises(SystemExit) as exc:
        handle_check("foo.py")
    assert exc.value.code == 2
