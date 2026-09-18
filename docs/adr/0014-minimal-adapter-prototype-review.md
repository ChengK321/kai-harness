# ADR-0014 Minimal Capability Adapter Prototype Review

Status: Proposed

## Context

Kai already contains Observation and Registry-related components. Adding another provider abstraction may create duplicate data paths and unclear ownership.

## Decision

The V1.1 prototype uses a minimal adapter boundary instead of a new provider framework.

```text
Existing Observer
        |
        v
Capability Adapter
        |
        v
Capability Reference
        |
        v
Verification Contract
```

## Consequences

Positive:

- avoids duplicate observation pipelines;
- keeps Kai as a control plane;
- preserves external execution ownership.

Constraints:

- adapter is not an executor;
- adapter cannot mutate environment state;
- verification remains independent.

## Rejected Alternatives

### Generic Provider Framework

Rejected because it introduces a second extension system before a concrete need exists.

### Kai Executor

Rejected because execution belongs to external capability providers or environment systems.

## Future

Only after a real controlled use case demonstrates a gap should additional capability abstractions be introduced.
