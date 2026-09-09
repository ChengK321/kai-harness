# Changelog

本文件记录 Kai Infrastructure 的版本级变化。

## v0.5.0 — 2026-09-04

### Added

- 建立 Kai Infrastructure 基础目录与文档体系。
- 定义 Agent、Memory、Tool、MCP 和 Environment Core Contract。
- 定义 Agent Runtime V1.0 设计与任务生命周期状态机。
- 建立 Agent、Tool、Environment 和 MCP Registry Layer。
- 创建独立 Registry JSON Schema 命名空间。
- 实现 Registry Validator V1.1，包括重复 YAML Key、业务规则和跨 Registry 引用检查。
- 建立 Registry Snapshot V1.0 设计。
- 补齐五层 Memory 的 System Memory 目录。

### Fixed

- 统一 Memory Provenance 为 `source_type`、`source_id`、`created_by`、`confidence` 和 `verified`。
- 删除新 Memory Contract 对旧 `source` 字段的依赖，并定义旧记录迁移规则。
- 修复 Schema 失败后仍进入 Cross Reference 的安全路径。
- 将 Validator 各阶段的异常转换为结构化 Validation Report。

### Security

- 所有 Registry 保持 default deny。
- Tool 权限统一为 READONLY、CONTROLLED、ADMIN。
- ADMIN 和不可逆副作用必须进入人工审批路径。
- Agent 禁止直接访问 Memory 后端或执行系统命令。
- Validator 保持只读，不执行 Tool、不连接 Environment，并拒绝重复 YAML Key。
- 配置、Schema 和发布归档不保存凭据。

### Not Included

- Agent Runtime Implementation
- Policy Engine
- Tool Executor
- MCP Runtime
- Robot Adapter
