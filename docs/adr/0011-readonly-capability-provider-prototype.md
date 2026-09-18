# ADR-0011 Readonly Capability Provider Prototype

## Context

Kai V1.0 established Observation, Governance and Capability Reference boundaries. V1.1 requires proving external capability integration without turning Kai into an execution platform.

## Decision

Introduce a readonly Capability Provider prototype.

The provider exposes facts from an environment. It does not execute environment changes.

```
Kai
 |
 | capability reference
 v
Readonly Provider
 |
 | evidence
 v
Environment Observation
```

## Accepted

- readonly service queries
- health checks
- evidence generation
- verification integration

## Rejected

- command executor
- SSH bridge
- restart wrapper
- workflow engine
- automatic remediation

## Consequences

The prototype validates the integration boundary while keeping execution responsibility outside Kai.
