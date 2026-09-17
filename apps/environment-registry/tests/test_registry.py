import unittest

from environment_registry import EnvironmentRecord, EnvironmentRegistry


class RegistryTests(unittest.TestCase):
    def test_register_and_get(self):
        registry = EnvironmentRegistry()
        env = EnvironmentRecord("vps-1", "vps", "trusted", ["observation"])
        registry.register(env)
        self.assertEqual(registry.get("vps-1"), env)

    def test_duplicate_environment_is_rejected(self):
        registry = EnvironmentRegistry()
        env = EnvironmentRecord("vps-1", "vps", "trusted", [])
        registry.register(env)
        with self.assertRaises(ValueError):
            registry.register(env)

    def test_capability_query(self):
        registry = EnvironmentRegistry()
        registry.register(EnvironmentRecord("robot-1", "robot", "trusted", ["observe"]))
        self.assertTrue(registry.has_capability("robot-1", "observe"))
        self.assertFalse(registry.has_capability("robot-1", "execute"))

    def test_unknown_environment_fails(self):
        registry = EnvironmentRegistry()
        with self.assertRaises(KeyError):
            registry.get("missing")


if __name__ == "__main__":
    unittest.main()
