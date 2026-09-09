import unittest
from pathlib import Path

from app.rules import validate_schema_instance
from app.validator import load_schema


class InvalidPermissionTest(unittest.TestCase):
    # 非法权限由外部 Schema enum 拒绝，而非 Registry 自带 entry_schema。
    def test_rejects_unknown_agent_permission(self):
        schema = load_schema(Path("/opt/kai/configs/schema/registry/agent-registry.schema.json"))
        fields = {"id": "a1", "name": "Agent", "type": "generic", "adapter": "adapter", "version": "1.0", "status": "disabled", "capabilities": [], "permissions": ["SUPERUSER"], "memory_access": {"read_layers": [], "write_layers": []}, "tool_access": {"allow": [], "deny": ["*"]}}
        data = {"version": "1.0", "default_action": "deny", "agents": [fields], "defaults": {}, "validation": {}}
        errors = validate_schema_instance(data, schema, "fixture.yaml")
        self.assertIn("SCHEMA_ENUM", {item.code for item in errors})


if __name__ == "__main__": unittest.main()
