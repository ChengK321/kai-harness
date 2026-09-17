# Changelog

本文件记录 Kai Infrastructure 的版本级变化。

## v0.5.0 — 2026-09-04

### Added

- 建立 Kai Infrastructure 基础目录与文档体系。
- 定义 Agent、Memory、Tool、MCP 和 Environment Core Contract。
- 建立 Registry Layer 与 Validator 基础能力。

### Security

- 所有 Registry 保持 default deny。
- Tool 权限统一为 READONLY、CONTROLLED、ADMIN。
- Validator 保持只读。

## v0.6.0

### Added

- Added Kai Agent Control Plane architecture documentation.
- Added Claude Code harness execution baseline.

### Changed

- Repositioned Kai from standalone Agent Runtime toward thin Control Plane.

## v0.7.0

### Added

- Observation Contract V1.0
- Observation Adapter interface
- Observation Provider abstraction

### Architecture

- Established:

```
Harness → Observation Provider → Environment Adapter
```

- Observation remains read-only.

## v0.8.0

### Added

- Governance Intent Contract
- Governance Validator prototype
- Governance validation negative corpus
- Governance boundary ADRs

### Architecture

Established the Governance Control Plane boundary:

```
External Agent
      |
Governance Intent
      |
Contract Validation
      |
Existing Tool / MCP / Environment Capability
      |
Environment
```

### Security

- No Executor introduced.
- No Workflow Engine introduced.
- No Tool Protocol replacement introduced.
- No automatic remediation introduced.

### Freeze

V0.8 freezes Kai responsibility as a governance boundary layer, not an execution platform.
