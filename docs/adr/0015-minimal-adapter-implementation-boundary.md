# ADR-0015 Minimal Capability Adapter Implementation Boundary

Status: Proposed

## Context

Kai already contains Observation related components. Adding a standalone Provider framework would duplicate environment access and create unnecessary abstraction layers.

## Decision

Implement only a minimal adapter layer.

The adapter:

- consumes existing observation data;
- maps evidence to capability references;
- connects verification contracts.

The adapter does not:

- execute environment operations;
- own credentials;
- manage workflows;
- provide generic tool execution.

## Consequence

The system keeps a single observation path:

```text
Environment
    |
    v
Existing Observation
    |
    v
Capability Adapter
    |
    v
Governance / Verification
```

Future write capabilities require separate review.
