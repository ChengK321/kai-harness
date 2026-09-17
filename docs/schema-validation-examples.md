# Governance Intent Schema Validation Examples — V0.8-D2

以下为离线设计用例，不运行测试、不连接环境、不代表授权。
对应 [Schema](../configs/schema/governance-intent.schema.json)。既有应用测试框架不在本阶段
允许修改范围，因此将负例记录在 docs，不增加测试代码或依赖。

## Valid Example

```json
{
  "version": "1.0",
  "intent_id": "intent-001",
  "requester": {"type": "human", "id": "user-001"},
  "environment": {"environment_id": "vps-primary"},
  "target": {"resource": "service/nginx"},
  "purpose": "恢复网站可用性",
  "risk": "HIGH",
  "approval": {"required": true, "reference": null},
  "verification": {"required": true, "evidence_type": "observation"}
}
```

预期：结构通过，但处于待审批语义；示例身份不是实际认证。
Registry 执行关闭仍然有效，本例不能用于重启服务。
将 risk 改为 LOW、approval 改为 required=false/reference=null 也应结构通过，
但“无需审批”必须由可信政策核验，本阶段不执行该判断。

## Invalid Example

以下完整示例在合法基线中增加 command，预期因 additionalProperties=false 拒绝：

```json
{
  "version": "1.0",
  "intent_id": "intent-001",
  "requester": {"type": "human", "id": "user-001"},
  "environment": {"environment_id": "vps-primary"},
  "target": {"resource": "service/nginx"},
  "purpose": "恢复网站可用性",
  "risk": "HIGH",
  "approval": {"required": true, "reference": null},
  "verification": {"required": true, "evidence_type": "observation"},
  "command": "systemctl restart nginx"
}
```

下表每行均独立基于 Valid Example 修改，不叠加其他变化；字段路径是说明记法，不是执行指令。

| 用例 | 修改 | 预期拒绝原因 |
| --- | --- | --- |
| command | 添加顶层 command="systemctl restart nginx" | 顶层未知属性。 |
| tool_name | 添加顶层 tool_name="restart_service" | 顶层未知属性。 |
| executor | 添加顶层 executor="local" | 顶层未知属性。 |
| 缺少 environment | 移除整个 environment | 缺少必填属性。 |
| 未知 risk | risk="SAFE" | 不属于风险枚举。 |
| 其他执行/规划字段 | 分别添加 shell、retry、rollback、workflow、planner、model_reasoning、prompt | 每个字段均为未知属性，必须分别拒绝。 |
| 嵌套命令 | target 中添加 command | target 对象禁止未知属性。 |
| 直接地址字段 | environment 中分别添加 hostname、ip、ssh | environment 对象禁止未知属性。 |
| 空标识 | intent_id="" 或仅空格 | minLength 或非空白 pattern 不满足。 |
| 模型身份类型 | requester.type="model" | 非 human/service；即使填写 human 也仍需外部认证。 |
| 缺少主体 ID | requester 中移除 id | 缺少嵌套必填字段。 |
| 缺少审批语义 | approval 中移除 required 或 reference | 缺少嵌套必填字段。 |
| 错误布尔类型 | approval.required="false" | string 不是 boolean。 |
| 高风险免审批 | 保持 HIGH，approval.required=false | 条件约束要求 true。 |
| 空审批引用 | approval.reference="" | 非空字符串约束。 |
| 缺少验证语义 | verification 中移除 required 或 evidence_type | 缺少嵌套必填字段。 |
| 未知证据类型 | verification.evidence_type="shell_output" | 1.0 仅支持 observation。 |

## Schema 不能单独拒绝的语义伪造

一个符合字符串格式但不存在的 environment_id、冒充真实用户的 requester.id、
已撤销的 approval.reference 或谎报的 LOW 风险可能结构合法，必须由可信治理来源拒绝。
Schema 不建立 Registry 连接，不验证身份，不自动审批，也不能识别所有藏在文本中的指令。
文本字段永远不作为可执行内容。intent_id 重复及同 ID 内容冲突需要外部唯一性检查。

以上为预期断言与人工审阅材料，未宣称已通过完整 JSON Schema 校验器执行。
