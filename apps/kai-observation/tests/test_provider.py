import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from kai_observation import ObservationProviderError, VPSObserverProvider
from vps_observer.models import Capacity, RawObservation


class ProviderTests(unittest.TestCase):
    def setUp(self):
        patcher = patch("kai_observation.provider.VPSObserver")
        self.adapter = patcher.start()
        self.addCleanup(patcher.stop)
        self.raw = RawObservation(
            "test-vps", "2026-09-14T08:00:00Z", hostname="private-host",
            cpu=25.0, memory=Capacity(1000, 400), disk=Capacity(2000, 500),
        )
        self.adapter.return_value.collect.return_value = self.raw

    def test_contract_output(self):
        schema = json.loads((Path(__file__).resolve().parents[3] /
                             "configs/schema/observation.schema.json").read_text())
        result = VPSObserverProvider().get_observation("test-vps")
        self.assertEqual(result, self.raw.to_observation())
        self.assertTrue(set(schema["required"]).issubset(result))
        self.assertTrue(set(result).issubset(schema["properties"]))
        self.assertEqual(result["version"], schema["properties"]["version"]["const"])
        self.assertIsNotNone(datetime.fromisoformat(result["timestamp"]).tzinfo)
        self.assertTrue(result["timestamp"].endswith("Z"))
        self.assertNotIn("private-host", json.dumps(result, allow_nan=False))
        self.assertEqual(set(result["system"]), {"cpu", "memory", "disk"})
        self.assertEqual(set(result["system"]["cpu"]), {"usage_percent"})
        self.assertTrue(0 <= result["system"]["cpu"]["usage_percent"] <= 100)
        for key in ("memory", "disk"):
            self.assertEqual(set(result["system"][key]), set(schema["$defs"]["capacity"]["properties"]))
            for value in result["system"][key].values():
                self.assertIs(type(value), int)
                self.assertGreaterEqual(value, 0)
        metadata = result["metadata"]
        self.assertTrue(set(metadata).issubset(schema["properties"]["metadata"]["properties"]))
        self.assertEqual(metadata["adapter_type"], "vps")
        self.assertEqual(metadata["collection_status"], "complete")
        self.assertEqual(metadata["errors"], [])

    def test_environment_id_passed_unchanged(self):
        VPSObserverProvider().get_observation(" local-label ")
        self.adapter.return_value.collect.assert_called_once_with(" local-label ")

    def test_adapter_exceptions_converted(self):
        for stage in ("construct", "collect", "convert"):
            with self.subTest(stage=stage):
                self.adapter.reset_mock(side_effect=True, return_value=True)
                if stage == "construct":
                    self.adapter.side_effect = OSError("secret")
                elif stage == "collect":
                    self.adapter.return_value.collect.side_effect = RuntimeError("secret")
                else:
                    self.adapter.return_value.collect.return_value.to_observation.side_effect = ValueError("secret")
                with self.assertRaisesRegex(ObservationProviderError, "VPS observation adapter failed") as caught:
                    VPSObserverProvider().get_observation("test")
                self.assertNotIn("secret", str(caught.exception))
                self.assertTrue(caught.exception.__suppress_context__)

    def test_partial_error_preserved(self):
        self.raw.errors.append({"section": "system", "code": "KERNEL_UNAVAILABLE",
                                "message": "Unable to collect kernel."})
        result = VPSObserverProvider().get_observation("test-vps")
        self.assertEqual(result["metadata"]["collection_status"], "partial")
        self.assertEqual(result["metadata"]["errors"], self.raw.errors)

    def test_invalid_id_does_not_call_adapter(self):
        for value in (None, "", "  ", 1):
            with self.assertRaises(ValueError):
                VPSObserverProvider().get_observation(value)
        self.adapter.assert_not_called()

    def test_no_side_effects_or_retained_state(self):
        provider = VPSObserverProvider()
        with patch("subprocess.Popen", side_effect=AssertionError("process forbidden")) as process, \
             patch("os.system", side_effect=AssertionError("shell forbidden")) as shell, \
             patch("socket.socket", side_effect=AssertionError("network forbidden")) as network, \
             patch("builtins.open", side_effect=AssertionError("file access forbidden")) as opened, \
             patch("pathlib.Path.open", side_effect=AssertionError("file access forbidden")) as path_open:
            first = provider.get_observation("test-vps")
            first["system"]["cpu"]["usage_percent"] = 99
            second = provider.get_observation("test-vps")
            self.assertEqual(second["system"]["cpu"]["usage_percent"], 25)
            for mock in (process, shell, network, opened, path_open):
                mock.assert_not_called()
        self.assertEqual(self.adapter.call_count, 2)
        self.assertFalse(hasattr(provider, "__dict__"))

    def test_interrupt_not_converted(self):
        self.adapter.return_value.collect.side_effect = KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            VPSObserverProvider().get_observation("test")


if __name__ == "__main__":
    unittest.main()
