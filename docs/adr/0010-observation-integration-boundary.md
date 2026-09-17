# ADR-0010 Observation Integration Boundary

Status: Proposed / V0.9-D2

## Context

Kai already defines Observation Contract and Environment Registry. Integration must connect them without creating a telemetry platform or execution runtime.

## Decision

Observation Integration follows:

```text
Environment Registry
        |
        v
Trusted Environment Adapter
        |
        v
Observation Provider
        |
        v
Observation Contract
```

Adapters and providers are read-only by default.

## Consequences

Positive:
- Environment identity becomes explicit.
- Observation remains portable.
- Existing telemetry ecosystems can be reused.

Negative:
- Adapter trust must be managed externally.
- Observation freshness and completeness must be represented.

## Rejected Alternatives

### Build Kai Telemetry Platform

Rejected. Existing ecosystems already provide metrics, traces and storage.

### Let Observation Trigger Actions

Rejected. Observation is evidence, not decision logic.

### Put Secrets in Adapter

Rejected. Credentials and identity management belong to external security systems.

## Future

Specific adapters such as VPS or ROS2 should prove concrete value before expanding contracts.
