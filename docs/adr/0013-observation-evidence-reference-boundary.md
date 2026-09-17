# ADR-0013 Observation Evidence Reference Boundary

Status: Proposed

## Context

Governance validation requires linking decisions with observed facts. Directly copying Observation data into Kai would duplicate telemetry responsibilities.

## Decision

Kai stores or references evidence metadata only. The source Observation remains owned by the Provider.

Reference relationships:

```text
Environment Registry
        |
        v
Observation Provider
        |
        v
Observation Evidence
        |
        v
Governance Verification
```

## Consequences

Benefits:

- avoids telemetry platform duplication
- preserves evidence traceability
- keeps Observation and Action boundaries separate

Limitations:

- evidence freshness must be defined by the consumer
- provider trust remains external responsibility
- unknown verification results must be preserved

## Rejected Alternatives

### Copy all Observation data into Kai

Rejected because Kai would become a telemetry storage platform.

### Trigger actions from evidence automatically

Rejected because Observation is evidence, not decision logic.
