"""Local diagnostics are separate from the stable Observation contract."""

from dataclasses import dataclass, field
from typing import Protocol


class ServiceObserver(Protocol):
    """Reserved interface only; VPSObserver does not invoke service collectors."""

    def collect(self) -> dict[str, dict[str, str]]: ...


@dataclass(frozen=True)
class Capacity:
    total_bytes: int
    used_bytes: int

    @property
    def percent(self) -> float:
        return self.used_bytes / self.total_bytes * 100


@dataclass
class RawObservation:
    environment_id: str
    timestamp: str
    hostname: str | None = None
    os: str | None = None
    kernel: str | None = None
    cpu: float | None = None
    memory: Capacity | None = None
    disk: Capacity | None = None
    errors: list[dict[str, str]] = field(default_factory=list)

    @property
    def resources(self) -> dict[str, float | None]:
        return {
            "cpu_percent": self.cpu,
            "memory_percent": self.memory.percent if self.memory else None,
            "disk_percent": self.disk.percent if self.disk else None,
        }

    def to_observation(self) -> dict:
        """Project collected values onto Observation 1.0; omit unavailable data."""
        system = {}
        if self.cpu is not None:
            system["cpu"] = {"usage_percent": self.cpu}
        for name in ("memory", "disk"):
            value = getattr(self, name)
            if value is not None:
                system[name] = {"total_bytes": value.total_bytes, "used_bytes": value.used_bytes}
        any_data = any(value is not None for value in (
            self.hostname, self.os, self.kernel, self.cpu, self.memory, self.disk
        ))
        status = "complete" if not self.errors else ("partial" if any_data else "failed")
        return {
            "version": "1.0",
            "timestamp": self.timestamp,
            "environment_id": self.environment_id,
            "system": system,
            "metadata": {
                "adapter_type": "vps",
                "adapter_version": "0.1.0",
                "collection_status": status,
                "errors": [dict(error) for error in self.errors],
            },
        }
