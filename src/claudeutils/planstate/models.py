"""Data models for plan state."""

from dataclasses import dataclass


@dataclass
class VetChain:
    """Source artifact → report mapping."""

    source: str
    report: str
    stale: bool = False
    source_mtime: float = 0.0
    report_mtime: float = 0.0


@dataclass
class VetStatus:
    """Vet chain status for all source artifacts in a plan."""

    chains: list[VetChain]


@dataclass
class PlanState:
    """Plan state inferred from directory artifacts."""

    name: str
    status: str
    next_action: str
    gate: str | None
    artifacts: set[str]
