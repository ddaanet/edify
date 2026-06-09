"""Core types and parsing for the ``edify check`` verification command."""

import enum
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
