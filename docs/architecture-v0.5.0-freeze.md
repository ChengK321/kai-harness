# Kai Infrastructure V0.5.0 Freeze

## 1. 冻结目标

V0.5.0 冻结 Kai AI Infrastructure 的基础目录、核心接口、Memory 契约、Registry 描述及 Registry Validator 安全边界，为后续 Runtime 原型提供稳定基线。

冻结表示本版本的既有字段、状态、权限枚举和安全语义不再原位破坏性修改。后续修复必须保持兼容；破坏性变化应进入新的契约版本。

## 2. 已冻结组件

### Infrastructure Layout

冻结 `/opt/kai/` 下 apps、configs、data、docs、logs、runtime、versions、backup 及五层 Memory 目录约定。目录存在不代表对应运行组件已经实现或启用。

### Core Contract

冻结 Agent、Memory、Tool 和 Environment 的接口边界，以及任务生命周期、错误分类和事件信封的 V1.0 语义。接口保持与具体 LLM、Agent 框架和存储后端解耦。

### Memory Contract

冻结五层 Memory 模型和统一 Provenance：`source_type`、`source_id`、`created_by`、`confidence`、`verified`。Memory Manager 是唯一访问入口；旧 `source` 只允许按迁移规范转换。

### Registry Layer

冻结 Agent、Tool、Environment 和 MCP Registry 的命名空间、默认拒绝原则、权限枚举、独立 Registry Schema 目录及跨 Registry 引用方向。

### Registry Validator

冻结 Validator V1.1 的验证顺序：YAML Parse、Schema Validation、Business Rules、Cross Reference、JSON Report。Schema 失败不得进入 Cross Reference，所有验证异常必须转换为报告错误。

## 3. 未包含组件

V0.5.0 不包含以下运行实现：

- Agent Runtime Implementation
- Policy Engine
- Tool Executor
- MCP Runtime
- Robot Adapter

相关文档仅作为后续设计输入，不代表组件已经部署、连接或具备生产能力。

## 4. 兼容性原则

- V0.5.x 只允许向后兼容的修复、可选字段和安全收紧。
- 已发布字段不得删除、改义或复用；权限与未知能力继续默认拒绝。
- Core Contract Schema 与 Registry Schema 保持命名空间隔离。
- 新 Agent、Tool、MCP Server 和 Environment 必须显式注册并通过对应 Schema 与 Validator。
- Runtime 未来必须绑定已验证的 Registry Snapshot；注册不等于启用，启用不等于授权。
- 不确定的迁移、引用、权限或副作用必须 fail closed。

## 5. 下一阶段路线

### V0.5.1 Snapshot

设计并实现只读 Registry Snapshot 构建流程，包括规范化排序、Registry 与 Schema 版本、Validator 版本、UTC 时间、SHA-256 清单、任务绑定和回滚验证。

### V0.6 Runtime Prototype

基于冻结契约开发最小 Agent Runtime 原型，优先实现任务状态机、Adapter 边界、只读 Registry Snapshot 加载、超时和取消；不绕过 Memory Manager、Policy Engine 或 Tool Executor 的安全边界。
