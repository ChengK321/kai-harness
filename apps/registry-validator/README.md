# Kai Registry Validator V1.1

轻量、只读的 Registry 校验器。它读取四类 Kai Registry 和独立 Registry JSON Schema，输出 JSON 报告，不修改 Registry、不连接 Environment，也不执行 Tool。

## 运行

在本目录执行：

```bash
python3 -m app.validator
```

成功退出码为 `0`，失败为 `1`。报告包含 `validator_version`、`checked_files`、`checked_schema_files`、`cross_reference_checks`、`errors` 和 `warnings`。

## 验证流程

`Registry → Schema Loader → JSON Schema Validation → Business Rules → Cross References → Report`

结构规则来自 `/opt/kai/configs/schema/registry/`，Validator 不读取 Registry 内的 `entry_schema` 作为验证依据，也不会加载上级目录中的 Core Contract Interface Schema。业务层检查 ID 唯一、default deny 和高风险审批；跨引用层检查 Agent Tool、Agent Environment 和 MCP Tool 引用。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

Python 标准库负责 JSON Schema 子集校验、CLI、报告和测试。YAML 解析复用系统已有 PyYAML，并通过自定义 SafeLoader 拒绝重复 Key；本应用不会自动安装依赖。

## 安全边界

- 默认只读四份 Registry 和四份隔离 Registry Schema。
- YAML 重复 Key 返回 `YAML_DUPLICATE_KEY`，不允许静默覆盖。
- 验证通过不等于授权；Runtime 和 Policy Engine 仍须逐次决策。
- 错误报告只包含位置和摘要，不回显原始配置内容。
