# ADR-0001 Observation Provider Boundary

## 1. Context

Kai 是 Agent Control Plane，不是 Agent Framework。Observation Layer 只负责
环境状态观察，环境专属采集由 Environment Adapter 承担。

Harness 不应直接依赖 Environment Adapter，否则会与具体环境的采集接口、
数据转换和异常处理耦合，增加替换 Adapter 及支持新环境的成本。
当前已提供 Observation Provider 接口；本决策定义未来 Harness 集成的稳定边界，
不表示现有 Harness 已接入 Observation。

## 2. Decision

采用以下稳定依赖边界：

```text
Harness
  |
Observation Provider
  |
Environment Adapter
```

Harness 通过 `ObservationProvider.get_observation(environment_id)` 获取
Observation Contract V1.0，不直接调用具体 Adapter。
Provider 隔离具体 Adapter 的调用细节和异常；Adapter 负责只读采集与格式转换。
返回数据必须符合对应版本的 Observation Contract。

Provider 不保存状态、不执行命令、不访问网络、不修改环境，也不承担分析、决策、
自动修复或 Memory 职责。环境访问权限由执行环境落实，接口声明不构成访问授权。

## 3. Consequences

正面影响：

- Adapter 可替换，Harness 不依赖具体采集实现。
- 支持 VPS、ROS2 和 Robot 环境扩展。
- 降低 Harness 与环境专属逻辑之间的耦合。

负面影响：

- 增加一层抽象，需要维护调用与异常转换约定。
- 需要维护 Provider 接口及 Observation 输出契约的版本兼容性。

## 4. Rejected Alternatives

### Harness 直接调用 Adapter

拒绝将具体环境的采集接口和异常处理引入 Harness。该方式使环境变化影响 Harness，
削弱 Adapter 的可替换性。

### Observation Adapter 同时负责分析

拒绝将采集、格式转换与分析混合。Adapter 应报告观察事实及采集错误，
不生成决策或修复动作；解释和决策交给外部 Agent 或明确分离的消费方。

### Observation 层承担 Memory 职责

拒绝在 Observation 层建立持久化 Agent Memory、历史检索或记忆管理。
单次环境状态与长期记忆具有不同职责，合并将扩大控制面范围并引入状态管理耦合。

## 5. Future

未来可通过 Provider 接入第三方 Adapter、ROS2 Adapter 和 Robot Adapter，
保持 Harness 面向统一接口。新 Adapter 必须遵循只读边界和明确版本的输出契约。

当前 Observation 1.0 尚未定义 ROS2 或机器人专用遥测字段；需要这些数据时，
应先版本化扩展契约，不通过未知字段或 metadata 绕过约束。
第三方接入不自动获得环境权限，也不允许引入执行、自动修复或 Memory 能力。
