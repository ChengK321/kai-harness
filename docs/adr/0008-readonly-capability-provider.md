# ADR-0008 Readonly Capability Provider Boundary

Status: Proposed

## Context

Kai V1.0 established Governance Boundary. The next step requires connecting external capabilities without moving execution responsibility into Kai.

## Decision

Introduce a minimal Capability Provider boundary.

The first provider is readonly only.

```
Kai
 |
Capability Reference
 |
Readonly Capability Provider
 |
Environment
```

## Accepted

- external capability integration
- evidence normalization
- readonly observation

## Rejected

- Kai owned executor
- shell command bridge
- workflow orchestration
- automatic remediation

## Consequence

Future controlled actions must prove that an existing provider already owns execution safety before Kai references them.
