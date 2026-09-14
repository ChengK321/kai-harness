# Kai V0.6 架构定位

Kai 当前定位是 **Agent Control Plane**，只实现薄 Control/Application Layer，
不重新实现通用 Agent Harness。该边界遵循
[ADR-0001](decisions/ADR-0001-kai-harness-boundary.md)。

当前执行链路：**Kai → Claude Code Harness → Model Provider（当前为 DeepSeek）**。
Claude Code 承担 Agent 执行能力，Kai 控制执行边界并收集执行结果。

## Kai 的职责边界

- **workspace boundary**：限定可启动任务的工作目录，验证路径与符号链接边界。
- **execution control**：控制 Harness 启动参数、工具范围、执行预算和超时。
- **registry**：管理能力与环境的声明；登记不等于启用或授权。
- **validation**：校验声明与约束，不执行声明中的 Agent 或工具。
- **observation**：收集执行状态、输出、耗时、费用与权限拒绝信息。
- **audit**：为执行与配置提供可追溯记录的控制面职责。

上述列表是职责划分，不代表完整 Control Plane 已实现。当前 Thin Harness Runner
负责 workspace 校验、固定 CLI 参数、子进程执行和结果解析；Registry Validator
是独立校验模块。Runner 尚未实现 Registry 绑定或持久化审计系统。

## Kai 不负责的能力

- LLM reasoning
- Agent loop
- Planner
- Memory backend
- Model provider

推理由模型提供，Agent loop、计划及工具调用由 Claude Code Harness 承担。
Kai 不实现持久化 Agent Memory，也不建立自己的模型 Provider Framework。

## 历史设计与当前实现

[旧架构](architecture.md)及 [V0.5 冻结文档](architecture-v0.5.0-freeze.md)
保留历史设计和契约背景，其中自研 Runtime 的下一阶段路线不再代表 V0.6 当前方向。
[Runtime 设计](runtime-design.md)、[Memory 设计](memory-design.md)、
[Runtime 配置](../configs/agent-runtime.yaml)和
[Memory 策略](../configs/memory-policy.yaml)标记为
**Future Design / Not Active Runtime**，仅作为设计参考，不是当前 Runner 的运行配置。
该标记不承诺未来实现这些组件。

旧接口、事件、Registry 及部署文档中的 Runtime、Memory Manager、Tool Executor
描述应结合其历史契约语境阅读，不表示当前已有对应运行组件。
历史契约与 Schema 保留原义；涉及当前职责时，以本定位及 ADR-0001 为准。
目录或配置中的 `enabled: true` 不构成当前组件已启动的证据。

workspace 目录约定见 [workspace-layout.md](workspace-layout.md)。
