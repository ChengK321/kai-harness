# Kai Registry Snapshot V1.0

## 1. Snapshot 作用

Registry Snapshot 是某一时刻经过 Validator 验证的不可变 Registry 集合。它把 Agent、Tool、Environment、MCP Registry 与对应 Schema 固定为可追溯发布单元，使 Runtime 不受配置文件随后变化影响，并为审计、复现和回滚提供稳定依据。Snapshot 只做设计，本阶段不生成制品、不签名、不连接环境。

## 2. 包含内容

每个 Snapshot 清单至少包含：

- `registry_version`：四类 Registry 的逻辑版本及文件级版本映射。
- `schema_version`：所使用 Registry Schema 的版本与文件映射；不得引用 Core Contract Interface Schema。
- `validator_version`：创建 Snapshot 前通过验证的 Validator 版本，V1.1 起为 `1.1`。
- `timestamp`：UTC RFC 3339 创建时间，由发布流程生成。
- `sha256`：对规范化清单及纳入文件计算的 SHA-256 摘要；必须明确规范化与文件排序规则。

建议同时记录 snapshot ID、源版本、文件列表、每个文件摘要、验证报告摘要及创建主体。时间戳不参与权限判定，摘要用于完整性检查但不能替代身份签名。

## 3. 任务如何绑定 Snapshot

Gateway 接纳任务后，Runtime 选择一个已发布且有效的 snapshot ID，并把 ID 与摘要写入任务状态、事件和审计记录。任务的 Agent 识别、Tool 选择、Environment scope 与 MCP 引用均基于该固定 Snapshot。普通 Registry 发布只影响新任务；运行中任务不得静默切换。

安全紧急撤销可以覆盖固定 Snapshot，但必须通过独立 deny/revocation 通道，产生审计事件，并使受影响任务进入 `paused`、`waiting_human` 或安全终态。

## 4. 回滚策略

发布流程保留上一份已验证 Snapshot。新 Snapshot 校验、完整性检查或运行验收失败时，将新任务绑定点原子切回上一版本；已绑定旧版本的运行中任务维持原引用。回滚不得恢复已被紧急撤销的能力。

回滚记录包含操作者、原因、来源和目标 snapshot ID、摘要、时间及验证报告。任何文件摘要不匹配都必须 fail closed，而不是尝试局部混用版本。

## 5. 未来签名机制

未来可对规范化 Snapshot manifest 签名，并保存签名算法、key ID、签发主体、签发时间和验证状态。签名材料与验证信任根由受控系统管理，不进入普通 Registry。Runtime 加载前验证摘要、签名、有效期和撤销状态。

签名方案应支持密钥轮换、多签审批和离线验证。SHA-256 只证明内容一致性；只有经过可信身份验证的数字签名才能证明发布来源。
