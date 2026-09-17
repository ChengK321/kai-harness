# ADR-0011 Observation Identity Binding

Status: Proposed / V0.9-D2.1

## Context

Observation data must be associated with a known environment. Without a stable identity boundary, an Observation Provider could report data from an unknown or incorrect environment.

Kai must not become a monitoring platform or identity authority. Environment identity belongs to Registry.

## Decision

`environment_id` is the primary identity reference shared by:

```
Environment Registry
        |
        v
Observation Provider
        |
        v
Observation Contract
```

The Provider may collect environment facts, but it does not create trusted identity.

## Rules

- Registry owns environment registration.
- Provider references registered identity.
- Observation Contract carries identity reference.
- Consumer validates identity relationship before using evidence.

## Rejected

- Provider-generated identity as trust source.
- Embedding credentials in Observation.
- Turning Observation metadata into IAM.
- Using Observation as a CMDB replacement.

## Consequence

Multiple providers may observe one environment, but identity resolution remains outside Provider responsibility.
