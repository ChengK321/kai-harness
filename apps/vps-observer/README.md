# VPS Observation Adapter Prototype — V0.7-D3

Kai 是 Agent Control Plane。本模块仅观察本机 Linux 状态，不实现 Agent Runtime、
Tool Executor、Policy Engine、自动修复或服务管理。仅使用 Python 标准库。

## Raw 与 Contract 分离

`VPSObserver().collect(environment_id)` 返回 `RawObservation`：

```text
environment_id, timestamp
hostname, os, kernel       # 仅本地诊断，不进入跨环境契约
cpu                       # 使用率百分比
memory, disk              # Capacity(total_bytes, used_bytes)，提供 percent
resources                 # 派生 cpu_percent / memory_percent / disk_percent
errors                    # 脱敏采集错误
```

`raw.to_observation()` 转换为 Observation Contract 1.0。Adapter 实现可以变化，
但跨 Environment Observation Contract 必须稳定。因此 hostname/os/kernel、resources
和顶层 errors 不进入输出；CPU 映射到 `system.cpu.usage_percent`，内存和磁盘映射为
字节量，错误统一进入 `metadata.errors`。未采集字段省略，不用零假装成功。
转换面向本采集器生成的 Raw 对象，不是任意外部数据的校验器。

## 采集范围与安全

- hostname、os、kernel 使用 `os.uname()`；os 表示内核系统名，不是发行版名称。
- CPU 读取两次 `/proc/stat`，默认间隔 0.1 秒；汇总全部 CPU，idle 包含 iowait，
  guest 时间不重复计入。间隔允许 0–1 秒之间的正值。
- 内存读取 `/proc/meminfo`，used = MemTotal - MemAvailable；不支持时记录错误。
- 磁盘读取 `shutil.disk_usage('/')`，范围仅根文件系统，不汇总所有挂载点。
- services 仅保留 `ServiceObserver` Protocol，不实现、不调用、不输出伪造服务状态。

不使用 subprocess、shell、Docker、网络或 SSH，不写文件、不重启服务、不修改配置。
environment_id 仅是本机逻辑标签，不能指定远端目标。错误文本固定且脱敏。
`complete` 仅表示这六项本地采集成功，不表示服务或整个环境健康。
部分失败返回 partial，全部失败返回 failed；不触发重试或修复。

## 使用与验证

未来授权本机采集时可在 Python 中使用（本模块无自动运行入口）：

```python
from vps_observer import VPSObserver

raw = VPSObserver().collect("local-vps")
observation = raw.to_observation()
```

测试全部使用 mock，不观察真实 VPS：

```bash
cd /opt/kai/apps/vps-observer
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

测试读取原始 Observation Schema，核对生成输出涉及的类型、必填字段、封闭字段、
枚举、数值范围和时间格式；使用标准库针对性断言，不宣称提供完整 Draft 2020-12 校验器。

## 限制

此原型针对 Linux；容器内看到的 /proc 与文件系统范围可能不同，不保证 cgroup 配额视图。
采样不是原子快照，environment_id 未绑定 Registry，Raw 主机信息不应直接注入 Agent 上下文。
只读实现不是 OS 沙箱。未接入 Claude Harness、Registry Validator 或任何真实环境服务。
