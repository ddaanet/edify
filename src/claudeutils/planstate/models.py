"""Data models for plan state."""

from dataclasses import dataclass


@dataclass
class VetChain:
    """Source artifact → report mapping."""

    source: str
    report: str | None
    stale: bool = False
    source_mtime: float = 0.0
    report_mtime: float | None = None


@dataclass
class VetStatus:
    """Vet chain status for all source artifacts in a plan."""

    chains: list[VetChain]

    @property
    def any_stale(self) -> bool:
        """Check if any chain is stale."""
        return any(chain.stale for chain in self.chains)


@dataclass
class PlanState:
    """Plan state inferred from directory artifacts."""

    name: str
    status: str
    next_action: str
    gate: str | None
    artifacts: set[str]
