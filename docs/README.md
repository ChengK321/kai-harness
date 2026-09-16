# Kai Documentation Index

Kai 项目文档分为以下三类。

当前生产实现以 **V0.6 Control Plane** 为准；具体已实现能力与目标能力的区别，
以当前架构文档中的说明为准。
V0.5 文档保留作为设计资产，不代表当前运行架构。

## 1. Current Implementation

- [V0.6 Control Plane](v0.6-control-plane-architecture.md)：当前架构、组件职责与执行边界。
- [kai-agent Harness](../apps/kai-agent/README.md)：薄 Claude Code Harness Runner 的运行与测试说明。

## 2. Historical Architecture

- [V0.5 Infrastructure](architecture-v0.5.0-freeze.md)：历史基础设施与契约冻结记录。
- [Registry](registry-design.md)：Registry 设计资产；Registry 与校验仍属于控制面职责，历史集成链路不代表当前 Runner 实现。
- [Runtime Design](runtime-design.md)：历史自研 Runtime 设计，供未来参考。
- [Memory Design](memory-design.md)：Memory 设计参考，当前 Kai 不实现持久化 Agent Memory。

## 3. Future Evolution

- [V0.8 Action Plane](action-design.md)：环境动作安全控制边界，D0 仅设计、待人工审核，未启用执行。
- [Action Schema 草案](action-schema-draft.md)：字段、约束及旧契约映射；尚未创建 JSON Schema。
- [ADR-0002 Action Boundary](adr/0002-action-boundary.md)：动作边界选择、取舍和执行前提。
- [Robot Agent](v0.6-control-plane-architecture.md#6-future-extension)：未来通过 Adapter 接入机器人 Agent。
- [ROS2 Environment](runtime-design.md#11-未来机器人扩展)：历史设计中的 ROS2 环境扩展参考。
- Embodied AI：未来具身智能方向，参考 Robot Agent 与 ROS2 Environment 设计；尚不代表当前运行能力。
