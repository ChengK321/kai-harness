import unittest

from app.rules import validate_cross_references


class MissingToolReferenceTest(unittest.TestCase):
    # Agent allow 中的每个 Tool ID 都必须存在于 Tool Registry。
    def test_agent_unknown_tool_is_error(self):
        registries = {"agent": {"agents": [{"tool_access": {"allow": ["missing.tool"]}}]}, "tool": {"tools": []}, "environment": {"environments": []}, "mcp": {"servers": []}}
        errors, checks = validate_cross_references(registries, {key: f"{key}.yaml" for key in registries})
        self.assertIn("CROSS_AGENT_TOOL_NOT_FOUND", {item.code for item in errors})
        self.assertEqual("failed", checks[0]["status"])


if __name__ == "__main__": unittest.main()
