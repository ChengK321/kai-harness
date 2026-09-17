# ADR-0006 Environment Adapter Boundary

Status: Proposed

## Context

V0.8 established Governance Intent and Validator boundaries. To integrate real environments, Kai needs a controlled connection point.

The risk is expanding Kai into an execution framework.

## Decision

Introduce Environment Adapter as a boundary layer only.

Adapter responsibilities:

- environment identity mapping
- observation conversion
- capability description
- verification evidence association

Adapter is not:

- executor
- workflow engine
- planner
- controller

## Consequences

Benefits:

- enables real environment integration
- keeps MCP and external tools reusable
- avoids duplicate execution systems

Costs:

- requires trusted external capabilities
- requires clear ownership of evidence
- requires environment identity management

## Rejected Alternatives

### Kai Executor

Rejected because it duplicates existing execution systems.

### Universal Environment Runtime

Rejected because different domains require different safety models.

## Future

Start with VPS/Linux integration. Expand only when a specific environment requires it.
