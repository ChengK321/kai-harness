# Kai 测试 workspace 目录规范

工作目录统一位于 `/srv/kai/workspaces`，约定布局如下：

```text
/srv/kai/workspaces/
├── sandbox/
├── projects/
└── snapshots/
```

| 目录 | 用途 |
| --- | --- |
| `sandbox/` | 最小 Runner 验证与临时测试材料，避免混入正式项目数据。 |
| `projects/` | 项目工作目录，每个项目使用独立子目录，例如 `projects/example/`。 |
| `snapshots/` | 保存用于复现测试的 workspace 文件副本，按项目和版本或时间建立子目录；不是 Registry Snapshot。 |

当前 Runner 仅允许绝对路径、实际存在的目录；经 `resolve()` 解析后必须严格位于
`/srv/kai/workspaces` 之下。根目录本身、路径穿越到根外或符号链接逃逸均不接受。
例如 `/srv/kai/workspaces/sandbox` 和 `/srv/kai/workspaces/projects/example`
符合目录边界要求，`/etc` 不符合。

目录由运维人员或未来 Control Plane 显式准备；Runner 不创建目录、复制项目、
生成快照或清理文件。本规范不创建或修改 `/srv` 下的实际目录。

当前 Agent 工具固定为 `Read,Glob,Grep`。workspace 路径校验控制启动目录，
不是操作系统级文件访问沙箱；`snapshots/` 名称本身也不提供不可变或只读保证。
目录布局不构成持久化 Agent Memory 的实现。
