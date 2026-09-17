# ADR-0005 Governance Validator Boundary

状态：V0.8-D3 原型 / 待人工审核。

## Context

D2 的治理声明需要可重复的离线边界检查，以验证缺字段、非法风险和执行语义能否被拒绝，
同时避免把所有请求都要求人工审批。该需求不要求连接真实环境或实现授权系统。

## Decision

Governance Validator 只检查 Governance Intent 1.0 契约及固定边界规则。
输入是内存对象或本地 JSON 文件；输出 allow/deny 报告，不触发动作。
allow 仅说明通过离线检查，不证明身份、审批、环境安全或执行成功。
不实现风险评分、规则 DSL、动态策略、自动审批、重试和修复。

## Consequences

优点：可测试、不依赖环境、防止执行层膨胀；低风险不需要人工审批的声明可被接受。
限制：不代表真实授权或执行成功；固定规则需随契约明确维护，不能作为通用 Schema 引擎。
已有 Registry 的执行关闭与 Executor 要求不被覆盖。

## Rejected Alternatives

1. Policy Engine：通用政策求值、风险评分和动态规则超出离线契约检查。
2. Executor：把 allow 接到执行入口会混淆结构检查与真实授权。
3. Workflow：串联审批、重试、执行和修复会引入本阶段不需要的调度系统。

参考 [设计](../governance-validator-design.md)、[D2 契约](../governance-intent-design.md)。
