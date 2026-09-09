# Kai Agent Runtime V1.0 Design

## 1. 目标与边界

Kai Agent Runtime V1.0 是框架无关的任务编排层，负责生命周期、计划、执行协调、观察、恢复与人工介入。它不绑定 LLM，不直接执行系统命令或访问 Memory 后端，也不替代受控边界组件。

## 2. Runtime 总体架构

`User → Gateway → Agent Runtime → Planner → Executor → Observer → Memory Manager → Tool Executor`

该链表示职责流而非固定串行顺序。Agent 接入关系是 `Agent Adapter → Agent Runtime → Kai Core Interface`：Adapter 转换框架协议，Runtime 决定状态与编排，Core Interface 定义稳定契约。

## 3. Agent Loop

`Observe → Plan → Act → Reflect → Memory Update`

Observe 获取授权上下文、Memory 和环境反馈；Plan 拆解目标并评估风险；Act 经受控接口执行；Reflect 判断成功失败并生成可审计摘要；Memory Update 生成带 provenance 的建议，由 Memory Manager 校验后提交。循环受任务时间、工具次数、恢复预算、取消信号和审批有效期限制。

## 4. Task State Machine

状态为 `accepted`、`planning`、`running`、`waiting_tool`、`waiting_memory`、`waiting_human`、`recovering`、`paused`、`succeeded`、`failed`、`cancelled`；转换以 `interfaces.md` 为规范来源。Runtime 是状态机 owner，使用 revision 防止并发覆盖，每次转换发布 `task.state_changed`。

`status` 只表示生命周期；`wait_reason` 表示等待原因。人工审批使用：

```json
{"status":"waiting_human","wait_reason":"requires_approval"}
```

旧 `status=requires_approval` 仅在兼容入口规范化，新 Runtime 不产生该格式。

## 5. Planning 模块

- 任务拆解：产生有依赖、完成条件和预算的步骤。
- 工具选择：只从任务允许列表与已注册能力交集中选择。
- 风险评估：按权限、敏感度、可逆性、物理影响和不确定性分级，交给 Policy Engine。

计划不是授权，Planner 不得通过拆分动作降低风险等级。

## 6. Executor 模块

Executor 通过 Tool Interface 调用工具，管理步骤、任务和调用超时、取消传播、并发限制和幂等键；按标准错误码处理失败。副作用状态未知时停止自动重试并请求人工，不得直接执行命令或访问 Environment。

## 7. Observer 模块

Observer 获取工具、Memory 和环境反馈，验证时间戳、完整性和数据质量，并判断执行结果。环境反馈必须经 `environment.observe()` 或注册工具取得；数据陈旧、传感器冲突或动作未确认时不得宣布成功。

## 8. Reflection 模块

Reflection 分析计划与实际结果，分类成功、部分成功、可恢复失败与不可恢复失败，形成简短 `reasoning_summary` 和经验，不输出私有思维链。经验写入前须摘要、脱敏，并标记 `source_type=agent_inference`、来源、创建主体、置信度和默认 `verified=false`。

## 9. Failure Recovery

| 分类 | 恢复策略 |
| --- | --- |
| Tool 失败 | 参数错误重新规划；暂时故障有限退避；副作用未知时人工核验 |
| Environment 失败 | 进入安全状态，重新观察或降级；物理影响不确定时人工核验 |
| Memory 失败 | revision 冲突时重读合并；暂时故障有限重试；禁止绕过 Manager |
| Agent 失败 | 隔离无效输出，重新调用或切换已注册 Adapter，保持审计链 |

只有可恢复且配置允许的错误进入 `recovering`。恢复有次数、时间和工具预算且不能提升权限；预算耗尽转 `failed`，安全不确定转 `waiting_human`。

## 10. Human-in-the-loop

所有 `ADMIN`、策略指定的 `CONTROLLED`、不可逆或范围不明的副作用、执行状态未知、重大 Memory 冲突，以及机器人急停恢复、越界动作或传感冲突必须请求人工。Runtime 发布 `approval.requested`；仅有效的 `approval.granted` 可恢复，拒绝、过期或参数变化不得执行原动作。

## 11. 未来机器人扩展

- ROS2：Adapter 映射 topic、service、action，实施允许列表、命名空间、Schema、QoS 和时间验证。
- Isaac Sim：作为仿真 Environment 插件；仿真和硬件身份隔离，审批不可跨环境复用。
- Robot Hardware：硬件网关实现 `observe/execute/status`，受速度、力、空间、安全区、租约、看门狗和急停约束。

连接路径为 `Runtime → Tool Executor → Environment Interface → ROS2/Isaac Sim/Hardware Adapter`。Runtime 不绕过插件访问设备；Camera 与 Sensor 数据携带采集时间、坐标系、质量和隐私分类，过期或失联时 fail safe。

## 12. 可观测性与一致性

任务、步骤、工具、Memory、审批和环境动作共享 `task_id`、`correlation_id`、`audit_id`。事件按任务维护 sequence，以 `event_id` 去重。崩溃恢复从已提交状态和事件重建，不猜测未确认副作用。
