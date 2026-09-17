# ADR-0004 Governance Intent Contract

状态：Proposed / V0.8-D2 / 待人工审核。

## Context

D1 将 Action 定义为 Governed Action Intent。需要最小可校验的治理声明，
避免把 Tool 参数、Workflow 步骤或 Executor 命令重新包装为 Action。
结构合法、真实身份、审批有效及执行授权是不同问题。

## Decision

Governance Intent 仅描述 identity、environment、target、purpose、risk、
approval reference、verification requirement，并包含 version 和 intent_id 用于契约识别。
它不描述 execution，不提供 execute() 或自动调用语义。

采用 Draft 2020-12，所有对象封闭。身份来自认证入口，环境身份来自 Registry；
Schema 不把模型声明转成可信事实。
审批不是所有动作的必经人工步骤；受信政策决定要求，HIGH / CRITICAL 的结构约束要求审批。
审批引用可为空以表达待审批；非空也不代表批准。risk 不等于 permission。

## Consequences

优点：防止 Tool Protocol 重复建设，可与 MCP 及未来 ROS2 能力关联而不修改其接口；
声明与执行分离，可离线检查字段及未知属性。

限制：需要外部执行能力、认证入口、Registry 引用核验、可信审批和验证证据。
最小声明不能绑定完整执行参数，不构成执行令牌；外部集成必须另行落实精确操作与授权关联。
不因为省略执行字段而省略超时、幂等、安全联锁和审计的外部责任。

## Rejected Alternatives

1. **Action = Tool Wrapper**：复制工具名与调用参数没有治理增量，并形成第二套工具协议。
2. **Action = Workflow Node**：引入步骤、依赖、重试和补偿超出治理声明边界。
3. **Action = Executor Command**：把声明直接解释为命令会绕过既有执行系统及权限边界。

## Scope

本阶段只新增契约与文档，不实现执行、审批服务或自动修复；历史权限与 Registry 限制保持。
参考 [设计说明](../governance-intent-design.md)、
[Schema](../../configs/schema/governance-intent.schema.json)、
[ADR-0003](0003-action-governance-boundary.md)。
