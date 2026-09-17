"""Focused Contract 1.0 drift guards, not a general JSON Schema evaluator."""

import ast
import copy
import json
import sys
import unittest
from pathlib import Path

from kai_governance_validator import GovernanceValidator
from kai_governance_validator.validator import FIELDS, FORBIDDEN


APP = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((APP.parents[1] / "configs/schema/governance-intent.schema.json").read_text())
BASE = {
    "version": "1.0", "intent_id": "alignment-001",
    "requester": {"type": "human", "id": "user"},
    "environment": {"environment_id": "vps-prod"},
    "target": {"resource": "nginx"}, "purpose": "Restore availability",
    "risk": "LOW", "approval": {"required": False, "reference": None},
    "verification": {"required": True, "evidence_type": "observation"},
}


class SchemaAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.validator = GovernanceValidator()
        self.assertEqual(self.validator.validate(copy.deepcopy(BASE)).status, "allow")

    def test_required_fields_match_and_are_enforced(self):
        expected = {"version", "intent_id", "requester", "environment", "target",
                    "purpose", "risk", "approval", "verification"}
        self.assertEqual(set(SCHEMA["required"]), expected)
        self.assertEqual(set(FIELDS), expected)
        for field in SCHEMA["required"]:
            with self.subTest(field=field):
                intent = copy.deepcopy(BASE)
                del intent[field]
                self.assertEqual(self.validator.validate(intent).status, "deny")

    def test_risk_enum_matches_implementation_and_behavior(self):
        expected = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        self.assertEqual(set(SCHEMA["properties"]["risk"]["enum"]), expected)
        # Freeze the fixed risk membership expression as well as representative behavior.
        # A deliberate implementation rewrite must update this drift guard explicitly.
        tree = ast.parse((APP / "kai_governance_validator/validator.py").read_text())
        enums = [ast.literal_eval(node.comparators[0]) for node in ast.walk(tree)
                 if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name)
                 and node.left.id == "risk" and len(node.ops) == 1
                 and isinstance(node.ops[0], ast.In)]
        self.assertEqual(len(enums), 1)
        self.assertEqual(set(enums[0]), expected)
        for risk in sorted(expected) + ["SAFE", "ADMIN", "UNKNOWN", "low", "", None, 0]:
            with self.subTest(risk=risk):
                intent = copy.deepcopy(BASE)
                intent["risk"] = risk
                intent["approval"]["required"] = True
                report = self.validator.validate(intent)
                self.assertEqual(report.status, "allow" if risk in expected else "deny")

    def test_forbidden_fields_rejected_at_every_object_boundary(self):
        expected = {"command", "shell", "executor", "tool_name", "workflow", "retry",
                    "rollback", "planner", "model_reasoning", "prompt"}
        self.assertEqual(set(FORBIDDEN), expected)
        objects = {None: SCHEMA}
        objects.update({key: value for key, value in SCHEMA["properties"].items()
                        if value.get("type") == "object"})
        for section, definition in objects.items():
            self.assertIs(definition["additionalProperties"], False)
            self.assertNotIn("patternProperties", definition)
            self.assertTrue(expected.isdisjoint(definition["properties"]))
            for field in sorted(expected):
                with self.subTest(section=section, field=field):
                    intent = copy.deepcopy(BASE)
                    target = intent if section is None else intent[section]
                    target[field] = "forbidden"
                    report = self.validator.validate(intent)
                    self.assertEqual(report.status, "deny")
                    self.assertTrue(any(c.name == "executable_fields" and c.status == "failed"
                                        for c in report.checks))

    def test_standard_library_imports_only(self):
        local_modules = {"kai_governance_validator", "test_schema_alignment", "test_negative_corpus", "test_validator"}
        for file in sorted(APP.rglob("*.py")):
            tree = ast.parse(file.read_text())
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    names = [node.module]
                for name in names:
                    with self.subTest(file=str(file), module=name):
                        self.assertIn(name.split(".")[0], sys.stdlib_module_names | local_modules)


if __name__ == "__main__":
    unittest.main()
