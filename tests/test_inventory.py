"""Exercise the distributable file boundary."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("bundle_inventory", Path(__file__).resolve().parents[1] / "scripts/check_inventory.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class InventoryTests(unittest.TestCase):
    def test_rejects_unlisted_files_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "public-files.json").write_text(json.dumps(["allowed.md"]))
            (root / "allowed.md").write_text("content")
            with patch.object(checker, "ROOT", root), patch.object(checker.subprocess, "check_output") as git:
                git.return_value = "100644 abc 0\tallowed.md\0"
                checker.check_inventory()
                git.return_value += "100644 def 0\tunexpected.md\0"
                with self.assertRaisesRegex(ValueError, "unexpected"):
                    checker.check_inventory()
                git.return_value = "120000 abc 0\tallowed.md\0"
                with self.assertRaisesRegex(ValueError, "ordinary"):
                    checker.check_inventory()


if __name__ == "__main__":
    unittest.main()
