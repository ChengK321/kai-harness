# ADR-0015 Capability Reference Boundary

Status: Proposed

## Context

Kai needs to associate environments with available capabilities without duplicating existing tool systems.

## Decision

Capability Reference is a governance association layer only.

It does not execute, discover, install, authorize, or schedule capabilities.

## Consequences

Kai remains a thin Control Plane and reuses MCP, APIs, ROS2 and other existing execution systems.
