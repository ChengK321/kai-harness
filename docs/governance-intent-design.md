# Minimal Governance Intent Contract — V0.8-D2

状态：Proposed / Design Only / 待人工审核。
契约：[governance-intent.schema.json](../configs/schema/governance-intent.schema.json)，
JSON Schema Draft 2020-12，契约版本 1.0，与 Kai 发布版本分别管理。

## 1. 为什么需要 Governance Intent

Governed Action Intent 记录环境状态改变请求的最小治理上下文，连接身份、目标、
用户目标、风险、审批引用和验证要求。它不是执行请求，也不授权改变环境。
沿用 [D1 边界](action-governance-design.md)，已有 Tool 满足需求时不重复包装。

## 2. Intent 与 Tool 的区别

Tool 提供具体可调用能力；Intent 描述治理对象，不指定工具、参数调用或执行方式。
同一个用户目标可能由不同外部能力满足，Kai 不据此自动选择工具或生成计划。
本契约没有 tool_name、command、shell、executor 或通用 parameters。
对 MCP 和未来 ROS2，只保留治理关联，不修改其接口。

## 3. Intent 与 Workflow 的区别

Intent 没有依赖边、步骤序号、调度、retry、rollback 或 planner。
请求与证据的关联不是 Workflow Node，也不建立持久执行状态机。
批准某个用户目标不等于批准实现该目标的所有可能步骤。

## 4. 字段与可信来源

全部九个顶层字段必填；顶层及每个嵌套对象均 additionalProperties=false。

| 字段 | 结构 | 语义与限制 |
| --- | --- | --- |
| version | string，固定 1.0 | 独立契约版本。 |
| intent_id | 非空且非纯空白 string | 唯一治理请求标识；唯一性及重复 ID 冲突需外部检查，Schema 不保存状态。 |
| requester | type、id | type 为 human 或 service；认证入口绑定真实主体。模型不是独立认证来源，不允许模型自报身份作为授权。 |
| environment | environment_id | 必须解析为 Registry 身份，不使用 hostname、IP 或 SSH 地址。 |
| target | resource | 目标环境内的逻辑资源，如 service/nginx、robot/arm01 或明确映射的 nginx；不描述执行方法。 |
| purpose | 非空摘要，最长 1024 字符 | 只保存用户目标摘要，不保存 reasoning chain、模型思维过程或控制提示词。 |
| risk | LOW / MEDIUM / HIGH / CRITICAL | 复用历史风险术语，由受信规则确认，不接受模型自行降级。 |
| approval | required、reference | 是否需要审批，以及 opaque 审批记录标识或 null；不是批准结果。 |
| verification | required、evidence_type | 是否要求验证；1.0 仅支持 observation，不包含验证结果。 |

environment_id 和 resource 只采用宽松的标识字符串约束以保留既有 Registry 语义；
Schema 能拒绝 hostname/ip/ssh 等额外键，但无法仅从字符串证明标识已登记。
即使把 IP 填入 environment_id 并通过类型检查，治理层仍须按 Registry 引用规则拒绝直接地址。
同样，Schema 不能识别 purpose 中所有指令或 secret；文本必须作为不可信数据处理，
不得解析为命令或 prompt。可信入口应限制和脱敏摘要。

## 5. Intent 生命周期

```text
Request
  ↓
Validate
  ↓
Approve（仅在受信策略要求时）
  ↓
External Execution（独立授权与既有执行能力）
  ↓
Verify
```

这是责任顺序，不是 Workflow Engine，也不是本阶段实现的调度流程。
Request 形成声明；Validate 检查结构及受信关联；Approve 核验所需审批；
External Execution 由外部系统对具体操作独立落实权限、预算和安全前提；
Verify 关联执行后的只读证据。拒绝、待审批或证据不足不能自动进入执行或重试。

## 6. Approval 语义修正

**Approval is a governance mechanism, not a universal execution step.**

**Approval is not mandatory for every action.**

低风险动作可以由已有策略授权，无需逐次人工批准；本阶段不实现自动授权或自动审批。
HIGH / CRITICAL 需要人工或可信审批，本 Schema 因此要求 approval.required=true。
LOW / MEDIUM 仍可能被环境政策要求审批，不能由风险枚举推导自动放行。
风险不能扩大权限；CONTROLLED 不代表自动批准。READONLY / CONTROLLED / ADMIN
继续由现有授权边界管理，不在本最小 Schema 重复定义 permission 字段。

| required | reference | 结构意义 |
| --- | --- | --- |
| true | null | 合法的待审批声明，不能因结构合法执行。 |
| true | 非空标识 | 有待核验审批引用；可能过期、拒绝、撤销或不匹配，不能直接视为批准。 |
| false | null | 声明无需逐次审批；必须核对可信策略依据，不等于模型豁免。 |
| false | 非空标识 | 可关联已有审批记录，但仍不产生超出原权限的授权。 |

reference 是记录 ID，不是可自动获取的 URL 或执行令牌。
Schema 不验证身份真实性、审批有效期或签名。高风险条件检查也不能阻止恶意模型谎报 LOW，
所以 risk 和 required 都必须由受信治理来源核对。

## 7. Action Intent 不可执行原则

**Governance Intent is declarative, not executable.**

Intent 本身不能 execute()。没有执行目标地址、工具选择、命令或调用参数。
Schema 合法不代表环境可用、审批通过或执行获准。
本契约不足以精确绑定部署制品、机器人姿态或具体变更；未来若接入执行，外部受信记录
必须把精确操作和参数摘要关联到该意图及审批，不能把宽泛 purpose 当作通用执行授权。
最小契约没有批准任意动作的能力，这一限制不能通过解释自然语言弥补。

明确拒绝额外键：tool_name、command、shell、executor、retry、rollback、workflow、
planner、model_reasoning、prompt，以及任何其他未声明属性。所有嵌套对象同样封闭。

## 8. Verification 与实现边界

执行成功 != 目标达成。verification.required=true 表示需要观察证据，不表示证据已获得。
required=false 必须符合外部受信政策，不应被当作通用绕过验证的方法。
即使 false，evidence_type 仍必填且为 observation，保留明确的证据类型声明；它不强制采集。
成功标准、环境匹配、新鲜度和容差属于外部领域要求，当前 Schema 不实现验证算法。
没有证据或证据不充分时不能宣称目标已验证，也不能自动修复。

不修改 Harness、MCP、Registry、execution_enabled 或 require_tool_executor。
现有执行阻断保持；不创建 apps、Executor、Runtime、Action Adapter 或测试执行器。
结构校验示例见 [schema-validation-examples.md](schema-validation-examples.md)，
不将示例误认为真实授权或运行测试结果。

## V0.8-D3：离线 Validator 结果边界

Governance Validator result does not mean:

- authorized execution
- successful execution
- environment safety

`allow` 只表示：intent satisfies Kai governance boundary checks。
它不验证真实身份、Registry 成员或审批有效性，也不读取环境。
`deny` 表示至少一项固定离线检查未通过，不会执行拒绝后的修复或重试。
详见 [Governance Validator 设计](governance-validator-design.md)。
