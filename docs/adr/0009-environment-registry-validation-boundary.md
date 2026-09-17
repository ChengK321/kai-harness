# ADR-0009 Environment Registry Validation Boundary

Status: Proposed / V0.9-D1

## Context

Environment Registry provides a reference point for Kai Control Plane to identify environments and declared capabilities.

The Registry must remain smaller than a CMDB, IAM system, or execution platform.

## Decision

Registry validation is limited to contract integrity:

- required identity fields exist
- declared values follow schema
- duplicate identities are rejected
- capability references are syntactically valid

Registry validation does not prove:

- user authorization
- operational safety
- execution permission
- capability availability at runtime

## Data Ownership

```
Registry
   |
   +-- identity reference
   +-- capability declaration

External Systems
   |
   +-- authentication
   +-- authorization
   +-- execution
   +-- runtime state
```

## Consequences

The Registry remains a thin control-plane component.

Future adapters must not move execution, secrets, or workflow responsibility into Registry.

## Rejected Alternatives

### Registry as CMDB

Rejected because asset lifecycle management is outside Kai scope.

### Registry as Tool Marketplace

Rejected because capability declaration is not tool distribution or execution.

### Registry as Permission System

Rejected because authorization requires trusted identity and policy systems.
