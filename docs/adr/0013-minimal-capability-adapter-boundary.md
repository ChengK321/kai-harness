# ADR-0013 Minimal Capability Adapter Boundary

Status: Proposed

## Context

Kai already contains Observation and Governance concepts. Introducing another generic Provider layer risks duplicate abstractions.

## Decision

Use a minimal capability adapter boundary.

The adapter connects existing environment observation capability with Kai capability references without owning execution.

```
Existing Observation
        |
        v
Minimal Adapter
        |
        v
Capability Reference
        |
        v
Governance Verification
```

## Consequences

Positive:

- avoids duplicate observation pipelines;
- keeps Kai as a control plane;
- enables future external capability integration.

Negative:

- real execution still requires an external trusted capability provider;
- adapter cannot solve authorization or safety by itself.

## Rejected Alternatives

- Generic provider framework: unnecessary abstraction.
- Kai executor: violates architecture boundary.
- Automatic remediation: introduces decision and workflow responsibilities.
