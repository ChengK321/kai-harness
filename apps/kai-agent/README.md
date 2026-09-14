# Kai Thin Harness Runner — V0.6-D1

执行链路：**Kai → Claude Code Harness → Model Provider**。
Claude Code 提供成熟的 Agent Harness，DeepSeek 是当前模型 Provider。
Kai 只做薄 Control/Application Layer：校验 workspace、启动 CLI、解析结果。
这不是新的 Agent Runtime，不实现 Planner、Tool Executor、Context Manager、
Provider Framework、Memory、Registry 或状态机。

仅使用 Python 3.12 标准库，无需安装 Python 第三方依赖。
运行前需在 PATH 中安装并配置好 `claude`，由启动进程注入模型环境变量。
Runner 不读取 API Key 文件（包括 `~/.config/kai/deepseek.env`），
不加载 dotenv，也不覆盖子进程环境。

## 运行

先由环境管理员准备 `/srv/kai/workspaces/sandbox`，然后执行：

```bash
cd /opt/kai/apps/kai-agent
python3 -m kai_agent.cli \
  --workspace /srv/kai/workspaces/sandbox \
  "检查当前目录并告诉我有哪些文件"
```

workspace 必须是绝对路径、存在且是目录；解析符号链接后必须严格位于
`/srv/kai/workspaces` 之下（根目录本身不接受）。
固定启用 `Read,Glob,Grep`，不开放 `Edit,Write,Bash`；最大轮数 5，
JSON 输出，不持久化会话。CLI 参数数组以 `--` 分隔 prompt，
使用 `shell=False`，以解析后的 workspace 为 cwd，默认超时 300 秒。
这是 Claude Code 工具集限制；workspace 校验不是操作系统级文件访问沙箱。

成功返回 `HarnessResult`，包含执行状态、退出码、结果文本、会话 ID、轮数、
耗时、费用、权限拒绝记录和 stderr。workspace 错误抛出 `WorkspaceError`；
启动失败、超时、非零退出或无效 JSON 抛出 `HarnessExecutionError`。
Claude 报告的业务失败保留在 `success=False` 的结果中。
CLI 将失败显示为清晰错误，并返回非零退出码。

## 测试

```bash
cd /opt/kai/apps/kai-agent
python3 -m unittest discover -s tests -v
```

测试使用临时目录与 `unittest.mock`，不执行 Claude，也不请求 DeepSeek。
