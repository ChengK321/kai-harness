# ADR-0010 Verification Integration Boundary

Status: Proposed

## Context

Capability Provider integration introduces a risk that execution responses are treated as final truth.

## Decision

Kai separates:

- execution evidence
- observation evidence
- verification result

A provider response alone cannot establish successful completion.

## Data Flow

```
Request
  |
  v
Capability Provider
  |
  v
Execution Evidence
  |
  v
Independent Verification
  |
  v
Result
```

## Rejected Alternatives

### Trust provider response as final state

Rejected because accepted commands may fail to achieve the intended environment state.

### Add automatic recovery loop

Rejected because planning and remediation are outside Kai responsibility.

## Consequences

Verification becomes a first-class boundary while keeping Kai independent from execution systems.
