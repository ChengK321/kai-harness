# ADR-0009 Capability Reference Binding

Status: Proposed

## Context

Kai V1.1 needs to connect governance decisions with external environment capabilities. A direct executor inside Kai would violate previous Control Plane boundaries.

## Decision

Capability is represented as a reference, not an implementation owned by Kai.

```
Intent
  |
  v
Governance Validation
  |
  v
Capability Reference
  |
  v
External Provider
  |
  v
Environment
```

## Consequences

Positive:

- avoids duplicate executor implementations;
- preserves external ownership of domain operations;
- allows different providers for VPS, robotics and other environments.

Constraints:

- capability metadata is not authorization;
- provider availability is not execution success;
- verification remains independent.

## Rejected Alternatives

### Kai Executor

Rejected because it moves environment operation logic into the control plane.

### Generic Command Bridge

Rejected because command forwarding creates an uncontrolled execution surface.

### Workflow Engine

Rejected because orchestration and recovery remain outside Kai scope.

## Future

Only introduce write capabilities after proving a concrete governance gap that cannot be solved by existing providers.
