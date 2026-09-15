import ast
import json
import re
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import mock_open, patch

from vps_observer import VPSObserver
from vps_observer.models import Capacity
from vps_observer.observer import _cpu_percent, _disk, _memory


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "configs/schema/observation.schema.json").read_text())


class ObserverTests(unittest.TestCase):
    def setUp(self):
        for target, value in (
            ("os.uname", SimpleNamespace(nodename="test-host", sysname="Linux", release="6.8")),
            ("_cpu_percent", 25.0),
            ("_memory", Capacity(1000, 400)),
            ("_disk", Capacity(2000, 500)),
        ):
            mock = patch("vps_observer.observer." + target, return_value=value)
            setattr(self, target.split(".")[-1], mock.start())
            self.addCleanup(mock.stop)

    def assert_schema(self, value, schema):
        """Check keywords used by this output's schema paths; not a general validator."""
        if "$ref" in schema:
            schema = SCHEMA["$defs"][schema["$ref"].split("/")[-1]]
        kind = schema.get("type")
        if kind:
            types = {"object": dict, "array": list, "string": str,
                     "integer": int, "number": (int, float), "boolean": bool}
            self.assertIsInstance(value, types[kind])
            if kind in ("integer", "number"):
                self.assertNotIsInstance(value, bool)
        if "const" in schema:
            self.assertEqual(value, schema["const"])
        if "enum" in schema:
            self.assertIn(value, schema["enum"])
        if kind == "object":
            self.assertTrue(set(schema.get("required", [])).issubset(value))
            properties = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                self.assertTrue(set(value).issubset(properties))
            for key, item in value.items():
                self.assert_schema(item, properties[key])
        elif kind == "array":
            for item in value:
                self.assert_schema(item, schema["items"])
        elif kind == "string":
            self.assertGreaterEqual(len(value), schema.get("minLength", 0))
            self.assertLessEqual(len(value), schema.get("maxLength", float("inf")))
            if "pattern" in schema:
                self.assertIsNotNone(re.search(schema["pattern"], value))
            if schema.get("format") == "date-time":
                self.assertIsNotNone(datetime.fromisoformat(value).tzinfo)
        elif kind in ("integer", "number"):
            self.assertGreaterEqual(value, schema.get("minimum", -float("inf")))
            self.assertLessEqual(value, schema.get("maximum", float("inf")))

    def test_normal_raw_and_contract(self):
        raw = VPSObserver().collect("test-vps")
        self.assertEqual((raw.hostname, raw.os, raw.kernel), ("test-host", "Linux", "6.8"))
        self.assertEqual(raw.resources, {"cpu_percent": 25, "memory_percent": 40, "disk_percent": 25})
        result = raw.to_observation()
        self.assert_schema(result, SCHEMA)
        self.assertEqual(result["environment_id"], "test-vps")
        self.assertEqual(result["metadata"]["collection_status"], "complete")
        self.assertEqual(set(result["system"]), {"cpu", "memory", "disk"})
        self.assertFalse(set(result) & {"hostname", "os", "kernel", "resources", "errors"})
        self.assertNotIn("services", result)
        json.dumps(result, allow_nan=False)

    def test_partial_failure_is_sanitized(self):
        self._memory.side_effect = OSError("secret diagnostic")
        raw = VPSObserver().collect("test")
        result = raw.to_observation()
        self.assertIsNone(raw.memory)
        self.assert_schema(result, SCHEMA)
        self.assertEqual(result["metadata"]["collection_status"], "partial")
        self.assertNotIn("memory", result["system"])
        self.assertEqual(result["metadata"]["errors"][0]["code"], "MEMORY_UNAVAILABLE")
        self.assertNotIn("secret", json.dumps(result))

    def test_all_collection_failures(self):
        for mock in (self.uname, self._cpu_percent, self._memory, self._disk):
            mock.side_effect = OSError("unavailable")
        result = VPSObserver().collect("test").to_observation()
        self.assert_schema(result, SCHEMA)
        self.assertEqual(result["metadata"]["collection_status"], "failed")
        self.assertEqual(len(result["metadata"]["errors"]), 6)
        self.assertEqual(result["system"], {})

    def test_invalid_input_does_not_collect(self):
        for value in ("", "  ", None, 1):
            with self.assertRaises(ValueError):
                VPSObserver().collect(value)
        self.uname.assert_not_called()

    def test_cpu_sampling(self):
        with patch("vps_observer.observer._cpu_ticks", side_effect=[(100, 50), (200, 125)]), \
             patch("vps_observer.observer.time.sleep") as sleep:
            self.assertEqual(_cpu_percent(0.1), 25)
            sleep.assert_called_once_with(0.1)

    def test_bad_cpu_delta(self):
        with patch("vps_observer.observer._cpu_ticks", return_value=(100, 50)), \
             patch("vps_observer.observer.time.sleep"):
            with self.assertRaises(ValueError):
                _cpu_percent(0.1)

    def test_memory_read_only(self):
        with patch("pathlib.Path.open", mock_open(read_data="MemTotal: 100 kB\nMemAvailable: 60 kB\n")) as opened:
            self.assertEqual(_memory(), Capacity(102400, 40960))
            opened.assert_called_once_with("r", encoding="ascii")

    def test_invalid_memory(self):
        with patch("pathlib.Path.open", mock_open(read_data="MemTotal: 100 kB\nMemAvailable: 101 kB\n")):
            with self.assertRaises(ValueError):
                _memory()

    def test_disk_scope(self):
        with patch("shutil.disk_usage", return_value=SimpleNamespace(total=100, used=20)) as usage:
            self.assertEqual(_disk(), Capacity(100, 20))
            usage.assert_called_once_with("/")

    def test_no_dangerous_calls(self):
        with patch("subprocess.Popen", side_effect=AssertionError("subprocess forbidden")), \
             patch("os.system", side_effect=AssertionError("shell forbidden")), \
             patch("socket.socket", side_effect=AssertionError("network forbidden")), \
             patch("builtins.open", side_effect=AssertionError("unexpected file access")):
            VPSObserver().collect("test").to_observation()
        allowed = {"math", "os", "shutil", "time", "datetime", "pathlib", "dataclasses", "typing"}
        for file in (ROOT / "apps/vps-observer/vps_observer").glob("*.py"):
            tree = ast.parse(file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertTrue(all(alias.name in allowed for alias in node.names))
                elif isinstance(node, ast.ImportFrom) and not node.level:
                    self.assertIn(node.module, allowed)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, {"system", "popen", "write", "write_text", "write_bytes", "unlink", "mkdir"})


if __name__ == "__main__":
    unittest.main()
