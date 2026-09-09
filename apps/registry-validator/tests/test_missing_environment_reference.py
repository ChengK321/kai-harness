import unittest

from app.rules import validate_cross_references


class MissingEnvironmentReferenceTest(unittest.TestCase):
    # execution_scope 只能引用 Environment Registry 中已声明的 ID。
    def test_agent_unknown_environment_is_error(self):
        agent = {"tool_access": {"allow": []}, "execution_scope": {"environments": ["missing-env"]}}
        registries = {"agent": {"agents": [agent]}, "tool": {"tools": []}, "environment": {"environments": []}, "mcp": {"servers": []}}
        errors, checks = validate_cross_references(registries, {key: f"{key}.yaml" for key in registries})
        self.assertIn("CROSS_AGENT_ENVIRONMENT_NOT_FOUND", {item.code for item in errors})
        self.assertEqual("failed", checks[1]["status"])


if __name__ == "__main__": unittest.main()
