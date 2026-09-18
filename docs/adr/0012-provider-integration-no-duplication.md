# ADR-0012 Provider Integration No Duplication

Status: Proposed

## Context

Kai already contains Observation related components. Introducing another provider layer without a clear boundary may create duplicated responsibility.

## Decision

Capability Provider is an integration boundary, not a replacement for Observation.

Kai owns:

- capability reference
- governance validation
- verification association

External components own:

- environment access
- domain operation
- evidence production

## Rejected Alternatives

### Generic Provider Framework

Rejected because it duplicates mature ecosystems and increases platform scope.

### Executor Based Provider

Rejected because execution control is outside Kai's responsibility.

### Duplicate Observer

Rejected because Observation and Capability Provider would compete as sources of truth.

## Consequences

Future implementation must first prove an existing component cannot satisfy the required contract before adding new code.
