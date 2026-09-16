# Action Schema Draft — V0.8-D0

状态：Proposed，待人工审核。本文件是设计说明，不是 JSON Schema。
未来目标 `configs/schema/action.schema.json` 本阶段不创建。
总体边界见 [Action 设计](action-design.md)。

## 字段、类型与约束

未来拟采用 Draft 2020-12，核心对象禁止未知字段；不同 action_type 使用独立、封闭的
parameters 结构，不复制旧 Tool Schema 的任意参数扩展作为执行入口。

| 必须字段 | 类型 | 拟定约束 |
| --- | --- | --- |
| version | string | 固定 1.0；未知版本拒绝。 |
| action_id | string | 非空，最长 128；同主体、环境范围内标识不可变动作。 |
| environment_id | string | 非空，最长 128；引用 Environment Registry，不是连接地址。 |
| requested_by | string | 非空，最长 128；可信入口核对认证主体，不信任模型自报。 |
| action_type | string | 小写字母开头，后续字母、数字、下划线、点、连字符；最长 128，必须在受信 allowlist 中。 |
| parameters | object | 按动作类型限定字段、资源标识、数值范围；禁止通用 command/script/endpoint 参数。 |
| permission | string enum | READONLY / CONTROLLED / ADMIN，复用既有枚举。 |
| side_effect | string enum | none / reversible / irreversible，复用 Tool Registry 枚举。 |
| approval | object 或 null | 对象只含必填 approval_id（非空、最长 128）；引用受信审批，不在请求内保存自报审批结论。 |

approval=null 仅表示尚无审批引用，不代表豁免。ADMIN、irreversible 或政策要求审批的
动作在 null 时不得分派。有 approval_id 也必须查验记录，不能凭字段存在就授权。
READONLY 必须 side_effect=none；其他组合还需可信动作定义校验，不按模型声明降低风险。

建议为未来执行显式增加以下字段，不让必需安全信息隐含在 parameters 中：

| 候选字段 | 类型 | 约束与来源 |
| --- | --- | --- |
| timeout | integer | 秒，至少 1；不超过适用最严格上限，当前全局为 120。 |
| audit_id | string | 受信入口生成，非空、最长 128；执行前须关联可用审计记录。 |
| correlation_id | string | 非空、最长 128；贯穿授权、请求、结果和观察关联。 |
| idempotency_key | string | 非空、最长 256；执行动作必需，不得声称单凭字段即可实现幂等。 |

这些字段是否纳入请求必填项或可信分派上下文，需在 Schema 冻结前决定；无论位置如何，
没有它们不能执行。策略版本、审批失效时间及资源绑定由受信记录提供，不接受调用方覆盖。

## 非可执行示例

以下是假设未来服务动作已完成定义后的请求草案；服务重启按保守的 ADMIN / irreversible
标注，不表示所有重启都属该等级。必须由具体动作风险定义决定。本例没有审批，不能执行；
当前 vps-primary 也关闭执行且没有登记该能力。

```json
{
  "version": "1.0",
  "action_id": "action-example-001",
  "environment_id": "vps-primary",
  "requested_by": "user:review-example",
  "action_type": "restart_service",
  "parameters": {"service_id": "example-service"},
  "permission": "ADMIN",
  "side_effect": "irreversible",
  "approval": null
}
```

restart_service 的 parameters 拟只允许 service_id，非空、最长 128，并且必须映射到已授权
的精确服务，不允许通配符、命令选项或 shell 字符串。查询优先使用 Observation Provider，
不通过增加 query_shell 之类动作绕过观察边界。

## ActionResult 草案

| 字段 | 类型 | 约束 |
| --- | --- | --- |
| action_id | string | 与请求一致。 |
| status | enum | completed / denied / failed / timed_out / unknown，单次结果，不是 Agent 生命周期。 |
| timestamp | string | RFC 3339 UTC。 |
| output | object 或 null | 按动作封闭定义，限长、脱敏。 |
| error | object 或 null | 对象只含 code、message，均非空字符串；不得包含凭据。 |
| observation_reference | string 或 null | 由控制面关联记录提供，绑定环境、采集时间及摘要；不是任意网络地址。 |

denied/failed/timed_out/unknown 应提供明确 error；completed 不等于观察验证成功。
现有 Observation 没有 observation_id，不能伪造字段或修改 Observation Contract 解决关联。

## 与旧契约的对应关系

| 新意图字段 | 旧契约对应 | 注意 |
| --- | --- | --- |
| version | contract_version | 不直接更名替换；独立契约分别验证。 |
| action_id | request_id | 未来可建立关联，不将动作自动等同整个 task/session。 |
| action_type | tool_name / Environment execute 的动作语义 | 必须显式映射到已有能力声明，不新建竞争性 Registry。 |
| environment_id、parameters 中的资源标识 | target.environment_id/resource_type/resource_id | 需动作专属受信映射，单独 environment_id 不够确定目标资源。 |
| permission | permission_level | 完全复用三类枚举。 |
| side_effect | Tool Registry side_effect | 请求不得覆盖可信声明。 |

旧 Environment execute 还要求 idempotency_key、safety_constraints，Tool Request 还要求
task_id、session_id 等；新草案不是旧 Schema 的合法替代品，不应直接送入原 Validator。
若未来桥接旧接口，必须满足全部旧字段及安全前提，而非因 Action 字段更少就省略。

## 校验分层与待审问题

结构校验检查必填、类型、枚举及未知字段；语义校验检查引用、动作参数与权限一致性；
授权/审批检查依赖受信主体、政策和审批记录。JSON Schema 本身不证明授权。

冻结前须决定：旧 require_tool_executor 约束的版本化迁移、执行上下文必填字段、
审批摘要规范、去重保留窗口、结果原因码与旧错误分类的映射，以及观察引用和完成条件。
当前不增加新状态机、通用 Policy Engine 或真实 Adapter 来填补这些待审项。
