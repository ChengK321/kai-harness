# Kai AI Agent Infrastructure V1.0 架构

## 目标

Kai V1.0 提供可审计、可扩展、可回滚的 Agent 基础设施。核心调用链如下：

`User Interface → Agent Gateway → Agent Runtime → Memory Manager → Tool Executor → MCP Interface → Environment`

## 分层职责

1. **User Interface**：接收用户输入并展示响应、审批请求和运行状态；不直接访问工具或运行环境。
2. **Agent Gateway**：负责身份识别、请求校验、会话路由、限流和关联 ID 注入，是外部请求的统一入口。
3. **Agent Runtime**：执行 Agent 推理与任务编排，维护运行状态、超时和取消语义，并根据策略请求记忆或工具能力。
4. **Memory Manager**：统一管理五层 Memory 的读写、检索、保留期、隔离和脱敏，不向模型暴露未经授权的数据。
5. **Tool Executor**：按白名单、参数约束和审批策略执行工具；实施超时、资源限制、结果截断和审计。
6. **MCP Interface**：以标准接口注册和调用 MCP 服务，校验服务身份、能力、健康状态及访问范围。
7. **Environment**：承载文件系统、容器、网络、外部 API 和系统资源；默认最小权限并与运行时隔离。

## 横切能力

- 配置：版本化 YAML 配置，环境差异通过覆盖层或环境变量注入。
- 可观测性：结构化日志、指标、追踪和贯穿全链路的 correlation ID。
- 安全：默认拒绝、最小权限、人工审批、敏感信息脱敏和不可抵赖审计。
- 可靠性：健康检查、超时、重试上限、幂等键、熔断与降级。
- 扩展：组件通过稳定契约交互；新增工具、MCP 服务和 Memory 后端不改变核心调用链。

## 典型请求流程

Gateway 验证请求并创建关联 ID；Runtime 制定执行步骤；Memory Manager 按策略提供上下文；Tool Executor 校验工具和参数；需要外部能力时经 MCP Interface 访问 Environment；结果经脱敏、记录和格式化后返回用户。

## 边界约束

V1.0 不允许 UI 绕过 Gateway，不允许 Runtime 直接读写持久化 Memory，不允许工具绕过 Tool Executor 或 MCP Interface。所有跨边界调用都必须可鉴权、可超时、可追踪、可审计。
