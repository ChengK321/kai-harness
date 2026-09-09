import unittest

from app.rules import validate_registry


# 重复身份会造成引用歧义，即使条目内容相同也必须拒绝。
class DuplicateIdTest(unittest.TestCase):
    # MCP Registry 使用 server_id，其他 Registry 使用 id。
    def test_rejects_duplicate_server_id(self):
        fields = ["server_id", "transport", "endpoint", "tools", "health_check", "enabled"]
        item = {"server_id": "m1", "transport": "stdio", "endpoint": None, "tools": [], "health_check": {}, "enabled": False}
        data = {"version": "1.0", "default_action": "deny", "servers": [item, dict(item)], "entry_schema": {"required_fields": fields}, "defaults": {"enabled": False}, "validation": {"unique_key": "server_id"}}
        errors, _ = validate_registry(data, "mcp", "fixture.yaml")
        self.assertIn("DUPLICATE_ID", {item.code for item in errors})


if __name__ == "__main__": unittest.main()
