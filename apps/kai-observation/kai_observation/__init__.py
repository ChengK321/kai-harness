"""Read-only Observation Provider interface."""

from .provider import ObservationProvider, ObservationProviderError, VPSObserverProvider

__all__ = ["ObservationProvider", "ObservationProviderError", "VPSObserverProvider"]
