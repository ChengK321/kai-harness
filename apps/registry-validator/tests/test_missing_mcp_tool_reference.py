import unittest

from app.rules import validate_cross_references


class MissingMcpToolReferenceTest(unittest.TestCase):
    # MCP Server 暴露的 Tool 也必须先进入统一 Tool Registry。
    def test_mcp_unknown_tool_is_error(self):
        registries = {"agent": {"agents": []}, "tool": {"tools": []}, "environment": {"environments": []}, "mcp": {"servers": [{"tools": ["missing.mcp.tool"]}]}}
        errors, checks = validate_cross_references(registries, {key: f"{key}.yaml" for key in registries})
        self.assertIn("CROSS_MCP_TOOL_NOT_FOUND", {item.code for item in errors})
        self.assertEqual("failed", checks[2]["status"])


if __name__ == "__main__": unittest.main()
