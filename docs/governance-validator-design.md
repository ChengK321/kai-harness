# Offline Governance Validator — V0.8-D3

## 1. Validator 定位

独立离线原型，仅检查 Governance Intent 1.0 的治理声明边界。
不是 Policy Engine，不是 Authorization System，不是 Executor。
代码位于 `apps/kai-governance-validator`，只使用标准库；不接入 Harness 或 Registry。

## 2. 数据流

```text
Governance Intent（内存对象或调用方指定的本地 JSON 文件）
  ↓
Validation（固定离线检查）
  ↓
Decision Report（allow / deny）
```

报告含 intent_id 和检查列表，每项包含 name、passed/failed 与 reason。
任一检查失败即 deny。输入不合法时返回报告，不通过异常回显文件路径或敏感原文。
文件只读打开；不读取环境、网络、审批引用或执行指令。

## 3. Validator 能做什么

- Contract validation：固定检查九个必填字段、版本、类型、长度、枚举及封闭嵌套结构。
- Boundary validation：environment 仅接受 environment_id；递归拒绝 command、tool_name、
  shell、executor、workflow、retry、rollback、planner、model_reasoning、prompt 等字段。
- Safety rejection：结构不合法、未知字段、非法风险、高风险未声明审批要求时返回 deny。

实现是针对既有 Contract 1.0 的显式检查，不是通用 Draft 2020-12 校验器或动态规则系统。
LOW/MEDIUM 不强制 approval.required=true；HIGH/CRITICAL 按 D2 要求 true。
待审批引用为 null 仍可结构通过；verification 必须有 boolean required 和 observation evidence_type。

## 4. Validator 不做什么

- Decision making：不决定业务动作、是否真正获准执行或风险等级。
- Planning：不生成步骤、工具选择、重试或修复计划。
- Execution：不执行命令、不创建 Tool/MCP Caller、不访问真实环境。
- Approval：不签发审批，不核验审批记录，不把结构通过视为批准。

风险不等于权限。身份、Registry 成员、审批真实性、新鲜度、证据与执行安全均不在离线检查内。
不存储唯一性状态；不拒绝所有可能伪装成 ID 的地址文本，也不扫描目的文本中的所有指令。
这些限制不会被 allow 覆盖。已有 execution_enabled 和 require_tool_executor 保持原样。

## 5. 验证与后续

unittest 使用内存数据和 mock 文件，覆盖有效声明、缺字段、执行字段、模型推理字段、
非法风险、低风险无人工审批、嵌套类型、高风险待审批、文件错误和无副作用路径。
Schema required 字段用于回归一致性检查，不宣称运行了完整 Schema 引擎。
契约版本变更需显式评审同步；下一步优先补离线契约一致性用例，不开放执行能力。
