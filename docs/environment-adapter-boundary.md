# Kai Environment Adapter Boundary V0.9

## 1. Purpose

Environment Adapter connects Kai contracts with external environments without owning environment execution.

## Boundary

```
                 Kai
                  |
        ----------------------
        | Environment Adapter |
        ----------------------
                  |
        External Environment
```

## 2. Adapter Responsibilities

Allowed:

- convert environment identity
- collect observations
- expose capability metadata
- return verification evidence references

Not allowed:

- execute arbitrary commands
- implement retry logic
- make business decisions
- replace domain controllers

## 3. Observation Path

```
Environment State
       |
       v
Adapter Collection
       |
       v
Observation Contract
       |
       v
Governance Context
```

## 4. Capability Path

```
Capability Declaration
       |
       v
Governance Intent
       |
       v
Existing Tool / MCP / Domain API
       |
       v
Environment
```

The Adapter does not become an Executor.

## 5. Failure Semantics

The adapter must preserve:

- unavailable
- stale
- unknown
- verification_failed

No failure automatically generates repair actions.

## 6. Review Requirement

Every new adapter requires:

- environment ownership definition
- identity mapping
- permission boundary
- evidence source
- negative tests
