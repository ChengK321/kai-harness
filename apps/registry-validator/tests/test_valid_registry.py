import unittest

from app.rules import validate_registry


# 正向样例同时验证未来 side_effect 字段的兼容路径。
class ValidRegistryTest(unittest.TestCase):
    # READONLY、无副作用且默认禁用的工具应通过校验。
    def test_valid_tool_with_future_fields(self):
        data = {
            "version": "1.0", "default_action": "deny",
            "tools": [{"id": "safe-read", "name": "Safe Read", "version": "1.0", "category": "filesystem", "description": "Read metadata", "permission_level": "READONLY", "timeout": 10, "requires_approval": False, "enabled": False, "side_effect": "none"}],
            "entry_schema": {"required_fields": ["id", "name", "version", "category", "description", "permission_level", "timeout", "requires_approval", "enabled"]},
            "defaults": {"enabled": False}, "validation": {"unique_key": "id"},
        }
        errors, warnings = validate_registry(data, "tool", "fixture.yaml")
        self.assertEqual([], errors)
        self.assertEqual([], warnings)


if __name__ == "__main__": unittest.main()
