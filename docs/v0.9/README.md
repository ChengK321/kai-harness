# Kai V0.9 Documentation

本目录补齐 V0.9 版本化文档入口，汇总仓库已有设计与原型事实，不替代或移动历史文件。
范围：**Environment Integration Readiness 的设计边界冻结**，不代表生产集成或真实执行验收。

| 文档 | 内容 |
| --- | --- |
| [架构总览](v0.9-architecture-overview.md) | V0.6–V0.9 演进、整体职责与生态边界。 |
| [Environment Registry](v0.9-environment-registry-design.md) | 环境身份、能力声明及当前原型限制。 |
| [Observation Integration](v0.9-observation-integration-design.md) | 只读证据、Provider 引用与缺失语义。 |
| [Capability Reference](v0.9-capability-reference-design.md) | 能力引用，不拥有调用和执行。 |
| [Integration Readiness Review](v0.9-integration-readiness-review.md) | 当前事实、缺口与进入后续集成的条件。 |
| [Freeze Summary](v0.9-freeze-summary.md) | 冻结范围、保留约束与变更原则。 |

决策记录：[ADR-0016 Integration Readiness Boundary](../adr/0016-v0.9-integration-readiness-boundary.md)。
Observation 是只读证据，Capability 是能力引用，Governance 是授权边界；
当前离线 Validator 的 allow 不是执行授权。
