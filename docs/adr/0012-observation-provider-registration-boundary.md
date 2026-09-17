# ADR-0012 Observation Provider Registration Boundary

Status: Proposed

## Context

V0.9 introduces Environment Integration. Observation sources need a stable reference without turning Kai into a monitoring platform.

## Decision

Observation Provider registration is metadata association only.

Kai may record:

- which provider can serve an environment
- which observation contract version is supported
- which readonly observation categories are declared

Kai does not own:

- provider deployment
- provider authentication
- provider credentials
- provider scheduling
- metric storage
- alerting

## Consequences

This keeps Observation as evidence production rather than telemetry infrastructure.

A provider failure is represented as missing or invalid observation evidence, not as a trigger for automatic repair.

## Rejected Alternatives

### Provider Marketplace

Rejected because discovery, installation and lifecycle management are outside Kai's control-plane boundary.

### Monitoring Platform

Rejected because existing telemetry ecosystems already provide this capability.

### Execution Adapter

Rejected because observation and action execution must remain separate.
