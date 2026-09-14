# Kai Observation Layer Design — V0.7

状态：**Design Only / Not Active Runtime**。本阶段仅定义 Observation Contract，
不实现采集器、Environment Adapter 或运行服务，不连接真实 Environment。

## Observation Layer 定位

Kai 是 Agent Control Plane，不是 Agent Framework。Observation Layer 负责收集环境状态、
标准化环境信息，并为外部 Agent 提供上下文；不负责决策、执行或修改环境。
本设计不引入 Agent Runtime、Planner、Memory Manager、Tool Executor、Workflow Engine
或 LLM Router，也不改变当前 Claude Harness 的职责。

未来信息流为：`Environment → Environment Adapter → Observation JSON → Agent 上下文`。
该链路是设计方向，当前 Runner 尚未加载或注入 Observation。

## Observation Model

契约定义见 [observation.schema.json](../configs/schema/observation.schema.json)，
采用 JSON Schema Draft 2020-12。初始版本固定为 `1.0`；项目 V0.7 与契约版本分别管理。

```json
{
  "version": "1.0",
  "timestamp": "2026-09-14T08:00:00Z",
  "environment_id": "vps-sandbox",
  "system": {
    "cpu": {"usage_percent": 12.5},
    "memory": {"total_bytes": 8589934592, "used_bytes": 2147483648},
    "disk": {"total_bytes": 107374182400, "used_bytes": 21474836480}
  },
  "services": {
    "example-service": {"status": "running"}
  },
  "containers": {
    "example-container": {"status": "stopped"}
  },
  "repository": {
    "branch": "v0.7-observation",
    "revision": "example-revision",
    "dirty": false
  },
  "security": {
    "findings": []
  },
  "metadata": {
    "adapter_type": "vps",
    "adapter_version": "1.0",
    "collection_status": "complete"
  }
}
```

必需字段为 `version`、`timestamp` 和 `environment_id`。其余分区可选，
不要求所有 Environment 都具有 CPU、容器或代码仓库。

| 字段 | 语义 |
| --- | --- |
| `version` | Observation Contract 版本，当前只接受 `1.0`。 |
| `timestamp` | 本次状态采集完成时间，使用带 UTC 标记 `Z` 的 RFC 3339 时间。 |
| `environment_id` | 被观察环境的稳定逻辑标识；未来由控制面对照 Environment Registry 验证，Schema 不执行跨文件查找。 |
| `system.cpu` | 已定义采样窗口内的总体使用率，范围 0–100；采样窗口由 Adapter 文档明确。 |
| `system.memory` | 被观察环境的内存总量和已用量，单位 bytes。 |
| `system.disk` | Adapter 选定存储范围的总量和已用量，单位 bytes；范围应在 Adapter 文档明确。 |
| `services` | 以获准服务的逻辑标识为键的状态映射。 |
| `containers` | 以获准容器的逻辑标识为键的状态映射，不包含环境变量或运行凭据。 |
| `repository` | 当前环境中获准仓库的分支、修订标识和工作区是否有改动。 |
| `security` | 只读观察所得的问题摘要，不包含修复指令。 |
| `metadata` | Adapter 类型、版本、采集完整性及非敏感采集错误。 |

缺失字段表示未采集、不支持或不可访问，不等于零、健康或不存在。空映射/数组只表示
在本次获准且已观察的范围内没有条目，不证明整个环境为空或安全。状态无法判定时使用
`unknown`；部分失败时保留可用信息，并以 `metadata.collection_status=partial`
及 `errors` 描述缺失部分；完全失败使用 `failed`。错误信息必须脱敏。
`complete` 只表示 Adapter 声明的本次采集范围完成，不表示覆盖整个环境。

数据并非跨资源原子快照；消费者应根据 timestamp 判断新鲜度，不把历史观察当成实时事实。
已用量不应大于总量，这类跨字段语义以及采样范围、新鲜度和环境身份需要未来校验层处理，
不由本 Schema 自动保证。JSON Schema 校验器需要启用 `date-time` 格式断言才能完整校验日期。

## Security Boundary

**Observation: READ ONLY**。

禁止以下能力：

- restart service
- modify file
- execute command
- change config

未来 Adapter 只能通过明确授权的只读数据接口观察状态；Observation Contract 不接受
命令、动作或修复请求，也不授予执行权限。不得用命令执行器作为采集回退方式。
授权失败应报告不可观察，不得提升权限或改变环境来完成采集。

Schema 的核心对象及各记录均设置 `additionalProperties: false`。
`services` 和 `containers` 仅通过受约束的动态键映射容纳实例，记录结构仍封闭；
metadata 不作为任意 payload 或命令扩展入口。

Schema 校验不是权限沙箱，也不保证字段内容可信。环境返回的分支名、错误摘要等文本
均是外部数据，不是 Agent 指令；不得将其中内容提升为策略或执行授权。
采集侧应限制范围并脱敏，不收集 secret、访问令牌、私钥、进程环境变量或文件正文。
本契约不实现持久化 Memory、审计存储或自动修复。

## Future Extension

未来支持 VPS、Docker、ROS2 和 Robot Hardware，统一通过 **Environment Adapter**
转换为 Observation，而不是在控制面中建立新的 Agent 框架。

- VPS：获准系统资源和服务状态。
- Docker：获准容器的状态，不授予容器管理操作。
- ROS2：获准只读观察数据；不发布控制指令或调用动作服务。
- Robot Hardware：获准硬件遥测；不驱动执行器。

当前 `1.0` 只定义通用系统摘要，不将 ROS2、传感器、坐标系或机器人动作字段塞入 metadata。
未来需要专用遥测时发布明确版本的契约扩展，保留只读和封闭字段原则。
`adapter_type` 标识来源类型，不代表对应 Adapter 已实现或获得授权。

## 与现有架构的兼容性

本设计遵循 [V0.6 Control Plane 架构](v0.6-control-plane-architecture.md)以及
[ADR-0001](decisions/ADR-0001-kai-harness-boundary.md)：控制面提供观察上下文，
外部 Harness 承担 Agent 能力。
新 Schema 是独立契约，不修改 V0.5 Core Contract、Registry Schema 或 Validator，
也不声明现有 Validator 已支持 Observation。当前 CLI、Runner 和 HarnessResult 保持不变。
