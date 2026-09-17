# ADR-0014 Capability Reference Boundary

Status: Proposed

## Context

Kai needs a way to associate governed intents with environment capabilities without creating another tool protocol.

## Decision

Capability Reference is an identity and relationship layer only.

It maps:

```
Environment
    |
    v
Capability Reference
    |
    v
Existing MCP / Tool / Domain Adapter
```

It does not implement execution.

## Consequences

Positive:

- Reuses existing ecosystems.
- Keeps Kai as a thin Control Plane.
- Allows VPS and robotics environments to share governance concepts.

Limitations:

- Actual execution permission remains external.
- Capability declaration is not proof that an operation is safe.
- Runtime failures remain the responsibility of execution systems.

## Rejected Alternatives

### Capability as Tool Wrapper

Rejected because it duplicates existing protocols.

### Capability as Executor Registry

Rejected because it moves Kai into execution ownership.

### Capability Marketplace

Rejected because discovery and distribution are outside Kai scope.

## Future

Only add capability fields when a real governance requirement cannot be satisfied by existing protocols.
