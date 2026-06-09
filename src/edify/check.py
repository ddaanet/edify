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
