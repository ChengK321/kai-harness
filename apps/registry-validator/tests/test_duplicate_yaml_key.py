import tempfile
import unittest
from pathlib import Path

from app.validator import DuplicateKeyError, load_yaml


class DuplicateYamlKeyTest(unittest.TestCase):
    # 重复 Key 必须在解析阶段失败，不能采用 PyYAML 的后值覆盖行为。
    def test_duplicate_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.yaml"
            path.write_text("version: '1.0'\nversion: '1.1'\n", encoding="utf-8")
            with self.assertRaises(DuplicateKeyError):
                load_yaml(path)


if __name__ == "__main__": unittest.main()
