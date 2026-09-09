"""Schema、业务规则与跨 Registry 引用规则。"""

from typing import Any

from .models import Finding


# 权限值严格对应 Core Contract；未知值由 Schema 层 fail closed。
REGISTRIES = {
    "agent": ("agents", "id"),
    "tool": ("tools", "id"),
    "environment": ("environments", "id"),
    "mcp": ("servers", "server_id"),
}


def _error(code: str, message: str, file: str, path: str) -> Finding:
    """统一构造不包含原始配置内容的错误。"""
    return Finding(code=code, message=message, file=file, path=path)


# 轻量引擎实现本项目 Registry Schema 实际使用的关键字。
# Schema 保持 Draft 2020-12 格式，未来可替换为完整实现。
def validate_schema_instance(instance: Any, schema: dict[str, Any], file: str, path: str = "$") -> list[Finding]:
    errors: list[Finding] = []
    expected = schema.get("type")
    if expected is not None and not _matches_type(instance, expected):
        return [_error("SCHEMA_TYPE", f"Expected type {expected}", file, path)]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(_error("SCHEMA_ENUM", "Value is outside the allowed enum", file, path))
    if "const" in schema and instance != schema["const"]:
        errors.append(_error("SCHEMA_CONST", "Value does not match the required constant", file, path))

    # 对象递归检查 required 和 properties；Registry Schema 保留未来扩展字段。
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(_error("SCHEMA_REQUIRED", f"Missing required field: {key}", file, f"{path}.{key}"))
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_schema_instance(value, properties[key], file, f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(_error("SCHEMA_ADDITIONAL_PROPERTY", f"Unexpected field: {key}", file, f"{path}.{key}"))
    elif isinstance(instance, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                errors.extend(validate_schema_instance(value, item_schema, file, f"{path}[{index}]"))
        if schema.get("uniqueItems") and len({repr(item) for item in instance}) != len(instance):
            errors.append(_error("SCHEMA_UNIQUE_ITEMS", "Array items must be unique", file, path))
    elif isinstance(instance, str) and len(instance) < schema.get("minLength", 0):
        errors.append(_error("SCHEMA_MIN_LENGTH", "String is shorter than minLength", file, path))
    elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(_error("SCHEMA_MINIMUM", "Number is below minimum", file, path))
    return errors


def _matches_type(value: Any, expected: str | list[str]) -> bool:
    """匹配 JSON 类型，并避免把 Python bool 当作 integer。"""
    names = [expected] if isinstance(expected, str) else expected
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return any(name in checks and checks[name](value) for name in names)


# 业务层不读取 Registry 内部 entry_schema；结构由外部 Schema 唯一决定。
def validate_registry(data: Any, kind: str, file: str) -> tuple[list[Finding], list[Finding]]:
    errors: list[Finding] = []
    warnings: list[Finding] = []
    if kind not in REGISTRIES or not isinstance(data, dict):
        return errors, warnings
    list_key, id_key = REGISTRIES[kind]
    entries = data.get(list_key, [])
    if not isinstance(entries, list):
        return errors, warnings

    # ID 是跨组件引用身份，因此唯一性属于独立业务不变量。
    seen: set[Any] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        base = f"$.{list_key}[{index}]"
        item_id = entry.get(id_key)
        if item_id is not None and item_id in seen:
            errors.append(_error("DUPLICATE_ID", f"Duplicate {id_key}: {item_id}", file, f"{base}.{id_key}"))
        seen.add(item_id)
        # Schema 检查字段枚举；业务层补充高风险审批约束。
        if kind == "tool":
            high_risk = entry.get("permission_level") == "ADMIN" or entry.get("side_effect") == "irreversible"
            if high_risk and entry.get("requires_approval") is not True:
                errors.append(_error("HIGH_RISK_APPROVAL", "High-risk tool must require approval", file, f"{base}.requires_approval"))
    errors.extend(_validate_default_deny(data, kind, file))
    return errors, warnings


def _validate_default_deny(data: dict[str, Any], kind: str, file: str) -> list[Finding]:
    """逐类确保省略配置不会开放执行权限。"""
    findings: list[Finding] = []
    if data.get("default_action") != "deny":
        findings.append(_error("DEFAULT_DENY", "default_action must be deny", file, "$.default_action"))
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        return findings
    if kind == "agent":
        if defaults.get("status") != "disabled":
            findings.append(_error("DEFAULT_AGENT_ENABLED", "Agent default status must be disabled", file, "$.defaults.status"))
        access = defaults.get("tool_access", {})
        if not isinstance(access, dict) or access.get("allow") or "*" not in access.get("deny", []):
            findings.append(_error("DEFAULT_TOOL_ACCESS", "Agent default tool access must deny all", file, "$.defaults.tool_access"))
    elif kind in {"tool", "mcp"} and defaults.get("enabled") is not False:
        findings.append(_error("DEFAULT_ENABLED", f"{kind} defaults.enabled must be false", file, "$.defaults.enabled"))
    elif kind == "environment":
        for index, entry in enumerate(data.get("environments", [])):
            policy = entry.get("safety_policy", {}) if isinstance(entry, dict) else {}
            if policy.get("default_action") != "deny" or policy.get("execution_enabled") is not False:
                findings.append(_error("DEFAULT_ENVIRONMENT_EXECUTION", "Environment execution must default to deny and disabled", file, f"$.environments[{index}].safety_policy"))
    return findings


# 只验证显式 allow、execution_scope 和 MCP tools；deny 通配符不是引用。
def validate_cross_references(registries: dict[str, Any], files: dict[str, str]) -> tuple[list[Finding], list[dict[str, Any]]]:
    errors: list[Finding] = []
    counts = {"agent_tool_reference": 0, "agent_environment_reference": 0, "mcp_tool_reference": 0}
    tool_ids = _ids(registries.get("tool"), "tools", "id")
    environment_ids = _ids(registries.get("environment"), "environments", "id")
    for index, agent in enumerate(_entries(registries.get("agent"), "agents")):
        # 防御式读取即使被独立调用也不对错误嵌套类型调用 .get()。
        for tool_id in _nested_list(agent, "tool_access", "allow"):
            counts["agent_tool_reference"] += 1
            if tool_id not in tool_ids:
                errors.append(_error("CROSS_AGENT_TOOL_NOT_FOUND", f"Agent references unknown tool: {tool_id}", files["agent"], f"$.agents[{index}].tool_access.allow"))
        for environment_id in _nested_list(agent, "execution_scope", "environments"):
            counts["agent_environment_reference"] += 1
            if environment_id not in environment_ids:
                errors.append(_error("CROSS_AGENT_ENVIRONMENT_NOT_FOUND", f"Agent references unknown environment: {environment_id}", files["agent"], f"$.agents[{index}].execution_scope.environments"))
    for index, server in enumerate(_entries(registries.get("mcp"), "servers")):
        tools = server.get("tools", [])
        for tool_id in tools if isinstance(tools, list) else []:
            counts["mcp_tool_reference"] += 1
            if tool_id not in tool_ids:
                errors.append(_error("CROSS_MCP_TOOL_NOT_FOUND", f"MCP Server references unknown tool: {tool_id}", files["mcp"], f"$.servers[{index}].tools"))
    codes = {item.code for item in errors}
    code_by_name = {"agent_tool_reference": "CROSS_AGENT_TOOL_NOT_FOUND", "agent_environment_reference": "CROSS_AGENT_ENVIRONMENT_NOT_FOUND", "mcp_tool_reference": "CROSS_MCP_TOOL_NOT_FOUND"}
    checks = [{"name": name, "status": "failed" if code_by_name[name] in codes else "passed", "checked_references": count} for name, count in counts.items()]
    return errors, checks


def _nested_list(entry: dict[str, Any], object_key: str, list_key: str) -> list[Any]:
    """安全读取跨引用数组；错误类型返回空列表而不是抛出异常。"""
    nested = entry.get(object_key, {})
    if not isinstance(nested, dict):
        return []
    values = nested.get(list_key, [])
    return values if isinstance(values, list) else []


def _entries(data: Any, list_key: str) -> list[dict[str, Any]]:
    """Schema 失败后仍防御式读取，避免产生二次异常。"""
    if not isinstance(data, dict) or not isinstance(data.get(list_key), list):
        return []
    return [item for item in data[list_key] if isinstance(item, dict)]


def _ids(data: Any, list_key: str, id_key: str) -> set[Any]:
    """提取已声明 ID，供跨 Registry 引用解析。"""
    return {item[id_key] for item in _entries(data, list_key) if id_key in item}
