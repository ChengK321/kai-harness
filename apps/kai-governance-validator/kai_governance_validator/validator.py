"""Fixed checks for Governance Intent 1.0, using only the standard library."""

import json
from pathlib import Path

from .models import CheckResult, GovernanceDecisionReport


FIELDS = frozenset({"version", "intent_id", "requester", "environment", "target",
                    "purpose", "risk", "approval", "verification"})
FORBIDDEN = frozenset({"tool_name", "command", "shell", "executor", "workflow",
                       "retry", "rollback", "planner", "model_reasoning", "prompt"})


def _text(value: object, limit: int) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def _shape(value: object, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def _executable_fields(value: object) -> bool:
    """Inspect keys, never interpret text values; tolerate cyclic memory input."""
    pending = [value]
    seen = set()
    while pending:
        item = pending.pop()
        if not isinstance(item, (dict, list)) or id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, dict):
            if FORBIDDEN.intersection(item):
                return True
            pending.extend(item.values())
        else:
            pending.extend(item)
    return False


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value):
    raise ValueError("Non-JSON numeric constant")


class GovernanceValidator:
    """Stateless offline validation, not a policy or authorization engine."""

    __slots__ = ()

    def validate(self, intent: object) -> GovernanceDecisionReport:
        if not isinstance(intent, dict):
            return GovernanceDecisionReport("deny", None, (
                CheckResult("required_fields", "failed", "Intent must be a JSON object."),
            ))

        checks = []

        def check(name, passed, failure):
            checks.append(CheckResult(name, "passed" if passed else "failed",
                                      "Satisfied offline check." if passed else failure))

        check("required_fields", FIELDS.issubset(intent), "Missing required top-level fields.")
        check("closed_fields", set(intent).issubset(FIELDS), "Unknown top-level fields.")
        check("executable_fields", not _executable_fields(intent), "Executable or planning fields are forbidden.")
        check("version", intent.get("version") == "1.0", "Unsupported contract version.")
        check("intent_id", _text(intent.get("intent_id"), 128), "Invalid intent_id.")
        requester = intent.get("requester")
        check("requester", _shape(requester, {"type", "id"})
              and requester["type"] in ("human", "service") and _text(requester["id"], 128),
              "Requester must contain a supported type and non-empty id only.")
        environment = intent.get("environment")
        check("environment_binding", _shape(environment, {"environment_id"})
              and _text(environment["environment_id"], 128),
              "Environment must contain non-empty environment_id only; address fields are forbidden.")
        target = intent.get("target")
        check("target", _shape(target, {"resource"}) and _text(target["resource"], 256),
              "Target must contain non-empty resource only.")
        check("purpose", _text(intent.get("purpose"), 1024), "Invalid user goal summary.")
        risk = intent.get("risk")
        check("risk", risk in ("LOW", "MEDIUM", "HIGH", "CRITICAL"), "Unknown risk value.")
        approval = intent.get("approval")
        check("approval", _shape(approval, {"required", "reference"})
              and type(approval["required"]) is bool
              and (approval["reference"] is None or _text(approval["reference"], 128))
              and (risk not in ("HIGH", "CRITICAL") or approval["required"] is True),
              "Invalid approval declaration; HIGH/CRITICAL must declare approval required.")
        verification = intent.get("verification")
        check("verification", _shape(verification, {"required", "evidence_type"})
              and type(verification["required"]) is bool
              and verification["evidence_type"] == "observation",
              "Verification must declare a boolean required and observation evidence_type only.")
        identifier = intent.get("intent_id")
        return GovernanceDecisionReport(
            "allow" if all(item.status == "passed" for item in checks) else "deny",
            identifier if _text(identifier, 128) else None,
            tuple(checks),
        )

    def validate_file(self, path: str | Path) -> GovernanceDecisionReport:
        """Read a caller-selected local JSON file, never follow intent references."""
        try:
            with Path(path).open("r", encoding="utf-8") as stream:
                intent = json.load(stream, object_pairs_hook=_unique_object,
                                   parse_constant=_invalid_constant)
        except (OSError, ValueError, RecursionError):
            return GovernanceDecisionReport("deny", None, (
                CheckResult("input_json", "failed", "Cannot read a valid local JSON intent."),
            ))
        return self.validate(intent)
