import unittest
from pathlib import Path

from app.rules import validate_schema_instance
from app.validator import load_schema


class SchemaValidationTest(unittest.TestCase):
    # 外部 Tool Registry Schema 必须识别结构类型与必填字段错误。
    def test_invalid_registry_fails_external_schema(self):
        schema = load_schema(Path("/opt/kai/configs/schema/registry/tool-registry.schema.json"))
        invalid = {"version": "1.0", "default_action": "deny", "tools": "not-an-array"}
        errors = validate_schema_instance(invalid, schema, "fixture.yaml")
        codes = {item.code for item in errors}
        self.assertIn("SCHEMA_TYPE", codes)
        self.assertIn("SCHEMA_REQUIRED", codes)


if __name__ == "__main__": unittest.main()
