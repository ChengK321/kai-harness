# ADR-0003 Action Governance Boundary

状态：Proposed / V0.8-D1 / 待人工审核。

## Context

Kai 是 AI Control Plane。D0 已识别 Action 与 Tool/Environment Contract 重复的风险。
普通只读工具通常已有足够的权限、参数和返回值；环境改变则还需要关联请求主体、
环境身份、风险、审批、执行证据及独立验证。拥有这些治理需求不意味着必须自建执行层。

## Decision

**Action 是治理层，不是执行层；Action = Governed Action Intent。**
意图描述一次经过策略约束的环境状态改变，说明谁请求、对哪个环境、为什么、风险、
审批要求和验证方式。Kai 只负责 Governance Boundary；外部 Agent 决策、规划，
Existing Tool / MCP / Environment Adapter 执行，机器人控制系统落实实时安全。

```text
Observation → Agent Reasoning → Action Intent → Governance Check → Approval
  → Existing Tool / MCP / Adapter → Environment → Observation Verification
```

只读查询不增加 Action 封装；已有工具满足全部治理需求时复用其能力和记录。
审批事实应有唯一受信来源，不以新层重复维护批准状态。

本提案细化 [ADR-0002](0002-action-boundary.md)：不要求创建 Action Adapter，
并将 D1 Action 意图限定为状态改变，D0 的 READONLY 查询继续使用既有工具。
旧权限枚举、历史文档和 require_tool_executor 等约束不因此修改或失效。

## Consequences

优点：避免重复 Tool Protocol，复用外部执行能力；支持机器人安全检查和验证证据关联，
同时把运动规划、碰撞检查和实时联锁留给专业系统。

限制：需要可信外部执行能力、身份和审批来源、可验证的证据与结果关联。
Kai 不能仅凭意图声明保证权限或物理安全；未知结果不允许自动补偿或重试。
目前执行禁用且相关观察能力未完成，因此本 ADR 不授权接入真实动作。

## Rejected Alternatives

### 1. Action = Tool Wrapper

仅复制工具名、参数和返回值没有治理增量，增加第二套 Schema 与调用层。
拒绝无条件包装所有工具；只在实际缺口存在时关联治理信息。

### 2. 自研 Executor

底层命令、协议执行和重试会扩大 Kai 的执行职责，与既有 Tool/MCP/环境服务重复。
拒绝用 Executor 填补旧配置约束；应另行审核兼容性迁移并保持默认拒绝。

### 3. 自研 Workflow Engine

治理流是责任顺序，不是任务图或自动恢复逻辑。拒绝加入规划、调度、补偿和修复循环。

## Future

未来复用 MCP + ROS2 + Environment Adapter，先证明单个场景的治理缺口，
再设计最小意图契约和受信关联。MCP 是工具交互协议，不是 Agent Runtime；
ROS2 的领域控制能力保持在执行环境内。

下一步仅建议在人工审核后进入 Governance Intent Schema 草案，不实现执行。
详见 [设计与案例](../action-governance-design.md)、[MCP 边界](../mcp-action-boundary.md)。
