"""Every frozen negative fixture must deny for its intended reason."""

import json
import unittest
from pathlib import Path

from kai_governance_validator import GovernanceValidator


FIXTURES = Path(__file__).parent / "fixtures/governance-invalid"
EXPECTED = {
    "command-field.json": "executable_fields",
    "executor-field.json": "executable_fields",
    "workflow-field.json": "executable_fields",
    "prompt-field.json": "executable_fields",
    "fake-approval.json": "approval",
    "high-risk-without-approval.json": "approval",
    "unknown-field.json": "closed_fields",
    "invalid-risk.json": "risk",
}


class NegativeCorpusTests(unittest.TestCase):
    def test_all_fixtures_deny_with_reasons(self):
        files = sorted(FIXTURES.glob("*.json"))
        self.assertEqual({file.name for file in files}, set(EXPECTED),
                         "Corpus missing, incomplete or changed without updating expected checks")
        validator = GovernanceValidator()
        for file in files:
            with self.subTest(fixture=file.name):
                intent = json.loads(file.read_text(encoding="utf-8"))
                report = validator.validate(intent)
                # Public API uses status, not an allow boolean.
                self.assertFalse(report.status == "allow")
                self.assertEqual(report.status, "deny")
                failed = [check for check in report.checks if check.status == "failed"]
                self.assertTrue(failed)
                self.assertTrue(all(isinstance(check.reason, str) and check.reason.strip()
                                    for check in failed))
                self.assertIn(EXPECTED[file.name], {check.name for check in failed})


if __name__ == "__main__":
    unittest.main()
