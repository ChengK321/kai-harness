"""Kai Registry Validator V1.1 report data models."""

# dataclass 固定报告结构；asdict 只序列化已知的非敏感字段。
from dataclasses import asdict, dataclass, field
from typing import Any


# 单条 Finding 不可变，防止规则返回后被其他阶段意外篡改。
@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    file: str
    path: str = "$"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为 CLI 可直接编码的标准 JSON 对象。"""
        return asdict(self)


# 报告记录配置、Schema 和跨引用检查，便于 CI 审计验证覆盖面。
@dataclass
class ValidationReport:
    validator_version: str = "1.1"
    checked_files: list[str] = field(default_factory=list)
    checked_schema_files: list[str] = field(default_factory=list)
    cross_reference_checks: list[dict[str, Any]] = field(default_factory=list)
    errors: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)

    @property
    def status(self) -> str:
        """warning 不阻断发布；任何 error 都使整体状态失败。"""
        return "passed" if not self.errors else "failed"

    def to_dict(self) -> dict[str, Any]:
        """保持顶层字段顺序稳定，方便调用方解析和报告 diff。"""
        return {
            "validator_version": self.validator_version,
            "status": self.status,
            "checked_files": self.checked_files,
            "checked_schema_files": self.checked_schema_files,
            "cross_reference_checks": self.cross_reference_checks,
            "errors": [item.to_dict() for item in self.errors],
            "warnings": [item.to_dict() for item in self.warnings],
        }
