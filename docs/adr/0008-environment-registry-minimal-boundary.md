# ADR-0008 Environment Registry Minimal Boundary

Status: Proposed / V0.9-D1

## Context

Kai 需要关联 Agent、Observation 和未来 Governance Intent 的目标环境。

但环境登记容易演变为 CMDB、IAM 或部署平台，因此必须保持最小边界。

## Decision

Environment Registry 只负责：

- 唯一环境身份
- 环境类型声明
- 信任级别声明
- 能力声明查询

Registry 不负责：

- 身份认证
- 权限签发
- Secret 管理
- 执行动作
- 状态采集
- 工作流编排

## Consequences

优点：保持 Control Plane 薄边界。

限制：真实授权、安全策略和环境状态必须由其他可信系统提供。

## Future

未来若接入 VPS、ROS2 或其他环境，应通过 Adapter 映射，而不是扩展 Registry 职责。
