"""CLI entry point for Kai Registry Validator V1.1."""

import argparse
import json
from pathlib import Path
from typing import Any

# PyYAML 是唯一非标准库依赖；自定义 SafeLoader 同时拒绝重复 Key。
import yaml

from .models import Finding, ValidationReport
from .rules import validate_cross_references, validate_registry, validate_schema_instance


VALIDATOR_VERSION = "1.1"
DEFAULT_FILES = {
    "agent": Path("/opt/kai/configs/registry/agent-registry.yaml"),
    "tool": Path("/opt/kai/configs/registry/tool-registry.yaml"),
    "environment": Path("/opt/kai/configs/registry/environment-registry.yaml"),
    "mcp": Path("/opt/kai/configs/mcp-registry.yaml"),
}
# Registry Schema 位于独立命名空间，绝不加载 Core Contract Schema。
DEFAULT_SCHEMAS = {
    "agent": Path("/opt/kai/configs/schema/registry/agent-registry.schema.json"),
    "tool": Path("/opt/kai/configs/schema/registry/tool-registry.schema.json"),
    "environment": Path("/opt/kai/configs/schema/registry/environment-registry.schema.json"),
    "mcp": Path("/opt/kai/configs/schema/registry/mcp-registry.schema.json"),
}


class DuplicateKeyError(yaml.YAMLError):
    """在重复 mapping key 覆盖前终止 YAML 解析。"""


class UniqueKeySafeLoader(yaml.SafeLoader):
    """具有 fail-closed Key 语义的安全加载器。"""


def _construct_unique_mapping(loader: UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    # 必须先构造 key 并检查，再构造对应 value。
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            error = DuplicateKeyError(f"duplicate key: {key}")
            error.problem_mark = key_node.start_mark
            raise error
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def load_yaml(path: Path) -> Any:
    """以 UTF-8 只读解析 Registry，不构造任意 Python 对象。"""
    with path.open("r", encoding="utf-8") as stream:
        return yaml.load(stream, Loader=UniqueKeySafeLoader)


def load_schema(path: Path) -> dict[str, Any]:
    """从隔离目录加载外部 Registry JSON Schema。"""
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("Schema root must be an object")
    return data


def validate_files(files: dict[str, Path] | None = None, schemas: dict[str, Path] | None = None) -> ValidationReport:
    """按 Parse → Schema → Business → Cross 顺序执行且始终返回报告。"""
    report = ValidationReport(validator_version=VALIDATOR_VERSION)
    selected_files = {kind: Path(value) for kind, value in (files or DEFAULT_FILES).items()}
    selected_schemas = {kind: Path(value) for kind, value in (schemas or DEFAULT_SCHEMAS).items()}
    loaded_schemas: dict[str, dict[str, Any]] = {}
    schema_valid_registries: dict[str, Any] = {}

    # Schema 先于 Registry 加载；任何加载异常都转换为报告错误。
    for kind, schema_path in selected_schemas.items():
        report.checked_schema_files.append(str(schema_path))
        try:
            loaded_schemas[kind] = load_schema(schema_path)
        except Exception:
            report.errors.append(Finding("SCHEMA_LOAD_ERROR", "Registry Schema cannot be loaded", str(schema_path)))

    # 每个 Registry 必须先通过 YAML 与 Schema，才允许进入 Business Rules。
    for kind, registry_path in selected_files.items():
        report.checked_files.append(str(registry_path))
        try:
            data = load_yaml(registry_path)
        except DuplicateKeyError as exc:
            report.errors.append(_yaml_finding("YAML_DUPLICATE_KEY", "Duplicate YAML key", registry_path, exc))
            continue
        except FileNotFoundError:
            report.errors.append(Finding("FILE_NOT_FOUND", "Registry file not found", str(registry_path)))
            continue
        except PermissionError:
            report.errors.append(Finding("FILE_PERMISSION", "Registry file is not readable", str(registry_path)))
            continue
        except yaml.YAMLError as exc:
            report.errors.append(_yaml_finding("YAML_PARSE_ERROR", "Invalid YAML", registry_path, exc))
            continue
        except Exception:
            report.errors.append(Finding("YAML_READ_ERROR", "Registry cannot be read or parsed", str(registry_path)))
            continue

        schema = loaded_schemas.get(kind)
        if schema is None:
            continue
        try:
            schema_errors = validate_schema_instance(data, schema, str(registry_path))
        except Exception:
            report.errors.append(Finding("SCHEMA_VALIDATION_ERROR", "Schema validation failed unexpectedly", str(registry_path)))
            continue
        report.errors.extend(schema_errors)
        if schema_errors:
            # P0 安全边界：错误结构不进入业务层，更不能进入跨引用层。
            continue

        try:
            business_errors, warnings = validate_registry(data, kind, str(registry_path))
        except Exception:
            report.errors.append(Finding("BUSINESS_RULE_ERROR", "Business rule validation failed unexpectedly", str(registry_path)))
            continue
        report.errors.extend(business_errors)
        report.warnings.extend(warnings)
        schema_valid_registries[kind] = data

    # Cross Reference 只消费四类全部通过 Schema 和业务阶段的安全结构。
    required_kinds = set(DEFAULT_FILES)
    if required_kinds.issubset(schema_valid_registries):
        try:
            cross_errors, checks = validate_cross_references(
                schema_valid_registries, {kind: str(value) for kind, value in selected_files.items()}
            )
            report.errors.extend(cross_errors)
            report.cross_reference_checks.extend(checks)
        except Exception:
            report.errors.append(Finding("CROSS_REFERENCE_ERROR", "Cross-reference validation failed unexpectedly", "registry-set"))
            report.cross_reference_checks.append({"name": "all", "status": "failed", "checked_references": 0})
    else:
        report.cross_reference_checks.append({"name": "all", "status": "skipped", "checked_references": 0, "reason": "schema_or_business_failure"})
    return report


def _yaml_finding(code: str, message: str, path: Path, exc: yaml.YAMLError) -> Finding:
    """只报告位置，不回显原始 YAML 行，避免敏感内容泄露。"""
    mark = getattr(exc, "problem_mark", None)
    location = f"line {mark.line + 1}, column {mark.column + 1}" if mark else "$"
    return Finding(code, message, str(path), location)


def main() -> int:
    """向 stdout 输出 JSON，并返回 CI/CD 可消费的退出码。"""
    parser = argparse.ArgumentParser(description="Validate Kai Registry V1.1 files")
    parser.add_argument("--indent", type=int, default=2, choices=range(0, 9))
    args = parser.parse_args()
    report = validate_files()
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=args.indent))
    return 0 if report.status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
