import unittest
from pathlib import Path

from app.rules import validate_schema_instance
from app.validator import load_schema


class MissingRequiredFieldTest(unittest.TestCase):
    # Tool name 缺失必须由独立 Registry Schema 检出。
    def test_rejects_missing_tool_name(self):
        schema = load_schema(Path("/opt/kai/configs/schema/registry/tool-registry.schema.json"))
        tool = {"id": "t1", "version": "1.0", "category": "system", "description": "", "permission_level": "READONLY", "timeout": 10, "requires_approval": False, "enabled": False}
        data = {"version": "1.0", "default_action": "deny", "tools": [tool], "defaults": {}, "risk_policy": {}, "validation": {}}
        errors = validate_schema_instance(data, schema, "fixture.yaml")
        self.assertIn("SCHEMA_REQUIRED", {item.code for item in errors})


if __name__ == "__main__": unittest.main()
