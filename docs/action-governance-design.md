# Controlled Action Governance — V0.8-D1

状态：**Proposed / Design Only / 待人工审核**。本阶段只定义治理边界，不实现 Action、
Executor、Workflow、Adapter 或新 Tool Protocol，不启用真实环境执行。

## 1. 定位与 D0 的关系

Kai 是 AI Control Plane，不是 Agent Framework、Workflow Engine 或 Robot Controller。
外部 Agent 负责推理和动作建议；Kai 负责 Governance Boundary；已有执行能力负责操作环境。
MCP 是能力交互协议，不是 Agent Runtime；背景图表示职责关系，不表示当前 Runner 已接入 SDK、
MCP 或 Observation Provider。

本提案收紧 [D0 Action 设计](action-design.md)：**Action = Governed Action Intent**，
表示一次经过策略约束的环境状态改变意图，不是 another tool call。
D0 中的 READONLY 查询不再需要进入 D1 的 Action 意图模型，继续走受限 Tool 或 Observation。
READONLY / CONTROLLED / ADMIN 权限枚举仍完整保留，不修改历史 Schema 或 Registry。
D0 的 Action Adapter 位置可由 Existing Tool / MCP / 外部 Adapter 满足，不要求新建组件。
上述是待审核的设计演进，D0 草案与 ADR 原文保留。

## 2. Tool vs Governed Action Decision Matrix

| 场景 | Tool即可 | 需要Action Governance | 原因 |
| --- | --- | --- | --- |
| query_status | 是，已有身份和访问范围约束时 | 无需新增 | 查询事实，不改变环境；保留必要访问审计。 |
| read_file | 是，路径、主体和敏感数据边界有效时 | 无需新增 | 读权限仍须落实；读取 secret 不因 READONLY 自动获准。 |
| get_observation | 是，优先现有 Provider 或受信 Tool | 无需新增 | 已有输出契约和错误语义，不重复封装。 |
| restart_service | 仅有调用参数和返回值不足 | 是，可复用既有治理实现 | 涉及可用性、任务中断，需要目标绑定、审批和恢复证据。 |
| deploy_change | 仅有部署接口不足 | 是，可复用既有治理实现 | 绑定制品/变更版本、环境、审批与发布后证据；不实现部署步骤编排。 |
| move_robot | 仅有坐标参数和回执不足 | 是，可复用既有治理实现 | 必须关联物理安全条件、受限空间和动作后状态。 |
| modify_configuration | 仅有文件写入能力不足 | 是，可复用既有治理实现 | 绑定精确差异、目标和生效条件，避免审批后内容替换。 |
| 已有 Tool 服务具备全部所需治理 | 是，复用同一执行与授权来源 | 语义需要，Kai 无需另建一套 | 引用其审批、审计和证据即可，不重复审批或包装同名工具。 |
| 未知资源、身份或副作用 | 否 | 先拒绝，不能靠加封装放行 | 治理不能弥补缺失的授权事实。 |

判断顺序：确认是否改变环境状态；核对已有 Tool 与部署能否满足实际边界；
只补未覆盖的治理信息。只读 Tool 已提供可靠权限、参数和返回值时，Kai 不重复封装。
写动作需要治理，不等于必须由 Kai 新建治理服务；已有能力充分时优先引用。
普通日志或计量不算这里的业务状态改变，也不因此把所有查询归为 Action。

## 3. Governed Action Intent 的信息边界

下列是语义需求，不是新的 JSON Schema 或调用协议：

| 问题 | 意图及治理记录应表达什么 | 可信来源 |
| --- | --- | --- |
| 谁请求 | 主体、委托关系及请求关联 | 认证入口；不以模型自报身份授权。 |
| 对哪个环境 | 环境身份、精确资源、版本或状态前提 | 已审核登记与资源映射，不接受任意地址。 |
| 为什么执行 | 用户目标、相关 Observation 和简短理由 | 用户请求与外部 Agent 建议；理由不是授权，也不要求私有思维链。 |
| 风险等级 | 影响范围、可逆性、物理风险和不确定性 | 受信动作定义与环境安全规则；不让模型降低等级。 |
| 是否需要审批 | 审批要求、审批引用及其绑定范围 | 受信政策与审批来源。 |
| 如何验证 | 完成条件、证据来源、新鲜度及容差 | 审批前固定的领域要求，不由执行后临时改写。 |

风险沿用历史 Policy 设计的 LOW / MEDIUM / HIGH / CRITICAL 术语，不引入新的风险引擎。
风险与 READONLY / CONTROLLED / ADMIN 权限不是同一字段：风险不能扩大权限，
CONTROLLED 也不意味着免审批。实际权限及更严格的环境限制优先。

Action 不负责领域决策、Planner、执行或控制。Governance Check 判断“是否满足既有约束”，
不判断“接下来应该做什么”。执行失败不会由 Kai 自动生成重试、回滚或修复意图。

## 4. Action Governance 数据流

```text
Observation
  ↓
Agent Reasoning
  ↓
Action Intent
  ↓
Governance Check
  ↓
Approval
  ↓
Existing Tool / MCP / Adapter
  ↓
Environment
  ↓
Observation Verification
```

| 阶段 | 职责 |
| --- | --- |
| Observation | 提供只读状态、采集时间、环境标识及缺失信息；不诊断并自动修复。 |
| Agent Reasoning | 外部 Agent 分析现象、选择建议；Kai 不运行推理循环。 |
| Action Intent | 表达一次状态改变目标及治理所需上下文，不包含任意 shell。 |
| Governance Check | 检查环境与资源身份、允许范围、权限、风险约束、预算和验证前提；缺失即拒绝。 |
| Approval | 按政策核验审批来源、有效期和精确请求绑定；无需人工时也须有受信政策依据。 |
| Existing Tool / MCP / Adapter | 使用已有调用协议执行已获准请求，输出执行回执；不由 Kai 实现底层操作逻辑。 |
| Environment | 落实原生权限、安全联锁与实际操作，仍可拒绝已审批的请求。 |
| Observation Verification | 独立只读采集执行后状态；按已定义完成条件关联证据和验证结论。 |

此图是职责流，不是 Workflow Engine。审计贯穿请求、门禁、审批、执行与验证。
执行前必须绑定主体、环境、资源、参数/变更摘要、风险约束和验证条件；任一实质变化
使原审批失效。不得出现 Harness 和 Kai 分别维护且相互冲突的审批真相。

三种信息不能混同：**audit** 说明谁何时获准；**execution evidence** 说明已有工具
实际接受和完成了什么；**verification** 说明观察到的结果是否满足目标。
工具退出成功不等于网站恢复或机器人已安全到位。
超时、失联、证据过期或环境不匹配时保留 unknown/unverified，不默认成功、不自动再执行。
历史幂等、超时与审计要求必须有外部责任方，不能因“不造 Executor”而省略。

## 5. 案例一：VPS 网站恢复

用户：“网站打不开，帮我恢复”。这是目标表达，不是任意重启、部署或修改配置的授权。

| 阶段 | 设计示例 |
| --- | --- |
| Observation | 假设未来已有只读证据确认目标 nginx service unhealthy；还需区分网络、应用等其他原因。 |
| Agent Reasoning | 外部 Agent 提议一次 restart nginx；Kai 不从 unhealthy 自动生成动作。 |
| Action Intent | 绑定已登记 VPS、精确 nginx 服务、请求者、原因与预期恢复条件。 |
| Governance | 本案例假设已有审核定义将该受限重启归为 CONTROLLED；范围、影响与窗口已知。 |
| Approval | required，明确展示目标、影响与参数；受信审批仅覆盖这一次意图。 |
| Tool | existing system service tool；保留其调用协议，Kai 不拼接或执行系统命令。 |
| Verification | 通过只读 Observation 确认服务状态及获准网站健康证据；单纯 running 不证明网站已恢复。 |

CONTROLLED 是案例前提，不是所有 nginx 重启的固有等级。可能丢失会话、扩大停机或影响未知时
必须拒绝该前提，按更严格政策重新审核。D0 的保守 ADMIN 示例因此不被默默降级。
记录关联的审批、执行回执和验证证据；失败后如需部署或再重启，必须由外部决策者提出新请求。

当前不可执行：VPS Observer 未采集服务和网站健康信息；Registry 仍为
execution_enabled=false、require_tool_executor=true。当前 Runner 也未开放 MCP 执行能力。
本案例不增加探测、服务控制或网络连接。

## 6. 案例二：机械臂移动

用户：“把机械臂移动到指定位置”。仅提供目标坐标并收到 Tool 回执不足以证明动作安全。

- **safety check**：专业机器人系统验证运行模式、载荷、速度/力限制、急停及联锁状态。
- **workspace boundary**：核验目标坐标系、单位、物理可达空间和禁入区；这不是 Kai 的文件目录边界。
- **collision check**：轨迹与碰撞检查由外部规划器/控制器完成；Kai 只要求引用有效的检查证据，
  不实现运动规划、碰撞算法或控制回路。
- **verification**：执行后依据新鲜机器人状态确认位置、容差、停止状态和错误信息，不能只看请求已接受。

Governed Intent 绑定机器人身份、目标姿态、坐标系、容差、安全条件、检查证据及审批。
环境或轨迹条件改变时旧证据可能失效，专业控制系统必须在执行期间持续保证安全；
Kai 的一次性审批不能替代实时联锁。

未来 ROS2 Adapter 由执行环境提供，复用其 action/service 接口与反馈，接受获准的领域请求；
Kai 不实现 ROS2 的控制或任务生命周期。也可以通过既有 MCP Tool 暴露该能力，
无需建立第二个机器人协议。动作后的只读观察保持独立。
当前 Observation 1.0 不包含完整姿态/坐标系遥测，需后续版本设计，不能塞入任意 metadata。

## 7. 进入 Schema 阶段的条件

建议在人工认可本边界后进入**最小 Governance Intent Schema 草案**，不是 Action 执行 Schema。
先确定主体、环境、理由、风险、审批和验证引用的最小字段与受信来源；复用现有权限枚举，
不复制 MCP 工具描述、调用、发现或执行状态机。

仍需审核：与 D0 字段的映射、唯一审批事实来源、证据引用与保留责任、重复意图和未知结果处理。
require_tool_executor 的兼容性问题另行版本化决策；在解决前，Schema 即使通过也不能执行。

相关：[MCP 边界](mcp-action-boundary.md)、[ADR-0003](adr/0003-action-governance-boundary.md)、
[架构非目标](architecture-non-goals.md)。

## V0.8-D2 补充：声明与审批语义（待人工审核）

Action Intent 是 **declarative、non executable、approval optional**。
Governance Intent is declarative, not executable.
Approval is a governance mechanism, not a universal execution step.
Approval is not mandatory for every action.

approval optional 指是否需要逐次审批取决于可信政策，不表示可以省略契约中的 approval
对象或由模型自行批准。低风险动作可由已有策略授权，高风险动作需人工或可信审批；
本阶段不实现自动审批。风险不扩大权限，CONTROLLED 不代表自动批准。

最小契约仅描述治理声明，不能 execute()，也不构成对任意具体执行方式的授权。
详见 [Governance Intent 设计](governance-intent-design.md)及
[ADR-0004](adr/0004-governance-intent-contract.md)。以上补充不改写 D1 历史正文。
