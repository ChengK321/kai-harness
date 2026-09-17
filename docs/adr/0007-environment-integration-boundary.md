# ADR-0007 Environment Integration Boundary

Status: Proposed / V0.9-D0.5

## Context

V0.8 established Kai as a Governance Control Plane. V0.9 introduces Environment Integration.

The main risk is that connecting environments may gradually transform Kai into an execution framework.

## Decision

Kai introduces environment integration through boundaries, not execution ownership.

The following responsibilities remain external:

- Agent reasoning
- task planning
- workflow execution
- tool execution
- robot control
- infrastructure operation

Kai owns:

- environment identity association
- governance contract validation
- capability reference association
- observation and verification relationship

## Environment Registry

Environment Registry is a trust and identity index.

It must not become:

- infrastructure inventory
- credential manager
- deployment controller

## Adapter Design

Adapters translate external systems into Kai contracts.

Adapters do not execute arbitrary operations.

```
Environment
    |
    v
Adapter
    |
    v
Kai Contract
```

## Capability Decision

Kai must not create a universal executor.

Existing MCP tools, services and domain systems remain responsible for execution.

Capability references describe available trusted capabilities without owning their implementation.

## Verification Decision

Verification observes outcomes and associates evidence.

Verification failure does not trigger automatic repair.

## Consequences

Benefits:

- avoids duplicate execution frameworks
- preserves compatibility with MCP and domain systems
- keeps Kai suitable for VPS and Embodied AI scenarios

Limitations:

- requires trusted external systems
- does not provide autonomous recovery
- does not replace domain safety mechanisms

## Future

Future environment integrations must prove a missing governance boundary before adding new abstractions.
