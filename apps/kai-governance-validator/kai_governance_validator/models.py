"""Plain, serializable offline decision reports."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    reason: str


@dataclass(frozen=True)
class GovernanceDecisionReport:
    status: str
    intent_id: str | None
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "intent_id": self.intent_id,
            "checks": [asdict(check) for check in self.checks],
        }
