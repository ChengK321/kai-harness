import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.validator import DEFAULT_FILES, validate_files


class SchemaFailureStopsCrossReferenceTest(unittest.TestCase):
    # 该输入可以被 YAML 解析，但 tool_access 的字符串类型违反 Agent Registry Schema。
    def test_schema_failure_returns_report_without_cross_reference(self):
        invalid_yaml = """
version: "1.0"
default_action: deny
agents:
  - id: broken-agent
    name: Broken Agent
    type: generic
    adapter: generic-adapter
    version: "1.0"
    status: disabled
    capabilities: []
    permissions: [READONLY]
    memory_access:
      read_layers: []
      write_layers: []
    tool_access: invalid-object
defaults:
  status: disabled
  tool_access:
    allow: []
    deny: ["*"]
validation: {}
"""
        with tempfile.TemporaryDirectory() as directory:
            invalid_path = Path(directory) / "agent-registry.yaml"
            invalid_path.write_text(invalid_yaml, encoding="utf-8")
            files = dict(DEFAULT_FILES)
            files["agent"] = invalid_path

            # 若 Schema 门控失效，mock 会让测试以 AssertionError 明确失败。
            with patch("app.validator.validate_cross_references", side_effect=AssertionError("cross reference must not run")) as cross_reference:
                report = validate_files(files=files)

        result = report.to_dict()
        self.assertFalse(cross_reference.called)
        self.assertEqual("failed", result["status"])
        self.assertTrue(result["errors"])
        self.assertIn("SCHEMA_TYPE", {item["code"] for item in result["errors"]})
        self.assertEqual("skipped", result["cross_reference_checks"][0]["status"])


if __name__ == "__main__":
    unittest.main()
