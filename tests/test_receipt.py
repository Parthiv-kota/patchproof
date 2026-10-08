import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("receipt", ROOT / "scripts/receipt.py")
receipt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receipt)


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".test-tmp"
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.repo = Path(self.temp.name).resolve()
        assert self.repo.is_relative_to(base.resolve())
        self.addCleanup(self.temp.cleanup)
        (self.repo / "app.py").write_text("value = 42\n", encoding="utf-8")

    def run_check(self, code="assert 2 + 2 == 4", **kwargs):
        return receipt.run_check(self.repo, ["app.py"], [sys.executable, "-c", code], **kwargs)

    def test_real_success_has_current_hashes(self):
        result = self.run_check()
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(receipt.inspect_receipt(self.repo, result)["state"], "current_passed")
        self.assertNotIn("value = 42", json.dumps(result))

    def test_real_failure_is_not_success(self):
        result = self.run_check("raise SystemExit(7)")
        self.assertEqual(result["exit_code"], 7)
        self.assertEqual(receipt.inspect_receipt(self.repo, result)["state"], "current_failed")

    def test_later_edit_invalidates_success(self):
        result = self.run_check()
        (self.repo / "app.py").write_text("value = 43\n", encoding="utf-8")
        state = receipt.inspect_receipt(self.repo, result)
        self.assertEqual(state["state"], "changed_since_check")
        self.assertEqual(state["changed_files"], ["app.py"])

    def test_deleted_file_invalidates_success(self):
        result = self.run_check()
        (self.repo / "app.py").unlink()
        self.assertEqual(receipt.inspect_receipt(self.repo, result)["state"], "changed_since_check")

    def test_check_modifying_watched_file_is_not_current_pass(self):
        result = self.run_check("from pathlib import Path; Path('app.py').write_text('new')")
        self.assertEqual(receipt.inspect_receipt(self.repo, result)["state"], "changed_during_check")

    def test_missing_executable_is_error(self):
        result = receipt.run_check(self.repo, ["app.py"], [str(self.repo / "missing-executable")])
        self.assertEqual(receipt.inspect_receipt(self.repo, result)["state"], "current_error")

    def test_timeout_is_not_success(self):
        result = self.run_check("import time; time.sleep(30)", timeout=1)
        self.assertEqual(receipt.inspect_receipt(self.repo, result)["state"], "current_timed_out")

    def test_unsafe_and_missing_paths_are_rejected(self):
        for name in ["../outside", "C:/Windows/system.ini", "/etc/passwd", "missing.py", "a/../app.py"]:
            with self.subTest(name=name), self.assertRaises((receipt.ReceiptError, OSError)):
                receipt.fingerprint(self.repo, [name])

    def test_invalid_receipts_are_rejected(self):
        result = self.run_check()
        result["exit_code"] = 1
        with self.assertRaises(receipt.ReceiptError):
            receipt.inspect_receipt(self.repo, result)
        with self.assertRaises(receipt.ReceiptError):
            receipt.inspect_receipt(self.repo, {})

    def test_html_escapes_command_text(self):
        result = self.run_check()
        result["command"] = ["<script>alert(1)</script>"]
        report = receipt.report_html(result, receipt.inspect_receipt(self.repo, result))
        self.assertNotIn("<script>", report)
        self.assertIn("&lt;script&gt;", report)

    def test_existing_output_is_not_replaced(self):
        path = self.repo / "keep.txt"
        path.write_text("original", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            receipt.write_new(path, "replacement")
        self.assertEqual(path.read_text(), "original")

    def test_cli_roundtrip_and_stale_exit_code(self):
        path = self.repo / "result.json"
        code = receipt.main(["run", "--repo", str(self.repo), "--watch", "app.py", "--out", str(path),
                             "--", sys.executable, "-c", "pass"])
        self.assertEqual(code, 0)
        self.assertEqual(receipt.main(["status", "--repo", str(self.repo), "--receipt", str(path)]), 0)
        (self.repo / "app.py").write_text("changed", encoding="utf-8")
        self.assertEqual(receipt.main(["status", "--repo", str(self.repo), "--receipt", str(path)]), 1)


if __name__ == "__main__":
    unittest.main()
