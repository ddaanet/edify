"""Core types and parsing for the ``edify check`` verification command."""

import enum
import re
from dataclasses import dataclass, field


class CheckStatus(enum.StrEnum):
    """Outcome of a CrossHair verification run."""

    VERIFIED = "verified"
    REFUTED = "refuted"
    ERROR = "error"


@dataclass(frozen=True)
class Finding:
    """A single counterexample CrossHair reported."""

    location: str
    message: str


@dataclass(frozen=True)
class CheckResult:
    """Structured result of checking a target against its contract."""

    status: CheckStatus
    target: str
    findings: tuple[Finding, ...] = ()
    detail: str = field(default="")


def build_crosshair_argv(
    target: str,
    *,
    per_condition_timeout: float | None = None,
) -> list[str]:
    """Build the argv for invoking CrossHair's check command on a target.

    Args:
        target: A file path or a dotted ``module.func`` CrossHair target.
        per_condition_timeout: Optional CrossHair ``--per_condition_timeout``.

    Returns:
        The argv list to pass to ``subprocess.run``.
    """
    argv = ["crosshair", "check"]
    if per_condition_timeout is not None:
        argv.append(f"--per_condition_timeout={per_condition_timeout}")
    argv.append(target)
    return argv


_FINDING_RE = re.compile(r"^(?P<location>.+?:\d+): error: (?P<message>.*)$")


def parse_crosshair_output(
    exit_code: int,
    stdout: str,
    stderr: str,
    *,
    target: str,
) -> CheckResult:
    """Map a CrossHair run to a CheckResult.

    Exit codes (CrossHair contract): 0 = no counterexample within budget,
    1 = counterexample(s) found, 2 (or other) = error.

    Args:
        exit_code: CrossHair process return code.
        stdout: Captured standard output (machine-readable error lines).
        stderr: Captured standard error (context for errors).
        target: The target that was checked, echoed into the result.

    Returns:
        A CheckResult whose status reflects the exit code.
    """
    if exit_code == 0:
        return CheckResult(status=CheckStatus.VERIFIED, target=target)
    if exit_code == 1:
        findings = tuple(
            Finding(
                location=match.group("location"),
                message=match.group("message"),
            )
            for line in stdout.splitlines()
            if (match := _FINDING_RE.match(line.strip()))
        )
        return CheckResult(
            status=CheckStatus.REFUTED,
            target=target,
            findings=findings,
            detail=stdout.strip(),
        )
    return CheckResult(
        status=CheckStatus.ERROR,
        target=target,
        detail=(stderr.strip() or stdout.strip()),
    )
