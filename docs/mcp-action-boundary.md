# MCP / Tool / Action Governance Boundary — V0.8-D1

状态：设计提案，待人工审核。**Kai 不替代 MCP，不创建新的 Tool Protocol。**
本文是 Kai 职责划分，不修改 MCP 规范，也不声明当前 Harness 已接入 MCP。

## MCP Tool 与 Kai Governance

| 维度 | MCP Tool / 既有执行服务 | Kai Governance |
| --- | --- | --- |
| 能力暴露 | 暴露已有工具能力和调用接口 | 关联允许使用的能力，不创建第二个市场或发现协议。 |
| 参数调用 | 接受工具参数、返回工具结果 | 将获准意图绑定到精确参数，防止审批后替换。 |
| 资源访问 | 由服务实现访问和原生权限检查 | 核对环境身份、资源范围及委托主体。 |
| 权限 | 服务端继续执行访问控制 | 核对 Kai 授权范围与环境策略，不取代服务端鉴权。 |
| 审批 | 若已有可信审批服务，继续作为事实来源 | 核验和引用审批，不另建冲突的批准记录。 |
| 审计 | 提供工具调用及操作回执 | 关联请求者、意图、授权、回执和证据。 |
| 验证 | 返回操作结果，必要时提供领域证据 | 关联独立 Observation 和预先确定的完成条件。 |

Tool 是能力，Governed Action Intent 是受治理的环境改变意图。
它们可以描述同一次操作；Action 不需要成为另一个远程调用协议或可执行对象。
MCP 并不禁止实现方提供审批、审计或验证能力；若现有服务已经满足要求，Kai 应复用，
而不是假设 MCP 天生缺失这些能力并重复建设。

## 何时不增加封装

query_status、read_file、get_observation 等只读调用，只要已有受信权限、参数和返回值
覆盖实际需求，就直接复用原 Tool 或 Provider。读取仍需环境和敏感数据边界，
不能仅凭工具名称或只读声明推定安全。

对于已经具有完整治理能力的写工具，Kai 只保留必要关联引用；不重复注册同名 Action Tool，
不复制参数 Schema，不要求用户在两个相互独立的审批系统重复批准。

## 何时补充 Governance

restart_service、deploy_change、move_robot、modify_configuration 需要回答：
谁在什么环境改变什么，影响是否可接受，审批绑定什么，以及如何确认结果。
如果这些问题不能由既有工具和部署回答，Kai 可补最小治理边界；实际执行仍由已有能力承担。

```text
外部 Agent 提交 Governed Intent
  → Kai 核对边界与审批引用
  → 既有受信调用方使用原 Tool / MCP 接口
  → Environment
  → 操作回执 + 独立 Observation 验证
```

治理通过不会赋予模型通用执行凭据。未来的受信集成点必须确保未授权意图不能绕过门禁，
并保证批准的资源和参数就是实际执行的资源和参数；否则薄封装没有安全价值。
本阶段不选择或实现该集成点，不给 Runner 增加工具权限。

## 不能跨越的界限

- Kai 不决定修复方案、生成计划或选择机器人轨迹。
- Kai 不实现工具执行逻辑、shell 转发、SSH、ROS2 控制或工作流。
- 审批不覆盖环境禁用、原生拒绝或安全联锁；超时不意味着动作撤销。
- 执行回执、审计记录与结果验证分别关联，不能互相替代。
- Observation Provider 保持只读；验证失败不触发自动重试或修复。

完整决策矩阵与 VPS/机器人案例见 [Governance 设计](action-governance-design.md)。
本提案细化 [ADR-0002](adr/0002-action-boundary.md)，不改写历史决定或 Registry 安全限制。
