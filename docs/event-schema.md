# Kai Event Schema V1.0

## 1. 通用事件信封

所有事件使用 UTF-8 JSON。事件应不可变、可追加、可按 `event_id` 去重；时间使用 UTC RFC 3339。事件不得包含密码、Token、私钥或未经授权的完整用户内容。

```json
{
  "schema_version": "1.0",
  "event_id": "evt_01JABC500",
  "timestamp": "2026-09-02T08:00:00Z",
  "source": "agent-gateway",
  "event_type": "task.created",
  "task_id": "task_01JABC123",
  "session_id": "session_01JABC100",
  "correlation_id": "corr_01JABC120",
  "sequence": 1,
  "payload": {},
  "metadata": {
    "environment_id": "vps-primary",
    "contract_version": "1.0"
  }
}
```

必填字段为 `schema_version`、`event_id`、`timestamp`、`source`、`event_type` 和 `payload`。与任务相关的事件还必须包含 `task_id`、`session_id`、`correlation_id` 和任务内单调递增的 `sequence`。跨生产者不承诺全局顺序；消费者必须幂等。

## 2. 标准事件

### `task.created`

由 Gateway 在任务校验并持久化标识后发出。

```json
{"payload":{"request_summary":"生成项目风险摘要","allowed_tools":["project.status.read"],"memory_policy_ref":"policy:default@1.0"}}
```

### `task.started`

由 Agent Runtime 开始处理任务时发出。

```json
{"payload":{"agent_adapter":"generic-agent","adapter_version":"1.0.0","started_at":"2026-09-02T08:00:01Z"}}
```

### `tool.called`

由 Tool Executor 在权限判定完成、实际调用之前发出。`parameters_summary` 必须脱敏。

```json
{"payload":{"audit_id":"audit_01JABC301","tool_name":"project.status.read","permission_level":"READONLY","parameters_summary":{"project":"care-smart"},"timeout":30}}
```

### `tool.completed`

由 Tool Executor 在工具达到可确认的终态时发出。

```json
{"payload":{"audit_id":"audit_01JABC301","tool_name":"project.status.read","status":"completed","duration_ms":420,"result_summary":{"state":"healthy"},"error":null}}
```

### `memory.saved`

由 Memory Manager 在存储提交成功后发出，不在仅收到 Agent 建议时发出。

```json
{"payload":{"audit_id":"audit_01JABC510","memory_id":"mem_01JABC200","layer":"episodic","namespace":"user:u_123","revision":1,"content_digest":"sha256:example"}}
```

### `error.occurred`

由发现错误的边界组件发出。不得在 `details` 中复制敏感输入。

```json
{"payload":{"error":{"code":"TOOL_ERROR_3003","message":"工具执行超时","retryable":true},"related_event_id":"evt_01JABC505","audit_id":"audit_01JABC301","component":"tool-executor"}}
```

## 3. 演进与投递

- V1.x 可以增加可选字段，不得删除字段或改变既有语义；破坏性变化升级主版本。
- 未知 `event_type` 应安全忽略或进入隔离队列，不能导致执行副作用。
- 事件至少一次投递时，消费者以 `event_id` 去重，以 `sequence` 检测任务内缺口。
- `payload` 只存必要摘要或资源引用；大对象放在受控存储并通过引用访问。
- 日志与事件是不同记录：事件描述领域事实，审计日志证明主体、权限判定与操作轨迹。
