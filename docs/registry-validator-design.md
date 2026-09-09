# Kai Registry Validator V1.1

## 1. 设计目标

V1.1 将 Validator 从 Registry 自描述规则升级为外部 Schema 驱动和跨 Registry 一致性检查。它在 Snapshot 发布前阻止语法、结构、身份、权限、默认策略和引用错误进入 Runtime。Validator 只读运行，不执行 Tool、不连接 Environment。

Core Contract Schema 保留在 `/opt/kai/configs/schema/`；Registry Schema 位于 `/opt/kai/configs/schema/registry/`。两者命名空间、文件名和用途严格隔离。

## 2. 验证流程

`Registry → Schema Loader → JSON Schema Validation → Business Rule Validation → Cross Reference Validation → Report`

1. Schema Loader 加载四份外部 Registry Schema，并记录 `checked_schema_files`。
2. YAML Parser 使用安全加载器，重复 Key 立即产生 `YAML_DUPLICATE_KEY`。
3. Schema 层检查 required、type、enum 和 nested structure，不依赖 Registry 的 `entry_schema`。
4. Business Rule 层检查 ID 唯一、default deny 和高风险审批。
5. Cross Reference 层检查 Agent Tool、Agent Environment、MCP Tool 三类引用。
6. JSON Report 输出 Validator 版本、文件、Schema、跨引用统计、errors 和 warnings。

## 3. Schema 实现边界

运行环境没有完整 `jsonschema` 包，本阶段不安装新依赖。轻量引擎实现当前四份 Schema 使用的 Draft 2020-12 关键字：`type`、`required`、`properties`、`additionalProperties`、`items`、`enum`、`const`、`minLength`、`minimum` 和 `uniqueItems`。

不支持的 Schema 关键字不能被静默加入生产 Schema；未来引入完整实现时，应先运行一致性测试并保持错误语义稳定。Schema 只描述结构，授权语义继续由业务规则和未来 Policy Engine 决定。

## 4. 错误分类

- `SCHEMA_LOAD_ERROR`：外部 Schema 缺失、不可读或不是合法 JSON 对象。
- `SCHEMA_*`：实例违反类型、必填字段、枚举或其他结构约束。
- `YAML_DUPLICATE_KEY` / `YAML_PARSE_ERROR`：YAML 重复键或解析错误。
- `DUPLICATE_ID`、`DEFAULT_*`、`HIGH_RISK_APPROVAL`：业务不变量失败。
- `CROSS_AGENT_TOOL_NOT_FOUND`：Agent 引用不存在 Tool。
- `CROSS_AGENT_ENVIRONMENT_NOT_FOUND`：Agent scope 引用不存在 Environment。
- `CROSS_MCP_TOOL_NOT_FOUND`：MCP 引用不存在 Tool。

## 5. CI/CD 与 Runtime

CI 在产生 Registry Snapshot 前运行 `python3 -m app.validator`，以退出码阻断失败发布并归档 JSON 报告。Runtime 只能加载通过指定 Validator 版本验证的固定 Snapshot，但仍必须由 Policy Engine 在每次调用时结合主体、任务与环境做最终授权。Validator 失败时保持上一有效 Snapshot 或 fail closed。

## 6. 兼容性

Registry 内现有 `entry_schema` 可以暂时保留，V1.1 对它不作结构信任。可选 `side_effect` 缺失时兼容通过，出现时必须符合枚举；可选 `execution_scope` 缺失时兼容通过，出现时其 environments 必须是字符串数组且引用已注册环境。
