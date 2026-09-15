"""Delegate local observation to the existing VPS adapter without retaining data."""

from typing import Protocol

from vps_observer import VPSObserver


class ObservationProvider(Protocol):
    """Return Observation Contract V1.0 data for an environment."""

    def get_observation(self, environment_id: str) -> dict: ...


class ObservationProviderError(RuntimeError):
    """The adapter could not produce an observation."""


class VPSObserverProvider:
    """Stateless bridge to the local read-only VPSObserver."""

    __slots__ = ()

    def get_observation(self, environment_id: str) -> dict:
        if not isinstance(environment_id, str) or not environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        try:
            return VPSObserver().collect(environment_id).to_observation()
        except Exception:
            # Unexpected adapter failures are distinct from partial/failed observations.
            # Suppress potentially sensitive adapter exception messages and tracebacks.
            raise ObservationProviderError("VPS observation adapter failed.") from None
