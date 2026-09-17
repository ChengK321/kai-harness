# Offline Governance Validator — V0.8-D3

仅使用 Python 标准库。独立、无状态的离线验证组件，不是 Runtime、Policy Engine、
Authorization System 或 Executor。不调用 Tool/MCP，不读取 Registry 或 Environment。

```python
from kai_governance_validator import GovernanceValidator

validator = GovernanceValidator()
report = validator.validate(intent).to_dict()  # 已解析的内存 JSON 对象
# 或 validator.validate_file("intent.json").to_dict()，仅读取指定本地文件
```

输出包含 `status`（严格为 `allow` / `deny`）、`intent_id` 和
`checks`（每项 name/status/reason，状态为 passed/failed）。不使用 denied/ALLOW 等其他拼写。
未能识别有效 intent_id 时返回 null。文件不可读、JSON 非法、重复键或非法数值常量均返回 deny。
不回显异常原文或被拒绝的字段值。

固定检查对应 Governance Intent 1.0：顶层必填及封闭字段、版本、字符串长度/非空、
requester 结构、environment_id、目标和目的、风险枚举、审批结构、高风险审批声明、
验证结构；递归拒绝执行/规划字段。不是通用 JSON Schema 引擎，不加载策略或规则 DSL。
契约变更时须显式更新代码和测试，不会自动支持未来 Schema。

`allow` 仅表示通过离线检查，不代表 authorized execution、successful execution 或
environment safety。LOW + required=false 合法；HIGH + required=true + reference=null
也可结构合法，但仍待审批，绝不是自动批准。verification.required=false 可结构合法。

不验证真实身份、Registry 成员、风险真实性、审批有效性或证据质量。
environment 只接受 environment_id，拒绝 host/hostname/ip/ssh 属性；不解析标识，
因此不能判定一个字符串究竟是 Registry ID 还是伪装地址。这需要未来可信治理核验。
文本值不作为命令解释，也不宣称能识别自然语言中的执行意图。
文件入口仅用于调用方选择的本地 JSON 文件，不作为任意不可信路径的沙箱。

测试（不执行真实动作）：

```bash
cd /opt/kai/apps/kai-governance-validator
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

设计见 [governance-validator-design.md](../../docs/governance-validator-design.md)。
