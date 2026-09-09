# Kai Error Code V1.0

## 1. 格式

标准错误对象：

```json
{
  "code": "TOOL_ERROR_3003",
  "message": "工具执行超时",
  "retryable": true,
  "details": {"tool_name": "project.status.read"},
  "audit_id": "audit_01JABC301"
}
```

`message` 可本地化且不得含 secret；程序只能依据稳定的 `code`、`retryable` 和结构化 `details` 决策。错误编号发布后不得改变含义或复用。未知错误按所属分类的通用内部错误处理。

## 2. 编号范围与处理策略

| 分类 | 编号范围 | 含义 | 默认处理策略 |
| --- | --- | --- | --- |
| `AGENT_ERROR` | 1000–1999 | Agent 输入、生命周期、适配器或结果校验失败 | 修正请求；仅对明确的暂时故障限次重试；保留任务现场 |
| `MEMORY_ERROR` | 2000–2999 | Memory 校验、查询、并发、保留或后端失败 | 不绕过 Memory Manager；冲突时重读，暂时故障退避重试 |
| `TOOL_ERROR` | 3000–3999 | 工具注册、参数、执行、超时或结果失败 | 默认拒绝；副作用不确定时先核验，禁止盲目重试 |
| `MCP_ERROR` | 4000–4999 | MCP 注册、协议、连接、能力或远端服务失败 | 检查能力协商；暂时连接故障可熔断后重试 |
| `ENVIRONMENT_ERROR` | 5000–5999 | 环境插件、目标、观察、动作或状态失败 | 转入安全状态；物理环境优先停止动作并请求人工检查 |
| `SECURITY_ERROR` | 6000–6999 | 身份、授权、策略、隔离、审计或敏感数据风险 | 不自动重试；拒绝操作、记录审计并按严重度告警 |

## 3. V1.0 标准错误

| Code | 含义 | Retryable | 处理策略 |
| --- | --- | --- | --- |
| `AGENT_ERROR_1000` | Agent 未分类内部错误 | 否 | 标记任务失败并保留关联 ID |
| `AGENT_ERROR_1001` | 任务输入无效 | 否 | 返回字段级校验信息 |
| `AGENT_ERROR_1002` | 不支持的契约版本 | 否 | 协商受支持版本 |
| `AGENT_ERROR_1003` | Agent 适配器不可用 | 是 | 限次退避或切换已注册适配器 |
| `AGENT_ERROR_1004` | Agent 输出不符合契约 | 否 | 隔离输出并修复适配器 |
| `AGENT_ERROR_1005` | 任务已取消或状态冲突 | 否 | 查询任务最终状态 |
| `MEMORY_ERROR_2000` | Memory 未分类内部错误 | 是 | 退避并保持上层一致性 |
| `MEMORY_ERROR_2001` | Memory 请求无效 | 否 | 修正层、作用域或过滤条件 |
| `MEMORY_ERROR_2002` | 记录不存在 | 否 | 核对 ID 与作用域 |
| `MEMORY_ERROR_2003` | revision 冲突 | 是 | 重读后重新合并，禁止覆盖更新 |
| `MEMORY_ERROR_2004` | Memory 后端暂时不可用 | 是 | 熔断、退避，不直连后端 |
| `MEMORY_ERROR_2005` | 保留或删除策略冲突 | 否 | 请求政策授权或修正操作 |
| `TOOL_ERROR_3000` | Tool 未分类内部错误 | 否 | 保留审计记录并人工检查 |
| `TOOL_ERROR_3001` | 工具未注册或未启用 | 否 | 拒绝并完成显式注册流程 |
| `TOOL_ERROR_3002` | 工具参数校验失败 | 否 | 按 Schema 修正参数 |
| `TOOL_ERROR_3003` | 工具执行超时 | 条件性 | 先确认副作用状态再决定重试 |
| `TOOL_ERROR_3004` | 工具执行失败 | 条件性 | 根据工具幂等性和错误详情处理 |
| `TOOL_ERROR_3005` | 工具结果无效或过大 | 否 | 截断/隔离并修复工具适配器 |
| `MCP_ERROR_4000` | MCP 未分类内部错误 | 是 | 熔断并诊断连接 |
| `MCP_ERROR_4001` | MCP 服务未注册 | 否 | 拒绝并注册服务 |
| `MCP_ERROR_4002` | MCP 协议或版本不兼容 | 否 | 完成版本协商或升级适配器 |
| `MCP_ERROR_4003` | MCP 连接失败 | 是 | 有上限地退避重试 |
| `MCP_ERROR_4004` | MCP 能力不可用 | 否 | 重新发现能力或降级 |
| `MCP_ERROR_4005` | MCP 远端调用失败 | 条件性 | 按幂等性和远端状态处理 |
| `ENVIRONMENT_ERROR_5000` | Environment 未分类内部错误 | 否 | 进入安全状态并检查插件 |
| `ENVIRONMENT_ERROR_5001` | 环境插件未注册/不可用 | 是 | 禁止执行并检查插件健康 |
| `ENVIRONMENT_ERROR_5002` | 目标资源不存在 | 否 | 更新资源引用 |
| `ENVIRONMENT_ERROR_5003` | 不支持的环境能力 | 否 | 重新协商 capabilities |
| `ENVIRONMENT_ERROR_5004` | 环境观察数据陈旧或无效 | 是 | 重新观察；不得据此执行高风险动作 |
| `ENVIRONMENT_ERROR_5005` | 环境动作失败或状态未知 | 否 | 停止后续动作并人工核验 |
| `SECURITY_ERROR_6000` | Security 未分类错误 | 否 | 拒绝、审计和告警 |
| `SECURITY_ERROR_6001` | 身份验证失败 | 否 | 拒绝，不泄露身份细节 |
| `SECURITY_ERROR_6002` | 权限不足 | 否 | 拒绝并记录策略版本 |
| `SECURITY_ERROR_6003` | 策略默认拒绝 | 否 | 通过受控流程显式授权 |
| `SECURITY_ERROR_6004` | 需要人工审批 | 否 | 挂起操作等待有效审批 |
| `SECURITY_ERROR_6005` | 检测到敏感数据风险 | 否 | 阻断输出、脱敏并告警 |
| `SECURITY_ERROR_6006` | 审计记录失败 | 否 | fail closed，禁止执行副作用 |

“条件性”表示只有操作可证明幂等或已确认无副作用时才可重试。任何重试均应有次数上限、指数退避和相同幂等键。
