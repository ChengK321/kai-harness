# Kai Infrastructure V0.5.0 Release Notes

## 版本概述

V0.5.0 是 Kai AI Infrastructure 的首个正式架构冻结版本。该版本固定基础目录、Core Contract、五层 Memory 与 Provenance、统一 Registry Layer，以及只读 Registry Validator V1.1。

## 核心能力

- 框架无关的 Agent、Memory、Tool 和 Environment 接口边界。
- `accepted` 至终态的 Agent 生命周期与人工等待兼容语义。
- 五层 Memory 及强制 Provenance 数据结构。
- Agent、Tool、Environment、MCP 的默认拒绝 Registry。
- 外部 Registry Schema、重复 YAML Key 检测和跨 Registry 引用校验。
- Schema 失败后的安全门控和结构化 JSON 错误报告。
- Registry Snapshot 的后续版本设计基础。

## 安全基线

V0.5.0 不启用任何 Agent、Tool 或 MCP Server，不连接 Environment，不包含运行凭据。Agent 不得直接执行系统命令或访问 Memory 后端；所有未知能力与权限默认拒绝。

## 范围外组件

本版本不包含 Agent Runtime、Policy Engine、Tool Executor、MCP Runtime 或 Robot Adapter 的运行实现，也不创建或修改任何系统服务。

## 升级方向

V0.5.1 将聚焦 Registry Snapshot 归档与完整性；V0.6 将基于冻结契约开发最小 Runtime Prototype。
