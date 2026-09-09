# Kai Policy Engine V1.0 Design

## 1. 范围

本文只定义未来 Policy Engine 的决策模型，不实现引擎。Policy Engine 将 Agent、User、Task、Tool、Environment 与 Risk Level 的上下文组合成最终授权决定。Registry 是声明来源，Policy Engine 是决策者，Tool Executor 或 Environment Adapter 是执行者。

未来 Policy Registry 路径：

`/opt/kai/configs/registry/policy-registry.yaml`

该文件当前不创建，以免在策略结构冻结前形成可执行配置。

## 2. 决策输入

- Agent：Registry ID、状态、能力、权限上限、Memory 与 Tool scope。
- User：认证主体、角色、租户、授权范围、同意状态和审批资格。
- Task：task/session ID、目标摘要、允许工具、Memory policy、预算和数据分类。
- Tool：Registry ID、权限等级、side effect、参数摘要、审批要求和幂等能力。
- Environment：环境 ID、类型、状态、capabilities、connection 和 safety policy。
- Risk Level：由影响、可逆性、数据敏感度、物理风险、不确定性和历史异常计算。

正文不携带 secret；凭据存在与否只能作为受信声明，不进入决策日志。

## 3. 决策模型

决策结果为 `allow`、`deny` 或 `require_approval`，并附 policy ID/version、原因码、约束、有效期和 audit ID。求值顺序：

1. 验证身份、Registry Snapshot 和资源引用。
2. 计算 Agent、User、Task、Tool、Environment 权限交集。
3. 应用显式 deny；deny 永远优先。
4. 计算 Risk Level 并应用环境安全约束。
5. READONLY 可在全部约束满足时自动允许；CONTROLLED 按政策允许或审批；ADMIN 必须审批。
6. 未匹配、未知字段、策略冲突或审计不可用时 fail closed。

审批结果使用 `status=waiting_human` 与 `wait_reason=requires_approval`。审批只对绑定的主体、参数摘要、资源、策略版本和有效期有效，不能扩大原权限。

## 4. Policy Registry 草案职责

未来 Policy Registry 应包含版本、默认 deny、policy ID、优先级、适用主体与资源、conditions、effect、obligations、审批角色、有效期及审计要求。policy ID 必须唯一；规则变更形成新版本，运行中任务绑定固定快照，紧急 deny 可立即撤销。

## 5. 风险等级

建议使用 `LOW`、`MEDIUM`、`HIGH`、`CRITICAL`。不可逆、ADMIN、物理安全影响、凭据/权限变更和未知副作用不得低于 HIGH；机器人安全联锁或生命安全影响为 CRITICAL。风险等级不能降低 Core Contract 的最低审批要求。

## 6. 审计与解释

每次决策记录输入引用、命中的 policy、结果、原因码、约束、Registry Snapshot 和时间，不记录原始 secret。解释应足以复核授权路径，但不暴露敏感策略细节。执行组件必须验证决定未过期、请求未改变且 audit ID 一致。
