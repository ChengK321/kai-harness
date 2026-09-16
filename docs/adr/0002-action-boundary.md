# ADR-0002 Action Boundary

Status: Proposed / V0.8-D0 / 待人工审核。

## Context

Kai 是 Agent Control Plane，V0.6 复用外部 Harness，V0.7 通过 Observation Provider
提供只读环境上下文。Agent 的未来动作请求需要受控边界，不能直接获得 shell 或环境凭据。
已有 V0.5 Tool/Environment Contract、权限和审批语义应复用，不能重新建立 Agent Runtime。

现有 Registry execution_enabled=false、require_tool_executor=true，当前 Runner 只读。
本 ADR 不解除这些限制；Action 设计不等于已具备可执行路径。

## Decision

选择逻辑上的 **Harness → Action Adapter** 边界，具体必须经过契约、验证与审批：

```text
Harness → Action Contract → Action Validator → Approval Check → Action Adapter → Environment
```

该简写不意味着 Harness 直接依赖具体 Adapter 实现，也不允许跳过任何门禁。
Harness 提交稳定的环境动作意图；控制面验证 allowlist、权限、审批、预算和审计；
Adapter 仅映射已授权动作并返回结果，不负责规划或权限决策。

观察路径继续为 Harness → Observation Provider → Observation Adapter。
动作后的核验仍通过只读 Provider，不给 Observation 添加执行接口。
权限复用 READONLY / CONTROLLED / ADMIN；默认拒绝，审批不能扩大授权。

require_tool_executor 的旧强制约束必须通过另行审核的版本化决策解决；
不能将 Action Adapter 默认为 Tool Executor，不能直接忽略字段来启用执行。

## Consequences

正面：隔离 Agent 与环境操作，复用既有权限语义，统一请求、结果和审计关联，
允许未来替换 VPS 或机器人 Adapter，保留 Observation 的只读边界。

代价：需维护契约版本、动作参数定义、审批绑定、结果语义和观察证据关联；
仍需环境最小权限，接口设计不能代替沙箱或机器人安全联锁。
当前旧执行约束及缺少服务状态观察会阻止直接上线，不能以设计完成宣称执行能力已完成。

## Rejected Alternatives

### Agent 直接调用工具

拒绝 Agent 绕过 Kai 授权边界直接调用环境 shell、SSH 或管理 API：无法可靠绑定
主体、资源、审批和审计。此决定不否定外部 Harness 已有的受限工具能力，
而是约束新增环境动作入口，不重写 Claude Code 的工具系统。

### 自研 Runtime

拒绝为环境动作重建 Agent loop、Planner、Memory Manager 或通用 Tool Executor。
这些超出单次请求控制职责，重复成熟 Harness 并扩大维护和安全范围。

### Workflow Engine

拒绝把动作边界扩展为步骤图、调度、自动恢复和补偿引擎。
复杂任务由外部 Agent 或既有专用系统承担；失败不授权下一步修复动作。

## Future

先审核 [Action 设计](../action-design.md)和 [Schema 草案](../action-schema-draft.md)，
确认旧契约映射、审批与执行上下文，再讨论离线验证。真实 Adapter 和 Environment 接入
需独立授权，不属于 D0。机器人控制和安全联锁始终由专业 Environment 实现。

本 ADR 路径为 docs/adr/0002-action-boundary.md；与 V0.6 架构文档内的 ADR-002 摘要
按完整路径区分，不重编号或改写历史 ADR。
