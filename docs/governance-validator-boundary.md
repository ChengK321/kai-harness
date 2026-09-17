# Kai Governance Validator Boundary

Status: V0.8 Freeze

## Responsibility

Governance Validator only performs offline contract validation:

- required field checking
- schema compatibility checking
- forbidden capability field detection
- risk declaration validation
- verification declaration validation

## Explicit Non-Responsibilities

Validator does not:

- authenticate identity
- issue approval
- execute tools
- call MCP
- run commands
- schedule workflows
- retry or rollback actions
- decide domain operations

## Output Meaning

Validation success means only:

> The Governance Intent satisfies Kai's declared contract rules.

It does not mean:

- authorized execution
- safe environment state
- successful operation
- approval authenticity

## Frozen Boundary

Future changes that add execution, orchestration or autonomous recovery require a new ADR and version review.
