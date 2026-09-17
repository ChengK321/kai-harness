# Governance Contract Boundary

Status: V0.8-D3.6 / Design Hardening

This document freezes the responsibility boundary between Governance Intent Schema, Validator, Approval and Execution systems.

## Responsibility separation

```
Governance Intent Schema
        |
        | structure validation
        v
Governance Validator
        |
        | offline governance boundary checks
        v
External Approval / Identity / Policy Sources
        |
        | trusted authorization facts
        v
Existing Tool / MCP / Environment Adapter
        |
        v
Environment
```

## Schema responsibility

The Schema defines structural constraints:

- required fields
- field types
- closed object boundaries
- contract version

Schema validity does not imply:

- requester identity is authentic
- approval exists
- execution is permitted
- operation succeeded

## Validator responsibility

Validator only evaluates whether an intent satisfies offline contract rules.

Validator may check:

- required governance fields
- risk declaration format
- forbidden execution fields
- verification declaration
- contract compatibility

Validator does not:

- authenticate users
- approve actions
- call tools
- execute commands
- schedule workflows
- retry failed operations

A successful validation result means only:

`validation=passed`

It does not mean:

`approved=true`

or:

`execution_allowed=true`

## Approval responsibility

Approval remains an external trusted fact source.

The existence of an approval reference is not approval itself.

The Validator does not verify or issue approval records.

## Execution responsibility

Execution remains owned by existing systems:

- MCP tools
- deployment systems
- robot controllers
- environment adapters

Kai does not become an executor by validating an intent.

## Negative contract examples

The following must never enter Governance Intent:

```json
{
  "command": "systemctl restart nginx",
  "executor": "bash",
  "workflow": "repair_pipeline"
}
```

These represent execution logic rather than governance information.

## Future changes

Any introduction of:

- approval engine
- executor
- workflow scheduler
- automatic repair loop

requires a new ADR review.
