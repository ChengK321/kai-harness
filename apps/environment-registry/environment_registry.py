"""Minimal Environment Registry prototype.

No persistence, network access, execution or permission management.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class EnvironmentRecord:
    environment_id: str
    environment_type: str
    trust_level: str
    capabilities: List[str]


class EnvironmentRegistry:
    def __init__(self):
        self._items: Dict[str, EnvironmentRecord] = {}

    def register(self, environment: EnvironmentRecord) -> None:
        if environment.environment_id in self._items:
            raise ValueError("environment already exists")
        self._items[environment.environment_id] = environment

    def get(self, environment_id: str) -> EnvironmentRecord:
        return self._items[environment_id]

    def has_capability(self, environment_id: str, capability: str) -> bool:
        return capability in self.get(environment_id).capabilities
