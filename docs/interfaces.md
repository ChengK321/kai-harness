# Kai Core Interface V1.0

## 1. 范围与设计原则

Kai Core Interface V1.0 是 Agent、Memory、Tool 与 Environment 的稳定互操作协议。OpenHands、Codex CLI、Claude Code、LangGraph Agent、自研 Runtime 和 ROS2 Robot Agent 均通过适配器接入，基础设施不依赖具体 LLM、提示格式、编程语言、框架或存储实现。

共同原则：

- 所有请求和响应使用 UTF-8 JSON；字段名使用 `snake_case`，时间使用 UTC RFC 3339。
- 每个接口信封包含 `contract_version: "1.0"`；V1.x 只允许向后兼容地增加可选字段。
- `task_id`、`session_id`、`request_id`、`audit_id` 和资源 ID 在各自作用域内唯一。
- 调用必须携带经过 Gateway 验证的主体上下文；正文不携带密码、Token、私钥或其他 secret。
- 未识别的能力、工具、环境或权限默认拒绝；所有副作用必须可审计。
- 错误使用 `error-code.md`；状态变化发布符合 `event-schema.md` 的事件。

## 2. Agent Interface

### 2.1 接收任务

逻辑操作：`agent.run(task_request) -> task_response`。传输可由 HTTP、RPC、消息队列或本地进程适配器实现，不属于核心契约。

输入字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `contract_version` | string | 是 | 固定为 `1.0` |
| `task_id` | string | 是 | 任务唯一标识；重试时保持不变 |
| `session_id` | string | 是 | 会话标识，用于隔离上下文 |
| `user_request` | string | 是 | 用户原始意图，不是可执行系统命令 |
| `context` | object | 是 | 已授权的结构化上下文；可含 locale、附件引用和先前结果引用 |
| `allowed_tools` | array[string] | 是 | 本任务可请求的已注册工具；空数组表示无工具权限 |
| `memory_policy` | object | 是 | 可读写层、作用域、保留期和用户同意约束 |

输入示例：

```json
{
  "contract_version": "1.0",
  "task_id": "task_01JABC123",
  "session_id": "session_01JABC100",
  "user_request": "汇总已授权的项目状态并生成风险列表",
  "context": {
    "locale": "zh-CN",
    "correlation_id": "corr_01JABC120",
    "resource_refs": ["project:care-smart"]
  },
  "allowed_tools": ["project.status.read"],
  "memory_policy": {
    "read_layers": ["working", "semantic", "user"],
    "write_layers": ["working", "episodic"],
    "user_consent": true,
    "retention_days": 30
  }
}
```

### 2.2 返回结果

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `contract_version` | string | 是 | 契约版本 |
| `task_id` | string | 是 | 对应输入任务 |
| `status` | enum | 是 | 生命周期状态：`accepted`、`planning`、`running`、`waiting_tool`、`waiting_memory`、`waiting_human`、`recovering`、`paused`、`succeeded`、`failed` 或 `cancelled` |
| `wait_reason` | string/null | 是 | 等待原因；非等待状态为 null；人工审批使用 `requires_approval` |
| `result` | object/null | 是 | 面向调用方的结构化结果；失败时可为 null |
| `reasoning_summary` | string/null | 是 | 简短、可审计的决策摘要；不得要求或暴露模型私有思维链 |
| `memory_update` | object/null | 是 | 建议写入 Memory Manager 的变更集，不代表已持久化 |
| `error` | object/null | 是 | `{code, message, retryable, details}`；成功时为 null |

输出示例：

```json
{
  "contract_version": "1.0",
  "task_id": "task_01JABC123",
  "status": "succeeded",
  "wait_reason": null,
  "result": {"summary": "项目运行正常", "risks": []},
  "reasoning_summary": "根据已授权的只读项目状态生成摘要。",
  "memory_update": {
    "operations": [{"operation": "store", "layer": "episodic", "record_ref": "result:current"}]
  },
  "error": null
}
```

Runtime 必须验证适配器输出。Agent 只能建议 `memory_update` 和发起工具请求，不能把建议视为已执行。

### 2.3 Agent Lifecycle State Machine

`status` 只表示生命周期，`wait_reason` 表示等待原因。Agent Runtime 是状态事实的唯一管理者，负责校验转换、持久化 revision 和产生事件；Adapter、Tool 和 Memory 组件不得直接改写任务状态。

| 状态 | 进入条件 | 离开条件 |
| --- | --- | --- |
| `accepted` | Gateway 校验后 Runtime 接纳任务 | 开始规划转 `planning`；取消转 `cancelled` |
| `planning` | 新任务、重新规划或恢复后调整计划 | 计划就绪转 `running`；等待依赖转相应 waiting；不可规划转 `failed` |
| `running` | 正在推进计划步骤 | 请求工具、Memory、人工分别转 `waiting_tool`、`waiting_memory`、`waiting_human`；故障转 `recovering` 或 `failed` |
| `waiting_tool` | 已提交合法工具请求 | 成功转 `running`；可恢复失败转 `recovering`；否则转 `failed` |
| `waiting_memory` | 已提交合法 Memory 请求 | 完成转 `running`；可恢复失败转 `recovering`；否则转 `failed` |
| `waiting_human` | 等待人工输入、审批或确认 | 批准或补充后转 `planning`/`running`；拒绝转 `cancelled`/`failed` |
| `recovering` | 正在执行有界恢复 | 成功转 `planning`/`running`；预算耗尽转 `failed`；需人工转 `waiting_human` |
| `paused` | 有效暂停命令、维护窗口或资源治理 | 恢复转 `planning` 或先前安全状态；取消转 `cancelled` |
| `succeeded` | 目标完成且结果已验证 | 终态 |
| `failed` | 不可恢复或恢复预算耗尽 | 终态 |
| `cancelled` | 有效取消且停止后续动作 | 终态 |

终态不可逆；任意非终态可因有效取消转 `cancelled`；只有 `recovering` 执行自动恢复；`paused` 不产生新副作用。每次转换发布 `task.state_changed`，包含 `from_status`、`to_status`、`wait_reason`、`state_revision`、`trigger` 和 `actor`。人工等待另发 `approval.requested`，审批结果发 `approval.granted` 或 `approval.denied`。

关系为 `Agent Adapter → Agent Runtime → Kai Core Interface`：Adapter 负责把不同 Agent/框架转换为 Runtime 请求，不拥有状态、权限或 Memory 持久化决定权；Runtime 承载状态机、编排、预算、取消、恢复和审批；Core Interface 定义跨实现稳定契约，而非具体 Runtime 或 LLM。

兼容迁移：旧 V1.0 的 `status="requires_approval"` 在兼容入口规范化为 `status="waiting_human"` 和 `wait_reason="requires_approval"`。新生产者禁止把 `requires_approval` 作为 status；它只保留为 wait_reason 枚举值。

## 3. Memory Interface

### 3.1 边界

Agent 禁止直接访问 SQLite、JSON 文件、向量数据库或其他物理存储。所有操作必须经过 Memory Manager，由其完成鉴权、作用域隔离、脱敏、审计、保留期和后端路由。

统一记录结构：

```json
{
  "memory_id": "mem_01JABC200",
  "layer": "episodic",
  "namespace": "user:u_123",
  "content": {"summary": "只读状态检查成功"},
  "metadata": {
    "source_type": "agent_inference",
    "source_id": "task_01JABC123",
    "created_by": "agent-adapter:generic-agent",
    "confidence": 0.85,
    "verified": false,
    "created_at": "2026-09-02T08:00:00Z",
    "updated_at": "2026-09-02T08:00:00Z",
    "classification": "internal",
    "schema_version": "1.0",
    "expires_at": "2027-03-01T08:00:00Z"
  },
  "revision": 1
}
```

所有新建或更新的 Memory 记录都必须包含 `source_type`、`source_id`、`created_by`、`confidence` 和 `verified`。`source_type` 仅允许 `user_input`、`agent_inference` 或 `system_generated`；这些字段属于受保护的 provenance 元数据，普通内容更新不得静默改写。

旧记录迁移时，旧 `source` 的值只可重命名为 `source_id`。迁移程序必须从可信的历史消息、任务、事件或审计记录推导 `source_type` 与 `created_by`，并明确写入 `confidence` 和 `verified`。无法可靠补齐任一必填字段的旧记录必须隔离待确认，不得猜测默认值、直接通过新 Schema 或进入检索结果。新写入接口不再接受旧 `source` 字段。

### 3.2 操作

- `memory.store(request)`：写入新记录。必需字段为 `layer`、`namespace`、`content`、`metadata`、`idempotency_key`；返回 `memory_id`、`revision`、`stored_at`、`audit_id`。
- `memory.query(request)`：按 `layer`、`namespace`、结构化 `filters`、`query`、`limit`、`cursor` 查询；返回授权后的 `items`、`next_cursor`、`audit_id`。不得接受任意后端查询语句。
- `memory.update(request)`：以 `memory_id`、`expected_revision` 和受限 `changes` 更新；使用乐观并发控制，返回新 revision。
- `memory.delete(request)`：以 `memory_id`、`reason`、`deletion_mode` 删除；返回删除状态和审计 ID。物理删除及备份过期由政策决定。

每次请求均需 `contract_version`、`request_id`、`actor`、`task_id`（系统维护除外）和 `purpose`。Memory Manager 必须拒绝越层、越用户或越租户访问。

### 3.3 五层 Memory

| 层 | 生命周期 | 数据结构 | 存储建议 | 权限要求 |
| --- | --- | --- | --- | --- |
| Working | 当前任务/会话；任务结束或短 TTL 后清理 | 任务状态、计划、临时引用、revision | 内存或有 TTL 的键值存储；可重建 | 当前任务 Runtime 读写；其他会话禁止访问 |
| Episodic | 中长期；按政策摘要、归档或到期删除 | 时间、任务、结果、成功/失败标签、经验摘要、来源 | 可查询的文档/关系存储，可选语义索引 | 对应用户/租户授权读；写入需脱敏和任务来源 |
| Semantic | 随知识版本更新；来源失效时重建 | 文档片段、事实、来源、版本、置信度、索引元数据 | 对象/文档存储加可替换检索索引 | 只读消费者；授权采集器或管理员写；必须保留来源 |
| User | 用户关系期或同意撤回前；受保留政策限制 | 偏好、长期目标、同意状态、更新时间 | 强用户隔离的持久存储，可导出和删除 | 仅本人作用域及明确授权服务；敏感项需额外同意 |
| System | 按运维/合规周期长期保存 | 部署记录、配置变更、系统状态、版本及审计引用 | 版本化、追加优先的持久存储 | Agent 默认只读且最小披露；仅管理员/发布流程写入 |

向量索引是可重建的派生数据，不是事实来源；后端选择不得改变接口权限语义。

## 4. Tool Interface

### 4.1 执行链

`Agent → Tool Executor → Permission Check → Tool`

Agent 不能直接执行系统命令或直接调用工具实现。所有工具默认拒绝，必须在注册表中显式注册其名称、版本、参数 Schema、权限等级、资源边界和审计规则。

### 4.2 tool.request

```json
{
  "contract_version": "1.0",
  "request_id": "toolreq_01JABC300",
  "task_id": "task_01JABC123",
  "session_id": "session_01JABC100",
  "tool_name": "project.status.read",
  "parameters": {"project": "care-smart"},
  "permission_level": "READONLY",
  "timeout": 30,
  "audit_id": "audit_01JABC301"
}
```

`timeout` 单位为秒，由策略设置上限；调用方不能通过声明更低权限绕过注册权限。`audit_id` 在执行前生成并贯穿审批、调用与响应。

### 4.3 tool.response

```json
{
  "contract_version": "1.0",
  "request_id": "toolreq_01JABC300",
  "tool_name": "project.status.read",
  "status": "completed",
  "result": {"state": "healthy"},
  "started_at": "2026-09-02T08:00:00Z",
  "completed_at": "2026-09-02T08:00:01Z",
  "audit_id": "audit_01JABC301",
  "error": null
}
```

`status` 为 `accepted`、`requires_approval`、`running`、`completed`、`failed`、`denied` 或 `timed_out`。输出必须限长并脱敏；超时不代表外部副作用一定已撤销，Executor 必须报告可确认的最终状态。

### 4.4 权限等级

| 等级 | 用途 | 规则 |
| --- | --- | --- |
| `READONLY` | 读取状态和数据，无持久副作用 | 限定资源范围；仍需显式注册和审计 |
| `CONTROLLED` | 有限写入、启动任务或调用外部服务 | 强参数校验、幂等、影响范围限制；按政策审批 |
| `ADMIN` | 系统级配置、权限或高影响变更 | 默认拒绝；必须显式人工审批、强身份验证和完整审计 |

## 5. Environment Interface

### 5.1 插件模型

Environment 是对可观察、可操作资源的抽象。当前 VPS（Linux、Docker、care-smart、Xray）只是第一个 Environment 插件，不是协议本身。未来 ROS2、Isaac Sim、Robot Hardware、Camera 和 Sensor 通过独立插件实现相同契约和能力声明。

通用目标引用为 `{environment_id, resource_type, resource_id}`。插件注册时声明 `plugin_version`、`capabilities`、支持的操作 Schema、权限等级、安全边界和健康检查，不得把 secret 写入注册信息。

### 5.2 操作

- `environment.observe(request)`：读取传感、状态或资源快照；请求包含目标、观察类型、参数和一致性要求；响应包含 `observation`、采集时间、数据质量和审计 ID。原则上为 READONLY。
- `environment.execute(request)`：执行受控动作；请求包含目标、`action`、参数、幂等键、权限等级、超时和安全约束；必须经过 Tool Executor/Permission Check。响应包含执行状态、结果、可确认副作用和审计 ID。
- `environment.status(request)`：返回插件及目标的 `available`、`degraded`、`unavailable` 或 `unknown` 状态，以及能力版本、检查时间和不含敏感信息的诊断。

示例：

```json
{
  "contract_version": "1.0",
  "request_id": "envreq_01JABC400",
  "operation": "observe",
  "target": {
    "environment_id": "vps-primary",
    "resource_type": "service",
    "resource_id": "care-smart"
  },
  "parameters": {"observation": "health"},
  "timeout": 10,
  "audit_id": "audit_01JABC401"
}
```

物理设备插件还必须声明急停、动作边界、数据新鲜度和失联策略。任何环境的存在都不自动授予 Agent 操作权限。

## 6. 兼容性与扩展

实现方必须忽略不影响安全的未知可选字段，但拒绝未知枚举、权限等级和可执行操作。破坏性字段变更需要新的主版本。扩展信息统一放入 `extensions` 对象，并使用组织命名空间防止冲突。接口实现应通过对应 JSON Schema 校验结构，通过策略引擎校验语义与权限。
