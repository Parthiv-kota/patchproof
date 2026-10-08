import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot", ROOT / "scripts/snapshot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ParserTests(unittest.TestCase):
    def test_paths_with_tabs_and_newlines(self):
        rows = module.parse_numstat(b"3\t1\tsome\tfile\nname.py\0")
        self.assertEqual(rows[0]["path"], "some\tfile\nname.py")
        self.assertEqual(rows[0]["added"], 3)

    def test_binary_counts_are_unknown(self):
        self.assertEqual(module.parse_numstat(b"-\t-\timage.png\0")[0]["added"], None)

    def test_malformed_data_is_rejected(self):
        for raw in [b"bad\0", b"x\t2\tfile.py\0"]:
            with self.subTest(raw=raw), self.assertRaises(module.SnapshotError):
                module.parse_numstat(raw)

    def test_hints_are_explicit_not_findings(self):
        hints = module.review_areas(["src/auth.py", "migrations/001.sql", "package.json"])
        self.assertEqual(len(hints), 3)
        self.assertTrue(all(h.startswith(("Check", "Review")) for h in hints))


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".test-tmp"
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.repo = Path(self.temp.name).resolve()
        assert self.repo.is_relative_to(base.resolve())
        self.addCleanup(self.temp.cleanup)
        self.run_git("init", "--quiet")
        self.run_git("config", "user.name", "PatchProof test fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.run_git("config", "core.autocrlf", "false")
        (self.repo / "app.py").write_text("a = 1\nb = 2\n", encoding="utf-8")
        (self.repo / ".gitignore").write_text("private.env\n", encoding="utf-8")
        self.run_git("add", "--", ".")
        self.run_git("-c", "core.hooksPath=", "commit", "--quiet", "-m", "fixture")

    def run_git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, timeout=10).stdout

    def test_clean_repository_is_not_reported_as_verified(self):
        result = module.snapshot(self.repo)
        self.assertEqual(result["tracked_changed_count"], 0)
        self.assertEqual(result["verification"], "not_run")

    def test_working_changes_count_real_lines(self):
        (self.repo / "app.py").write_text("a = 3\nb = 2\nc = 4\n", encoding="utf-8")
        result = module.snapshot(self.repo)
        self.assertEqual(result["tracked_changes"][0], {"path": "app.py", "added": 2, "removed": 1, "binary": False})

    def test_staged_excludes_later_working_edit(self):
        (self.repo / "app.py").write_text("a = 1\nb = 2\nc = 3\n", encoding="utf-8")
        self.run_git("add", "app.py")
        (self.repo / "app.py").write_text("a = 1\nb = 2\nc = 3\nd = 4\n", encoding="utf-8")
        self.assertEqual(module.snapshot(self.repo, "staged")["tracked_changes"][0]["added"], 1)
        self.assertEqual(module.snapshot(self.repo)["tracked_changes"][0]["added"], 2)

    def test_untracked_report_excludes_ignored_files(self):
        (self.repo / "new file.py").write_text("secret-shaped content is never read", encoding="utf-8")
        (self.repo / "private.env").write_text("do not report", encoding="utf-8")
        result = module.snapshot(self.repo)
        self.assertEqual(result["untracked_paths"], ["new file.py"])
        self.assertNotIn("secret-shaped", json.dumps(result))

    def test_file_limit_is_visible(self):
        for name in ["one.py", "two.py"]:
            (self.repo / name).write_text("x\n", encoding="utf-8")
        self.run_git("add", "one.py", "two.py")
        result = module.snapshot(self.repo, max_files=1)
        self.assertEqual(result["tracked_changed_count"], 2)
        self.assertTrue(result["tracked_truncated"])
        self.assertEqual(len(result["tracked_changes"]), 1)

    def test_subdirectory_does_not_expand_scope(self):
        sub = self.repo / "sub"
        sub.mkdir()
        with self.assertRaises(module.SnapshotError):
            module.snapshot(sub)

    def test_metadata_query_leaves_worktree_and_index_unchanged(self):
        (self.repo / "app.py").write_text("changed\n", encoding="utf-8")
        index = (self.repo / ".git/index").read_bytes()
        status = self.run_git("status", "--porcelain=v1", "-z")
        module.snapshot(self.repo)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        self.assertEqual(self.run_git("status", "--porcelain=v1", "-z"), status)

    def test_invalid_limit_fails(self):
        for limit in [0, 2001]:
            with self.assertRaises(module.SnapshotError):
                module.snapshot(self.repo, max_files=limit)


if __name__ == "__main__":
    unittest.main()
