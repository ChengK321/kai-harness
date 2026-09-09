# Kai Registry Layer V1.0

## 1. Registry 作用

Registry 是 Core Contract 与能力实现之间的声明式控制面，回答哪些 Agent 可接入、哪些 Tool 可调用、哪些 Environment 可管理、哪些 MCP Server 可连接。Registry 只描述身份、版本、能力与安全边界，不执行任务、不建立连接、不保存凭据。所有清单默认拒绝；注册不等于启用，启用不等于授权。

Registry 文件采用 UTF-8 YAML，并通过版本、必填字段、枚举和 ID 唯一性校验。Runtime 读取经过验证的不可变快照，并在任务与审计记录中保存 Registry 版本或摘要。

## 2. Agent Registry

Agent Registry 定义 Agent 逻辑身份、Adapter、能力、权限上限、Memory 范围和 Tool 范围。V1.0 清单为空，不绑定任何具体 Agent 实现。接入 Agent 时必须提供 `id`、`name`、`type`、`adapter`、`version`、`status`、`capabilities`、`permissions`、`memory_access` 和 `tool_access`。

`permissions` 只能是 `READONLY`、`CONTROLLED`、`ADMIN`。Registry 权限是上限而非运行授权；实际权限取 Agent Registry、任务授权、Tool Registry 和 Policy Engine 判定的最小交集。未显式允许的 Memory 层和 Tool 一律拒绝。

## 3. Tool Registry

Tool Registry 定义工具 ID、版本、类别、描述、权限等级、超时、审批要求及启用状态。类别为 `system`、`docker`、`filesystem`、`network`、`mcp` 或 `robotics`。所有工具默认 `enabled=false`；未注册、禁用或参数不符合工具 Schema 的调用必须拒绝。

高风险工具必须 `requires_approval=true`，其中 `ADMIN` 始终视为高风险；`CONTROLLED` 由 Policy Engine 根据动作、资源和可逆性决定。Tool Registry 不能绕过 `tools-policy.yaml`，两者冲突时采用更严格规则。

## 4. Environment Registry

Environment Registry 描述 Environment 插件和能力边界。V1.0 只登记 `vps-primary`，状态为 `registered`、连接模式为 `declarative_only`、`connected=false` 且执行关闭；这不是探测、连接或修改 VPS。Linux VPS 只是首个插件，Docker 与服务作为能力资源被未来 Adapter 暴露。

每个环境必须声明 connection 与 safety_policy。Environment 注册不会授予 Agent 控制权限；所有执行仍需 Tool Executor、Policy Engine 和必要的 Human Approval。

## 5. MCP Registry

MCP Registry 纳入统一 Registry 语义，每个 Server 具有 `server_id`、`transport`、`endpoint`、`tools`、`health_check` 和 `enabled`。V1.0 不注册实际 Server，默认 `enabled=false`。endpoint 只保存非敏感定位信息或 null；认证材料必须由外部受控注入，禁止进入 Registry。

MCP 暴露的工具还必须出现在 Tool Registry 且启用。Server 启用、Tool 启用和任务授权必须同时成立，任一缺失即拒绝。健康检查仅描述探针，不在 Registry 加载时自动连接。

## 6. Registry 与 Runtime 关系

执行关系为：

`Agent Adapter → Agent Runtime → Core Contract → Registry Snapshot → Memory Manager / Tool Executor / Environment Interface`

Runtime 在接纳任务时解析已验证快照，确认 Agent、能力和授权上限；Planner 只能选择交集中可见的工具；Tool Executor 在调用时再次检查 Tool/MCP/Environment 登记与策略。Registry 变更不应静默影响运行中任务：新任务使用新快照，运行中任务继续使用固定快照，安全撤销除外。

Registry 是声明来源，Policy Engine 是决策者，Executor 是执行者。任何组件不得以“已注册”为理由跳过权限或审批。

## 7. 未来 ROS2 扩展

ROS2 接入时新增 `type=ros2` 的 Environment 条目，声明 domain/namespace 引用、topic/service/action 能力、QoS、坐标系、数据新鲜度、失联策略和安全策略；连接细节不得包含 secret。对应动作以 `category=robotics` 注册为 Tool，并根据物理风险设置 `CONTROLLED` 或 `ADMIN`。

路径保持 `Runtime → Tool Executor → Environment Interface → ROS2 Adapter`。Isaac Sim 和真实 Robot Hardware 使用不同 environment ID、身份与审批范围，禁止跨环境复用授权。

## 8. 基础校验规则

加载前必须执行：

1. YAML 可被安全解析，顶层结构为 mapping，`version` 存在。
2. 每个条目包含各 Registry `entry_schema.required_fields` 指定字段。
3. 权限仅允许 `READONLY`、`CONTROLLED`、`ADMIN`。
4. 同一 Registry 内 ID 唯一；MCP 使用 `server_id`，其他 Registry 使用 `id`。
5. Tool 的 category、Environment 的 type/status、MCP transport 必须属于声明枚举。
6. Tool 默认禁用；高风险项必须审批；未知条目和未知权限 fail closed。
7. MCP 与 Environment 的 endpoint 可以为空，但不得包含用户信息、密码、Token 或内嵌凭据。

校验失败时不得发布 Registry 快照，并记录不含敏感值的错误位置。基础规则可由轻量 YAML 解析器实现，无需 Agent 框架或大型依赖。
