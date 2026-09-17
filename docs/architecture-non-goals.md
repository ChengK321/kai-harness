# Kai Architecture Non-Goals

状态：V0.8 反膨胀审查建议，待人工审核。Kai 是面向 Agent 与 Environment 的薄 AI Control Plane。
以下能力不纳入 Kai 自研范围；历史设计资产保留，不代表实现承诺。

| 非目标 | 原因 | 允许的最小边界 |
| --- | --- | --- |
| LLM Provider / LLM Router | 推理服务与模型路由由 Provider、Harness 或专用服务提供 | 传递受控配置引用、记录运行来源。 |
| Agent Framework / Runtime / Planner | 重复外部 Agent loop、上下文管理与规划能力 | 启动外部 Harness，限制预算，接收结果。 |
| Workflow Engine | DAG、持久调度、补偿和通用重试会把控制面变成执行框架 | 引用外部工作流运行，不管理其内部步骤。 |
| Vector Database | 索引、存储和一致性不是 Kai 的核心职责 | 需要时引用已有数据服务。 |
| Long-term Memory Engine / Retrieval System | 记忆生成、召回、排序和遗忘属于外部应用能力 | 保留历史 Contract；按需限制作用域和数据访问。 |
| Robot Controller | 实时运动控制、轨迹、安全联锁和急停要求专业组件 | 约束高层动作授权，不接管控制闭环。 |
| ROS2 替代层 | 重建 topic/service/action、QoS 和发现机制没有增量价值 | 有需求时做专用数据映射，不建设第二条总线。 |
| 通用 Tool Marketplace | 发现、分发、安装和商业市场超出受控登记职责 | 保留部署所需的能力声明与校验，不建第二份 Registry。 |
| 通用 Tool Protocol / Executor | 与 MCP、Function Calling 和环境执行能力重叠 | 复用协议，只增加可证明必要的授权和参数约束。 |
| 自动修复引擎 | 从观察自动生成并执行修复构成决策及动作循环 | 返回观察事实、错误和执行证据，由受权方决定下一步。 |
| 通用遥测平台 | 重复成熟采集、追踪和时序存储生态 | Observation 摘要及审计关联，复用外部后端。 |
| 通用 Policy 语言或规则引擎 | 为少量边界检查引入新 DSL 和规则调度会扩大复杂度 | 复用权限枚举、明确校验规则和既有授权服务。 |

## 不能以非目标为由省略的责任

不造 Executor 不等于允许任意 shell；不造 Policy Engine 不等于跳过授权；
不造 Memory 不等于删除审计证据。身份绑定、审批有效性、超时、输出限制、审计关联和
副作用未知处理仍须有明确责任方，真实执行前必须证明这些边界能够落实。

当前 require_tool_executor=true 的旧配置不能通过此清单被豁免，需单独审批版本化迁移。
MCP 工具的只读提示或 Adapter 元数据也不构成系统级权限保证。

## 新增能力的准入问题

1. 是否存在具体用户场景，而非为了未来通用性提前建框架？
2. 外部 Harness、MCP Tool 或既有环境服务是否已覆盖该需求？
3. Kai 增量是否只涉及环境身份、边界、契约或证据关联？
4. 是否引入步骤调度、通用重试、模型循环、检索引擎或机器人控制？若是，应委托外部系统。
5. 是否复用当前权限和能力声明，避免第二套 Registry、审批状态或 Tool 协议？

若需求必须越过这些边界，应先提出明确 ADR 并人工审核，不以“Adapter”“Provider”或
“Control Plane”的命名掩盖职责扩大。涉及新执行入口的设计认可不等于部署授权。

详见 [边界矩阵与生态比较](architecture-boundary-matrix.md)。

## V0.8-D1：Governance Boundary（待人工审核）

在环境动作路径中，Kai 不拥有 **Decision Making、Task Planning、Action Execution Logic**。
领域决策与任务规划属于外部 Agent，执行逻辑属于 Existing Tool / MCP 服务 / Environment Adapter。
Kai 只负责 **Governance Boundary**：环境与主体绑定、权限约束、审批引用、审计和验证关联。

治理检查是否满足既有约束，不代表 Kai 决定下一步业务动作。机器人 safety/collision check
由专业系统执行，Kai 只核对所需证据；不实现轨迹规划或实时控制。
验证失败不授权自动修复、回滚或重试。

Action 是 Governed Action Intent，不是新的 Tool Wrapper；既有工具能力充分时无需重复封装。
详见 [D1 Governance 设计](action-governance-design.md)和
[ADR-0003](adr/0003-action-governance-boundary.md)。本补充不改变历史配置或启用环境执行。
