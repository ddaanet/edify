"""CLI handler for the ``check`` subcommand."""

import json
import subprocess
import sys

from edify.check import (
    CheckResult,
    CheckStatus,
    build_crosshair_argv,
    parse_crosshair_output,
)
from edify.exceptions import CrossHairUnavailableError

_EXIT_CODES = {
    CheckStatus.VERIFIED: 0,
    CheckStatus.REFUTED: 1,
    CheckStatus.ERROR: 2,
}


def run_crosshair(
    target: str,
    *,
    per_condition_timeout: float | None = None,
) -> CheckResult:
    """Run CrossHair on a target and return a structured result.

    Raises:
        CrossHairUnavailableError: if the crosshair executable is missing.
    """
    argv = build_crosshair_argv(target, per_condition_timeout=per_condition_timeout)
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise CrossHairUnavailableError from exc
    return parse_crosshair_output(
        proc.returncode, proc.stdout, proc.stderr, target=target
    )


_VACUITY_WARNING = (
    "warning: verified at CrossHair's default budget (no --timeout given); "
    "this verdict may be vacuous if the contract's interesting paths were "
    "never explored. Re-run with --timeout to harden it."
)


def _print_human(result: CheckResult, per_condition_timeout: float | None) -> None:
    """Print a human-readable rendering of a check result."""
    if result.status is CheckStatus.VERIFIED:
        if per_condition_timeout is None:
            print(
                f"verified: {result.target} "
                "(no counterexample within CrossHair's default budget)"
            )
            print(_VACUITY_WARNING, file=sys.stderr)
        else:
            print(
                f"verified: {result.target} "
                f"(no counterexample within {per_condition_timeout} s "
                "per-condition budget)"
            )
    elif result.status is CheckStatus.REFUTED:
        print(f"refuted: {result.target}")
        for finding in result.findings:
            print(f"  {finding.location}: {finding.message}")
    else:
        print(f"error: {result.target}", file=sys.stderr)
        if result.detail:
            print(result.detail, file=sys.stderr)


def handle_check(
    target: str,
    *,
    per_condition_timeout: float | None = None,
    json_output: bool = False,
) -> None:
    """Run a check and exit with a status-derived code.

    Exit codes: 0 verified, 1 refuted, 2 error.
    """
    result = run_crosshair(target, per_condition_timeout=per_condition_timeout)
    vacuity_warning = (
        result.status is CheckStatus.VERIFIED and per_condition_timeout is None
    )
    if json_output:
        print(
            json.dumps(
                {
                    "status": result.status.value,
                    "target": result.target,
                    "findings": [
                        {"location": f.location, "message": f.message}
                        for f in result.findings
                    ],
                    "detail": result.detail,
                    "budget": per_condition_timeout,
                    "vacuity_warning": vacuity_warning,
                }
            )
        )
    else:
        _print_human(result, per_condition_timeout)
    sys.exit(_EXIT_CODES[result.status])
