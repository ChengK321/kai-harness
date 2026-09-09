# Kai V1.0 Memory 设计

## 设计原则

Memory Manager 是唯一读写入口。所有记录必须带作用域、来源、时间、版本、敏感级别和保留策略；写入前进行授权与脱敏，读取时执行最小披露。用户可查看、更正和删除其可管理数据。

## 五层 Memory

1. **Working Memory**：单次任务或短会话的临时上下文、计划和中间结果。容量受限、生命周期最短，任务结束后按策略清理。
2. **Episodic Memory**：按时间组织的交互事件与任务结果。用于回顾历史经历，写入前摘要化并去除无关敏感内容。
3. **Semantic Memory**：从可靠材料中形成的事实、概念和知识索引。必须保留来源、置信度、更新时间和失效条件，支持重新索引。
4. **User Memory**：用户明确提供或允许保存的偏好、长期目标和个人上下文。按用户强隔离，要求可解释、可导出、可撤回。
5. **System Memory**：系统策略、能力说明、运行约束和运维知识。仅授权管理员发布，版本化且优先级高于其他记忆层。

## 检索与冲突

检索同时考虑作用域、权限、相关性、新鲜度和可信度。冲突时，系统策略优先；事实信息优先采用来源更可靠且更新的记录；用户偏好仅在对应用户作用域生效。无法可靠消解时向调用方标记冲突，不静默合并。

## Memory Provenance

所有 Memory 记录必须增加可审计来源信息：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `source_type` | enum | `user_input`、`agent_inference` 或 `system_generated` |
| `source_id` | string | 原始消息、任务、事件、文档、部署或配置变更的稳定引用 |
| `created_by` | string | 经认证的用户、Agent Adapter、Runtime 或系统组件主体标识 |
| `confidence` | number | 0 到 1；表示内容正确性的置信度，不等于授权等级 |
| `verified` | boolean | 是否由允许的验证流程确认；Agent 不得自行把推理标记为 true |

- 用户明确输入使用 `source_type=user_input`，指向已授权消息；可视为用户陈述，但不自动视为客观事实。用户对其偏好和意图具有确认权。
- Agent 推理结果使用 `source_type=agent_inference`，必须关联任务及 Adapter，默认 `verified=false`，并与原始证据引用分开保存。
- 系统产生记录使用 `source_type=system_generated`，必须关联事件、部署、配置或监控来源；仅受信系统流程可标记为已验证。

来源字段不可在普通内容更新时静默改写。验证、纠正或派生操作应生成新 revision，保留来源链和审计 ID。缺少必要 provenance 的记录必须拒绝持久化或隔离待补全。

### 旧 `source` 字段迁移

旧版记录中的 `source` 不再是新契约字段。迁移时只允许将其原值映射为 `source_id`，并依据可信历史上下文补齐 `source_type`、`created_by`、`confidence` 和 `verified`：用户消息映射为 `user_input`，Agent 任务产物映射为 `agent_inference`，受信事件、部署或配置记录映射为 `system_generated`。

迁移不得仅凭字符串格式猜测来源类别，不得自动把记录标为已验证，也不得伪造创建主体。历史消息、任务、事件或审计记录不足以确定必填字段时，记录必须进入隔离区等待人工或受信流程确认。迁移成功后生成新 revision、记录迁移审计 ID，并删除对旧 `source` 字段的读取依赖；新记录与新接口一律禁止写入旧字段。

## Memory Priority and Conflict Resolution

默认优先级为：

`System Memory > User Memory > Semantic Memory > Episodic Memory > Working Memory`

该顺序表示同一作用域、同一主题且均有权参与决策时的默认约束优先级；它不允许高层记录越过授权边界，也不表示 System Memory 中的陈旧事实永远正确。

冲突决策顺序：

1. **权限与作用域**：先剔除无权读取、已撤销同意或不属于当前用户/租户的记录。
2. **层级优先级**：系统政策优先于用户偏好；用户明确偏好优先于一般知识和历史经验；Working Memory 不得改写长期事实。
3. **来源可靠性**：优先 `verified=true`、可追溯到权威来源且来源链完整的记录；用户陈述只对其偏好、意图和授权具有特殊权威性。
4. **时间与有效期**：权限和可靠性相当时使用较新且未过期的记录；政策与文档还必须匹配适用版本。
5. **用户确认**：涉及用户偏好、身份归属、重大副作用或仍无法消解时，进入 `waiting_human`；确认结果可形成新 User Memory，但不能覆盖 System Memory 的安全约束。

Memory Manager 必须返回候选记录引用、采用或拒绝原因与置信度，不得静默合并相互排斥的值。Agent 可以提出建议，但最终筛选、优先级执行和审计由 Memory Manager 与 Policy Engine 负责。

## 生命周期

数据经历采集、校验、分类、存储、检索、更新、归档和删除。每层独立设置容量、TTL、压缩、备份和删除规则；删除请求应覆盖主存、索引及到期备份，并留下不含原文的审计证明。

## 扩展接口

后端通过稳定的 `put/get/search/update/delete` 契约接入，并支持命名空间、元数据过滤、分页、幂等和迁移版本。向量索引只是检索实现，不作为事实来源；未来更换存储后端不改变上层权限语义。
