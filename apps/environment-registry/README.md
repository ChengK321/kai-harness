# Environment Registry Prototype

V0.9-D1 Minimal Prototype

当前阶段仅定义 Registry 边界，不提供服务。

## Goal

验证：

- environment 是否可以被唯一识别
- capability 是否可以被声明和查询
- registry 是否保持薄控制面定位

## Data Flow

```
Environment
     |
     v
Registry Record
     |
     v
Capability Reference
     |
     v
Observation Provider / Governance Layer
```

Registry 的作用是提供环境身份和能力声明参考，不参与环境操作。

## Responsibility Boundary

Registry owns:

- environment identity
- environment type
- trust classification
- capability declaration

Registry does not own:

- authentication
- secrets
- execution
- deployment
- observation collection
- workflow scheduling

## Example

```
environment_id: vps-prod-001
capabilities:
  - observation.cpu
  - observation.service_status
```

Capability 声明不是执行授权，也不会自动赋予 Agent 操作权限。

## Non Goals

不实现：

- database
- REST API
- authentication
- deployment
- executor
- secret management
- workflow
