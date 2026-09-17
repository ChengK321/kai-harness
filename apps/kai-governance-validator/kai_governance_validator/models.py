"""Plain, serializable offline validation reports."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    reason: str


@dataclass(frozen=True)
class GovernanceDecisionReport:
    """Offline contract validation result, not authorization or execution approval."""

    validation: str
    intent_id: str | None
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict:
        return {
            "validation": self.validation,
            "intent_id": self.intent_id,
            "checks": [asdict(check) for check in self.checks],
        }
