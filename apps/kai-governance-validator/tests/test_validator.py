import copy
import json
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from kai_governance_validator import GovernanceValidator


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = GovernanceValidator()
        self.intent = {
            "version": "1.0", "intent_id": "intent-001",
            "requester": {"type": "human", "id": "user-001"},
            "environment": {"environment_id": "vps-primary"},
            "target": {"resource": "service/nginx"},
            "purpose": "Restore website availability", "risk": "MEDIUM",
            "approval": {"required": True, "reference": "approval-001"},
            "verification": {"required": True, "evidence_type": "observation"},
        }

    def test_valid_intent(self):
        report = self.validator.validate(self.intent).to_dict()
        self.assertEqual(report["validation"], "passed")
        self.assertEqual(report["intent_id"], "intent-001")
        self.assertTrue(all(c["status"] == "passed" for c in report["checks"]))
        self.assertNotIn("approved", report)
        self.assertNotIn("execute", report)
        json.dumps(report, allow_nan=False)

    def test_missing_environment(self):
        del self.intent["environment"]
        report = self.validator.validate(self.intent)
        self.assertEqual(report.validation, "failed")
        self.assertTrue(any(c.name == "environment_binding" and c.status == "failed" for c in report.checks))

    def test_missing_approval(self):
        del self.intent["approval"]
        self.assertEqual(self.validator.validate(self.intent).validation, "failed")

    def test_all_required_fields(self):
        schema = json.loads((Path(__file__).resolve().parents[3] /
                             "configs/schema/governance-intent.schema.json").read_text())
        self.assertEqual(set(self.intent), set(schema["required"]))
        for key in schema["required"]:
            with self.subTest(key=key):
                value = copy.deepcopy(self.intent)
                del value[key]
                self.assertEqual(self.validator.validate(value).validation, "failed")

    def test_command_rejected(self):
        self.intent["command"] = "systemctl restart nginx"
        self.assertEqual(self.validator.validate(self.intent).validation, "failed")

    def test_tool_name_rejected(self):
        self.intent["tool_name"] = "restart_service"
        self.assertEqual(self.validator.validate(self.intent).validation, "failed")

    def test_model_reasoning_rejected(self):
        self.intent["model_reasoning"] = "private"
        self.assertEqual(self.validator.validate(self.intent).validation, "failed")

    def test_nested_forbidden_fields(self):
        for key in ("command", "tool_name", "shell", "executor", "workflow", "retry",
                    "rollback", "planner", "model_reasoning", "prompt"):
            with self.subTest(key=key):
                value = copy.deepcopy(self.intent)
                value["target"][key] = "forbidden"
                report = self.validator.validate(value)
                self.assertEqual(report.validation, "failed")
                self.assertTrue(any(c.name == "executable_fields" and c.status == "failed" for c in report.checks))

    def test_invalid_risk(self):
        for risk in ("SAFE", None, [], {}, 3):
            self.intent["risk"] = risk
            self.assertEqual(self.validator.validate(self.intent).validation, "failed")

    def test_low_risk_without_manual_approval(self):
        self.intent["risk"] = "LOW"
        self.intent["approval"] = {"required": False, "reference": None}
        self.assertEqual(self.validator.validate(self.intent).validation, "passed")

    def test_high_risk_requires_approval_declaration(self):
        for risk in ("HIGH", "CRITICAL"):
            self.intent["risk"] = risk
            self.intent["approval"] = {"required": False, "reference": None}
            self.assertEqual(self.validator.validate(self.intent).validation, "failed")
            self.intent["approval"]["required"] = True
            self.assertEqual(self.validator.validate(self.intent).validation, "passed")

    def test_validation_is_not_authorization(self):
        report = self.validator.validate(self.intent).to_dict()
        self.assertEqual(report["validation"], "passed")
        self.assertNotIn("authorization", report)
        self.assertNotIn("execution", report)

    def test_address_fields_rejected(self):
        for key in ("host", "hostname", "ip", "ssh"):
            value = copy.deepcopy(self.intent)
            value["environment"][key] = "1.2.3.4"
            self.assertEqual(self.validator.validate(value).validation, "failed")

    def test_closed_shapes_and_types(self):
        changes = [
            ("version", "2.0"), ("intent_id", " "), ("intent_id", "a" * 129),
            ("purpose", ""), ("purpose", "a" * 1025),
            ("requester", {"type": "model", "id": "x"}),
            ("target", {"resource": "x", "extra": 1}),
            ("approval", {"required": "false", "reference": None}),
            ("approval", {"required": False, "reference": ""}),
            ("verification", {}), ("verification", {"required": True}),
            ("verification", {"required": 1, "evidence_type": "observation"}),
            ("verification", {"required": True, "evidence_type": "shell"}),
        ]
        for key, replacement in changes:
            with self.subTest(key=key, replacement=replacement):
                value = copy.deepcopy(self.intent)
                value[key] = replacement
                self.assertEqual(self.validator.validate(value).validation, "failed")

    def test_non_objects_and_malformed_sections(self):
        for value in (None, [], "intent", 1):
            self.assertEqual(self.validator.validate(value).validation, "failed")
        for key in ("requester", "environment", "target", "approval", "verification"):
            for malformed in (None, [], "bad", 1):
                value = copy.deepcopy(self.intent)
                value[key] = malformed
                self.assertEqual(self.validator.validate(value).validation, "failed")

    def test_file_input_read_only(self):
        with patch("pathlib.Path.open", mock_open(read_data=json.dumps(self.intent))) as opened:
            self.assertEqual(self.validator.validate_file("intent.json").validation, "passed")
            opened.assert_called_once_with("r", encoding="utf-8")

    def test_invalid_file_input(self):
        for data in ("not json", '{"risk":"LOW","risk":"HIGH"}', '{"risk":NaN}', "[]"):
            with patch("pathlib.Path.open", mock_open(read_data=data)):
                self.assertEqual(self.validator.validate_file("intent.json").validation, "failed")
        with patch("pathlib.Path.open", side_effect=OSError("private path")):
            report = self.validator.validate_file("missing.json")
            self.assertEqual(report.validation, "failed")
            self.assertNotIn("private path", json.dumps(report.to_dict()))

    def test_no_side_effects_or_input_mutation(self):
        original = copy.deepcopy(self.intent)
        with patch("subprocess.Popen", side_effect=AssertionError("process forbidden")), \
             patch("os.system", side_effect=AssertionError("shell forbidden")), \
             patch("socket.socket", side_effect=AssertionError("network forbidden")), \
             patch("builtins.open", side_effect=AssertionError("IO forbidden")), \
             patch("pathlib.Path.open", side_effect=AssertionError("IO forbidden")):
            self.assertEqual(self.validator.validate(self.intent).validation, "passed")
        self.assertEqual(self.intent, original)
        self.assertFalse(hasattr(self.validator, "__dict__"))


if __name__ == "__main__":
    unittest.main()
