# Kai Action Control Plane — V0.8-D0

状态：**Proposed / Design Only / 待人工审核**。本阶段不创建 Action Schema、Runtime、
Adapter 或执行服务，不改变当前 Harness、Observation Provider、Registry 和任何环境。

## 架构审查

审查范围包括 V0.6 架构、Observation 设计和 Provider ADR、Policy 设计、Core Tool /
Environment Schema、Agent / Tool / Environment Registry Schema、实际环境登记和工具策略，
以及当前 Runner、Provider 与 Registry Validator 的安全规则。

当前 Kai 复用 Claude Code Harness 的 Agent 能力。Runner 只启用 Read/Glob/Grep；
Observation Provider 委托 Adapter 采集并转换为 Observation 1.0，尚未由 Runner 自动调用。
因此 `Harness → Observation Provider → Environment Adapter` 是稳定集成边界，
不是已完成全部串接的声明。Action 应是与观察并列的受控请求通道，不给 Observation 增加写方法。

| 已有设计 | 审查发现及 V0.8 处理 |
| --- | --- |
| V0.5 Tool / Environment Request | 已定义参数、权限、超时、审计和幂等；Action 只是环境动作意图，不重建通用工具执行框架。 |
| Registry 权限 | 复用 READONLY / CONTROLLED / ADMIN；登记或请求声明不等于授权。 |
| Tool Registry 副作用 | 复用 none / reversible / irreversible；未知影响拒绝，不默认 none。 |
| Policy 设计和 tools-policy | 复用默认拒绝、审批绑定、严格规则优先；D0 不实现 Policy Engine。 |
| 当前 vps-primary | registered、declarative_only、connected=false、execution_enabled=false，不能用于执行示例。 |
| require_tool_executor=true | 与不建 Tool Executor 的目标存在执行集成冲突。不得把 Action Adapter 改名视为满足条件；需另行批准版本化迁移，当前保持拒绝。 |
| Observation 1.0 | 不包含 observation_id；结果引用由未来控制面关联记录管理，不向 Observation 顶层加字段。 |
| VPS Observer 原型 | 尚不采集服务状态，不能验证 restart_service 的结果；机器人专用遥测也需未来契约扩展。 |

设计层兼容不等于执行层已就绪。当前不存在可合法启用 Action 的完整路径。

## 1. Action Plane 定位

Action Plane 是 **Agent 与 Environment 执行能力之间的安全控制边界**。
它不是 Agent Runtime、Planner、Robot Controller 或 Workflow Engine。
外部 Agent 决定请求什么；控制面验证能否请求；环境专属组件执行已获准的单个动作。

错误路径：

```text
LLM → SSH/System Command → Environment
```

目标路径：

```text
LLM → Harness → Action Contract → Action Validator
                                      ↓
                                Approval Check
                                      ↓
                                Action Adapter → Environment
```

图中的 Validator 是结构、引用、能力与授权边界的逻辑职责，不是新规划器或已实现服务。
Harness 只提交稳定契约，不绑定具体 Adapter 的环境 API，也不能绕过审批门禁。

## 2. Action 数据流

```text
User Request
  ↓
Agent Decision
  ↓
Action Request
  ↓
Action Validation
  ↓
Approval Check
  ↓
Action Adapter
  ↓
Environment
  ↓
Observation Verification
```

| 步骤 | 职责 |
| --- | --- |
| User Request | 表达目标和授权范围，不把自然语言请求视为无限环境权限。 |
| Agent Decision | 外部 Agent 形成动作建议；Kai 不生成计划。 |
| Action Request | Harness 提交类型化动作、明确目标和参数；可信入口绑定真实主体身份。 |
| Action Validation | 验证版本、结构、动作 allowlist、资源引用、参数、权限和副作用；未知或禁用项拒绝。 |
| Approval Check | 验证受信审批凭证、参数摘要、目标、主体、有效期和撤销状态；审批不能覆盖 deny。 |
| Action Adapter | 接收已验证且授权绑定的单次请求，映射环境操作并返回结果。 |
| Environment | 在自身最小权限及安全联锁下执行；环境原生约束仍可拒绝。 |
| Observation Verification | 通过只读 Provider 获取执行后的证据，由控制面按预先定义的完成条件核验；不触发修复。 |

拒绝或待审批时不进入 Adapter。分派前重新确认授权有效，避免审批后参数替换。
执行结果与观察证据分别记录：Adapter 报告完成不等于目标状态已验证；缺失、陈旧、
环境不匹配或粒度不足的观察不能作为成功证据。VPS 服务探测尚未实现，不伪造验证结果。

## 3. Action Contract 设计

未来路径为 `configs/schema/action.schema.json`，本阶段不创建。
详细类型与示例见 [Schema 草案](action-schema-draft.md)。必须字段：

| 字段 | 含义 |
| --- | --- |
| version | 独立 Action Contract 版本，拟为 1.0；不是 Kai 发布版本。 |
| action_id | 单次动作意图的稳定标识，用于结果关联和重复请求识别。 |
| environment_id | 已登记环境引用，不接受任意 SSH 地址。 |
| requested_by | 受信身份引用；LLM 自报值不能建立身份或权限。 |
| action_type | 显式允许的语义动作名，不是命令或可导入模块名。 |
| parameters | 针对该动作的封闭参数结构，不接受 shell 文本。 |
| permission | 请求声明的权限类别，必须与可信动作定义一致，不构成授权。 |
| side_effect | none / reversible / irreversible，与可信定义核对，不能由 Agent 降级。 |
| approval | 受信审批记录引用或 null；不接受自签 granted 布尔值。 |

这些字段不是完整执行授权包。分派前还须绑定 timeout、audit_id、correlation_id、
幂等键、资源身份、策略版本和适用安全约束；建议扩展字段见草案。
缺失受信上下文时 fail closed，不依靠 Adapter 猜测。

## 4. Permission 模型

复用 V0.5/V0.6 三类权限，不增加等级：

- **READONLY**：查询类动作，无环境写副作用；状态采集优先走既有 Observation Provider。
- **CONTROLLED**：可逆且范围明确的动作；仍需结合环境策略决定审批，不能假设可逆就无需审批。
- **ADMIN**：高风险动作，必须审批；审批不扩大主体或环境授权。

实际许可取主体、任务、工具登记、环境安全策略及适用政策的交集，显式 deny 优先。
ADMIN 和 irreversible 必须审批；其他破坏、提权或外部副作用遵守 tools-policy 的更严格要求。
当前 vps-primary 还要求 CONTROLLED 和 ADMIN 审批并关闭全部执行，审批不能解除关闭。
重启不天然可逆：可能中断任务或丢失内存状态，必须按目标服务定级，不能统一标成低风险。

## 5. Action Adapter 边界

负责将获准 Action Contract 转成环境操作，并返回有限、脱敏的执行结果。
不负责决策、任务规划或权限政策判断。它可以验证授权绑定的完整性、拒绝过期或不匹配输入，
但不能自行授权、降级风险或扩大动作范围。环境原生权限检查始终有效。

概念映射（不是当前可执行能力）：

| 环境 | Action | Adapter 内部映射 |
| --- | --- | --- |
| VPS | restart_service | 固定程序与参数数组语义：systemctl restart xxx；xxx 来自已授权服务映射，不拼接模型命令。 |
| Robot | move_arm | 受限 ROS2 action/service；机器人控制、轨迹和安全联锁由专业环境组件提供。 |

不接受任意 executable、command、脚本、SSH 目标或通用 RPC 转发。
不提供循环、依赖图、批处理编排、自动重试、补偿工作流或自动修复。

## 6. Action Result Contract

未来 ActionResult 字段：

| 字段 | 含义 |
| --- | --- |
| action_id | 关联原始动作请求。 |
| status | 拟用 completed / denied / failed / timed_out / unknown，描述单次执行结果，不建立任务状态机。 |
| timestamp | 结果记录时间，RFC 3339 UTC。 |
| output | 按动作定义的有限、脱敏结构化结果，无法确认时为 null。 |
| error | 稳定原因码及脱敏消息；无错误为 null，不包含凭据或堆栈。 |
| observation_reference | 关联执行后观察证据的控制面引用，未获得证据时为 null。 |

结果契约分离请求意图、执行事实与观察证据，便于跨 Adapter 审计，避免以自由文本宣称成功。
completed 仅代表 Adapter 确认操作完成，验证结论由引用的证据与完成条件另行记录。
观察引用需绑定环境、采集时间和内容摘要，不是任意 URL；现有 Provider 无持久引用存储，
其存储和保留策略需另行设计，本阶段不建设 Memory 系统。

超时不保证动作撤销；失联或副作用未知应明确记录 unknown，不自动重试。
action_id 对同一主体和环境绑定不可变请求摘要；同 ID 不同参数必须拒绝。
重复请求的去重记录是未来执行安全前提，不宣称 exactly-once，也不在 D0 实现状态存储。

## 7. 安全边界

Agent 直连 shell 会把模型文本转成开放执行权，绕过资源身份、审批绑定和审计，
并使命令注入与间接提示注入跨越边界。Action Request 必须被视为不可信输入。

- **allowlist**：限制 action_type、具体资源和参数集合；新增能力需审核，不从字符串动态加载代码。
- **permission**：验证真实主体和适用策略，不相信请求中的权限声明；注册不等于授权。
- **approval**：绑定 action_id、规范化请求摘要、环境、资源、主体、策略版本和有效期，执行前核验撤销。
- **timeout**：采用工具、环境及全局预算最严格上限；当前 tools-policy 上限 120 秒，不由请求提高。
- **audit**：执行前记录受信授权关联，执行后记录结果和证据；日志脱敏、输出限长，审计不可用时禁止开始执行。

审批结果不应由模型生成；观察文本和动作输出都不是新的系统指令。
不得因失败或观察不符合预期自行生成下一动作。紧急停机和物理安全仍属于 Environment，
不由 Kai 取代机器人控制器。当前 workspace 路径校验也不能当作系统级执行沙箱。

## 8. 兼容性与下一阶段门槛

V0.5 字段、枚举、Schema 和冻结语义保留；V0.6 Runner 继续只读；V0.7 Provider / Adapter
继续只读。新 Action 路径在审核前不接入任何生产环境。
历史 `require_tool_executor=true` 是明确的迁移阻断，不能静默忽略。
先评审 Action 与旧 Tool/Environment 请求的映射以及安全职责，再决定是否制定新版本；
不创建第二份能力 Registry，不启用既有登记。

下一阶段建议仅冻结契约和负面用例（未知动作、伪造身份、过期审批、参数替换、重复动作、
执行关闭、超时未知、陈旧观察），经人工审核后再考虑纯离线验证；真实执行另行授权。
