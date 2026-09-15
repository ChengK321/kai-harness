# Kai Observation Provider — V0.7-D4

Kai 是 Agent Control Plane。此模块只定义只读 `ObservationProvider` 接口及
`VPSObserverProvider` 适配，不实现 Agent Runtime、Tool Executor、Policy Engine、
自动修复或环境控制，也不修改当前 Claude Harness。

## 接口与数据流

```text
get_observation(environment_id)
  → VPSObserver().collect(environment_id)
  → RawObservation.to_observation()
  → Observation Contract V1.0 dict
```

Provider 每次创建 Adapter，不缓存采集结果、不保存实例状态、不写文件、
不执行命令、不访问网络。底层 Adapter 仅读取本机状态，不使用 SSH、Docker 或 ROS2。
environment_id 原样传递，是本机逻辑标签，不是远程地址或访问授权。

使用前通过启动环境使两个本地包可导入，无需安装第三方依赖：

```bash
export PYTHONPATH=/opt/kai/apps/kai-observation:/opt/kai/apps/vps-observer
```

授权本机观察时可调用：

```python
from kai_observation import ObservationProvider, VPSObserverProvider

provider: ObservationProvider = VPSObserverProvider()
observation = provider.get_observation("local-vps")
```

成功返回 [Observation 1.0](../../configs/schema/observation.schema.json)，
主机诊断字段保留在 Adapter Raw Model 中，不添加到公开输出。
Adapter 已捕获的采集错误继续通过 `metadata.errors` 与 `collection_status` 返回；
意外的构造、采集或转换异常统一转为 `ObservationProviderError`，使用固定脱敏消息。
无效 environment_id 在采集前抛出 `ValueError`；KeyboardInterrupt/SystemExit 不被吞掉。
不重试、不修复、不伪造成功结果。

## 测试

```bash
cd /opt/kai/apps/kai-observation
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:../vps-observer python3 -m unittest discover -s tests -v
```

测试用真实 Raw Model 和 mock Adapter 验证契约输出、参数传递、异常及副作用边界，
不采集真实环境。Schema 检查针对输出使用的契约字段，不引入完整 JSON Schema 引擎。

## 兼容性与限制

这是供未来控制面调用的接口，不向当前 Harness 自动注入 Observation，也不改变
Runner、CLI 或 HarnessResult。Provider 信任内置 Adapter 的转换，未提供任意第三方
输出的运行时 Schema 校验或 OS 沙箱。环境身份绑定、权限隔离和可信接入仍由部署及
未来控制面负责。调用同步执行，采样时间由 Adapter 控制；不引入调度器或工作流。
