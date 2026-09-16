# Kai Architecture Boundary Matrix

状态：V0.8 反膨胀审查建议，待人工审核。本文定义职责取舍，不授权实施或环境执行。

## 定位与当前实现

选择 **D. AI Control Plane**，在 Kai 中具体指外部 Agent 与 Environment 的薄控制面。
不是 Agent Framework、Workflow Engine 或 Robot Framework，也不是通用 AI 平台。
Kai 管接入、环境身份、边界约束、契约验证和审计关联；推理、规划及底层执行复用外部生态。

代码审查显示：kai-agent 委托 Claude Code；kai-observation 委托 VPS Observer；
Registry Validator 独立校验声明。Runner 尚未调用 Observation Provider，Provider 尚未
执行完整运行时 Schema 校验或 Registry 身份绑定。当前没有 Action Runtime。
V0.5 Runtime/Memory/Freeze 文档已标为历史参考，不应因其存在而恢复整套实现路线。

## 边界矩阵

| 能力 | Kai负责 | 外部生态 | 原因 |
| --- | --- | --- | --- |
| LLM调用 | 启动环境与模型配置引用，不建路由或推理服务 | 模型 Provider、外部 Harness/SDK | 模型调用不是环境治理的差异化能力。 |
| Agent Loop | 启停边界、总预算和结果接收 | Claude Code / Claude Agent SDK、OpenAI Agents SDK；有需要时外部 LangGraph 应用 | 不复制推理、上下文循环和恢复机制。 |
| Tool Protocol | 工具身份、允许范围和安全语义映射 | MCP、Provider Function Calling | 领域参数约束不是新发现、传输或调用协议。 |
| Memory Storage | 保留历史 Contract；有需求时定义最小外部引用与权限边界 | 数据库、检索服务、外部 Agent Memory | 不建向量库、长期记忆引擎或检索系统。 |
| Observation Contract | 有版本的只读状态摘要、环境标识、时间与缺失语义 | ROS2 topics、MCP Resources、既有遥测系统 | 定义消费视图，不替代数据总线或遥测存储。 |
| Action Contract | 有明确治理缺口时保留最小动作授权与结果关联封装 | MCP Tools、领域 API、环境专属 Adapter | 控制边界可独立存在，执行协议无需自研。 |
| Robot Control | 环境引用和高层授权边界 | ROS2、机器人控制器、安全联锁 | 实时控制、运动规划和急停属于专业控制系统。 |
| Workflow | 关联外部运行，不调度步骤图 | 外部 Harness、LangGraph 或既有工作流系统 | 不实现 DAG、补偿、通用重试和持久调度。 |
| Security Boundary | 明确身份/资源/审批绑定、allowlist、预算与审计要求 | OS 权限、沙箱、身份系统、环境原生授权 | Kai 负责边界要求，强隔离不能只靠 JSON 或 cwd。 |

外部生态列是职责归属，不代表现在同时引入这些依赖。

## Agent Loop：Delegate

- Claude Agent SDK 提供 Claude Code 的 Agent loop、工具和上下文能力；当前 CLI 已复用该类能力，
  没有必要仅为“统一接口”迁移到 SDK。[官方概览](https://code.claude.com/docs/en/agent-sdk/overview)
- OpenAI Agents SDK 是可复用的 Agent 开发 SDK；它是未来外部 Agent 接入选项，
  不是在 Kai 内自建循环的理由。[官方文档](https://developers.openai.com/api/docs/guides/agents/sdk)
- LangGraph 面向有状态编排、持久执行与人工介入；需要这些能力的应用可在 Kai 外部使用，
  Kai 不复制其图执行系统。[官方概览](https://docs.langchain.com/oss/python/langgraph/overview)

结论：当前 Harness 保留，自研 Agent Loop 从未来实现职责中移除；历史文档不删除。

## Tool Calling：复用协议

Function Calling 描述模型提出的结构化工具调用，实际执行由应用侧承接；MCP 定义客户端与
服务端之间的工具发现和调用等交互，两者不是同一层的互斥替代品。
Kai 可约束业务参数和授权，但不重新定义通用 Tool Protocol。
[Function Calling](https://developers.openai.com/api/docs/guides/function-calling)、
[MCP Tools](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)

MCP 工具注解只能作为提示，不能替代受信权限判定；采用 MCP 也不自动解决租户、审批和审计。

## Memory：保留契约资产，不建设后端

不实现 Vector Database、Long-term Memory Engine、Retrieval System。
五层 Memory 和 provenance 文档可保留作领域参考，但不要求每次 Agent 接入实现五层模型。
仅在实际集成需要时明确外部数据作用域与引用，不提前实现通用 Memory API 网关。
审计关联和幂等记录属于控制面执行证据，不应演变成供 Agent 检索学习的长期记忆系统。

## Observation：保留摘要，不建设第二个遥测平台

现有 Contract 的 version、timestamp、environment_id、封闭分区、错误语义和 Raw/Contract
分离适合轻量状态快照。它不是全环境标准，system/services 等分区偏 VPS；机器人字段需真实
消费需求驱动的版本化扩展，不能为了“统一”抹去单位、坐标系、源时间或质量信息。

| 外部机制 | 与 Kai 的关系 | 不应重复的能力 |
| --- | --- | --- |
| ROS2 topic | 连续、类型化发布订阅数据可作为 Adapter 输入；Kai 只提供所需摘要 | 消息传输、发现、QoS、原生机器人消息模型。 |
| MCP Resource | 可承载 Observation JSON 或引用，属于数据暴露接口 | 另造资源发现/订阅协议。 |
| OpenTelemetry | 可关联运行 traces/metrics/logs，或复用已有观测来源 | 自建通用 telemetry collector、时序库、追踪后端。 |

三者与 Observation 没有必然冲突，前提是 Kai 保持应用层消费视图，不追求无损替代原生系统。
[ROS2 接口](https://docs.ros.org/en/ros2_documentation/rolling/Concepts/Basic/Interfaces-Topics-Services-Actions.html)、
[MCP Resources](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)、
[OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/)

已发现的限制：Schema 合法不证明新鲜度、来源可信或环境授权；单个 timestamp 不表示原子
快照；当前服务状态未采集；Observer 的环境 ID 只是调用方标签。应按需求补缺口，不能用
新增 Registry、生命周期管理器或分析引擎掩盖这些具体问题。

## Action vs Tool：有条件保留控制语义

Tool 是可调用能力；Action 是 Kai 需要治理的特定环境操作意图。同一操作可以同时是
MCP Tool 和受 Kai 约束的 Action；查询工具不因此变成环境写动作。

当存在跨 Harness 的统一审批、不可替换的资源身份绑定、明确副作用控制、结果证据关联
等具体缺口时，Action 薄封装有价值。它可以映射到已有 MCP Tool，不要求新建 Action Adapter。

当受信 MCP Tool 及既有部署已经满足权限、审批、超时、审计和资源限制时，优先复用该 Tool，
无需再包装一套同名 Action JSON、Dispatcher 和结果体系。“直接使用”仍受授权边界约束，
不表示 Agent 可绕过控制面。当前 Runner 未开放 MCP，任何接入都需后续独立批准。

V0.8 草案与旧 Tool/Environment Request 在 ID、参数、权限、超时及结果上存在重叠。
冻结新 Schema 前应逐字段说明增量价值；不能只将 tool_name 改成 action_type。
批准请求绑定与最终执行授权应有一个受信事实来源，不让 Harness 和 Kai 各维护一份冲突审批。

## Keep / Remove / Delegate

| 对象 | 决定 | 具体边界 |
| --- | --- | --- |
| 薄 Harness、Registry Validator | Keep | 不扩张为调度器或通用能力市场。 |
| Observation Contract / Provider、Raw 转换 | Keep | 状态摘要和格式转换，无分析、决策、写入。 |
| Action Contract | Conditional Keep | 先证明治理缺口，优先复用 Tool 协议与字段。 |
| 自研 Agent Loop / Planner / Tool Protocol | Remove from scope / Delegate | 保留历史文件，运行能力交由外部 Harness 和协议。 |
| Memory、Workflow、Robot Control | Delegate | 不把外部依赖的完整模型复制进 Kai。 |
| require_tool_executor 旧约束 | Keep until reviewed migration | 不能删标志、改名或忽略约束以启用执行。 |

## V0.8 审查门槛

当前 execution_enabled=false、require_tool_executor=true 是执行阻断，不是实现 Executor
的需求证明。先审核旧约束如何映射到外部执行边界，再决定版本化迁移，期间保持拒绝。

下一步只评审一个动作案例，列出“现有 MCP/领域接口已提供什么、Kai 缺什么”，
以及拒绝、过期审批、参数替换、超时未知和观察不足的预期结果。
没有具体缺口则不增加 Action 框架；有缺口则只设计最小授权封装，仍不实施真实执行。

关联：[非目标](architecture-non-goals.md)、[当前定位](architecture-positioning.md)、
[Action D0 草案](action-design.md)。本审查不改写历史契约，也不声明安全边界已经完整实现。
