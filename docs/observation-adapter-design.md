# Kai Observation Adapter Interface — V0.7-D2

状态：**Design Only / Not Active Runtime**。本阶段仅定义 Adapter Contract，
不实现 Adapter、注册服务、采集调度器或生命周期状态机。

## 1. Observation Adapter 定位

Kai 是 Agent Control Plane。Observation Adapter 负责
**Environment-specific observation collection abstraction**：抽象不同环境的只读
状态采集，并将其标准化为 [Observation Contract](observation-design.md)。
它不实现 Agent Runtime、Planner、Memory Manager、Tool Executor 或自动修复，
也不修改环境。

| Adapter | 观察范围 |
| --- | --- |
| VPS Adapter | system metrics、service status。 |
| Docker Adapter | container state。 |
| ROS2 Adapter | node/topic/action observation；仅观察状态，不发布控制消息或提交 action goal。 |
| Robot Adapter | 获准的硬件状态与遥测，不能驱动执行器。 |

所有成功或部分成功的输出必须符合
[observation.schema.json](../configs/schema/observation.schema.json)。
Adapter metadata 与 Observation 数据是两个独立对象，不将 Adapter 描述直接混入输出。

当前 Observation 1.0 没有 ROS2 node/topic/action 或机器人专用遥测字段。
这些能力是未来方向，必须先演进并明确支持相应 Observation 契约版本；
不能在现有 `metadata`、`services` 或 `containers` 中伪装专用数据。
本阶段声明的能力仅涵盖 Observation 1.0 已有分区。

## 2. Adapter Interface

### Adapter metadata

元数据符合 [observation-adapter.schema.json](../configs/schema/observation-adapter.schema.json)。

```json
{
  "adapter_id": "vps-readonly",
  "version": "1.0.0",
  "environment_type": "vps",
  "capabilities": ["system.metrics", "service.status"],
  "permissions": ["READONLY"],
  "observation_schema_version": "1.0"
}
```

| 字段 | 定义 |
| --- | --- |
| `adapter_id` | 稳定逻辑标识，不是可执行文件路径、模块名或加载指令。 |
| `version` | Adapter 接口实现版本，采用三段数字版本号；不等于 Kai 项目版本。 |
| `environment_type` | `vps`、`docker`、`ros2` 或 `robot_hardware`；类型声明不代表已实现或已连接。 |
| `capabilities` | 非空且不重复的只读能力清单，限定为当前 Observation 分区可表达的能力。 |
| `permissions` | 固定为 `["READONLY"]`，不允许新增写权限或自动升级。 |
| `observation_schema_version` | 输出 Observation 契约版本，当前固定为 `1.0`。 |

六个字段均必填，顶层禁止未知字段。Adapter metadata 不保存凭据、主机地址、命令
或自动导入代码的信息。`version` 的变化不自动改变权限或输出契约。

能力映射：`system.metrics` → `system`，`service.status` → `services`，
`container.state` → `containers`，`repository.state` → `repository`，
`security.findings` → `security`。类型不自动授予任何能力；具体环境是否支持声明能力
需要未来接入校验确认，Schema 不据此访问环境。

### 逻辑调用约定

未来接口以 `collect(environment_id) → Observation` 表示一次只读采集。
这是语言无关的设计签名，不定义 HTTP 服务、CLI 命令或可执行实现。
调用方负责解析获准环境和只读访问范围；Adapter 不接受任意命令或任意目标地址。

输出的 `environment_id` 必须匹配请求，`version` 必须匹配
`observation_schema_version`；输出提供 `metadata.adapter_type`、
`metadata.adapter_version` 和 `metadata.collection_status`，分别记录来源类型、
Adapter 版本和本次采集完整性。调用方在带外保留 `adapter_id` 关联，不修改 Observation 1.0。
这些跨对象一致性约束由未来校验层验证，单个元数据 Schema 不保证它们成立。

部分采集失败采用 Observation 的 `partial` 和脱敏 `errors`；整体采集失败且仍能
构造合法 Observation 时使用 `failed`。无法产生合法结果时报告调用失败，调用方
不得将缺失结果伪造为健康或空环境。此契约不规定重试、任务调度或恢复流程。

## 3. Security Boundary

Adapter 默认且唯一权限为 **READONLY**。元数据必须显式声明 `["READONLY"]`；
缺失该字段是无效声明，不以隐式默认值绕过校验。

禁止：

- restart
- execute mutation command
- modify configuration
- write environment

沿用 Observation Layer 的禁止执行命令边界：未来通过获准的只读数据接口采集，
不建立通用命令执行入口，也不以命令作为失败回退方式。禁止自动修复、提权、
Docker 管理动作、ROS2 控制动作和机器人执行器写入。

登记和 Schema 合法不等于授权。实际访问需要执行环境落实最小权限；
`READONLY` 字符串不是沙箱，也不能证明第三方 Adapter 没有副作用。
不得采集 secret、凭据或敏感文件正文。环境文本是非可信数据，不可解释为执行指令。

## 4. Lifecycle

生命周期术语如下；图中的 `error` 是采集失败分支，不是每次采集的必经终点。

```text
registered
  ↓
available
  ↓
collecting
  ↓（失败）
error
```

- `registered`：声明已登记，尚不代表可用或获准采集。
- `available`：声明、版本和只读访问前提已通过校验，可接受采集请求。
- `collecting`：一次获准的只读采集正在进行。
- `error`：采集或可用性检查失败，不触发环境修改或自动修复。

成功采集后回到 `available`；部分结果可以返回，但采集状态按失败处理并记录原因。
`error` 只有在外部重新确认访问前提后才可回到 `available`，不定义自动重试。
这些是未来控制面观察执行状态的词汇，不是 Agent loop、Workflow Engine 或已实现的状态机。
生命周期不属于静态 Adapter metadata，也不向现有 Observation Schema 添加状态字段。

## 5. Compatibility

未来自研 Adapter、第三方 Adapter 和 Robot Adapter 均通过相同元数据契约、
输出契约和只读权限边界接入；来源不同不改变授权规则。
未知能力或不支持的输出版本应拒绝接入，而非静默降级或扩张 metadata。

本设计与 [V0.6 Control Plane](v0.6-control-plane-architecture.md) 的控制面和
Execution Environment 分离原则一致：Adapter 提供环境状态，外部 Harness 承担 Agent 能力。
不修改 Claude Harness、Runner、CLI、HarnessResult、V0.5 Registry 或 Validator；
当前代码不会自动加载该 Schema 或执行 Adapter。

## 6. 架构风险与限制

- 只读声明不能强制实现只读，未来需要独立环境权限和接入审查。
- ROS2 和机器人完整遥测超出 Observation 1.0，须先版本化扩展输出契约。
- 生命周期若扩展为规划、自动恢复或动作调度，将越过 Observation 边界。
- Schema 仅约束结构，不证明数据真实、新鲜、来源可信或跨对象身份一致。

本阶段仅记录这些边界，不实现执行机制或连接任何真实环境。
