import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("agents", ROOT / "patchproof/agents.py")
agents = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agents)


class AgentAdapterTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".test-tmp"
        base.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base)
        self.repo = Path(self.temp.name).resolve()
        self.addCleanup(self.temp.cleanup)

    def test_every_host_gets_its_own_file(self):
        results = agents.install(self.repo, sorted(agents.AGENTS))
        self.assertEqual(len(results), len(agents.AGENTS))
        for agent, relative, action in results:
            self.assertEqual(action, "created")
            self.assertTrue((self.repo / relative).is_file(), relative)
            self.assertIn("pp verify", (self.repo / relative).read_text(encoding="utf-8"))

    def test_cursor_and_copilot_files_carry_frontmatter(self):
        agents.install(self.repo, ["cursor", "copilot"])
        cursor = (self.repo / ".cursor/rules/patchproof.mdc").read_text(encoding="utf-8")
        copilot = (self.repo / ".github/instructions/patchproof.instructions.md").read_text(encoding="utf-8")
        self.assertIn("alwaysApply: true", cursor)
        self.assertIn('applyTo: "**"', copilot)

    def test_existing_instructions_are_appended_never_replaced(self):
        target = self.repo / "CLAUDE.md"
        target.write_text("# House rules\n\nKeep this.\n", encoding="utf-8")
        agents.install(self.repo, ["claude"])
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# House rules"))
        self.assertIn("Keep this.", text)
        self.assertIn(agents.MARKER_START, text)
        self.assertIn(agents.MARKER_END, text)

    def test_install_is_idempotent(self):
        agents.install(self.repo, ["codex"])
        first = (self.repo / "AGENTS.md").read_text(encoding="utf-8")
        results = agents.install(self.repo, ["codex"])
        self.assertEqual(results[0][2], "already installed")
        self.assertEqual((self.repo / "AGENTS.md").read_text(encoding="utf-8"), first)

    def test_unknown_agent_is_rejected(self):
        with self.assertRaises(agents.AdapterError):
            agents.install(self.repo, ["not-a-real-agent"])

    def test_dry_run_writes_nothing(self):
        results = agents.install(self.repo, ["claude", "cursor"], dry_run=True)
        self.assertTrue(all(action.startswith("would") for _, _, action in results))
        self.assertEqual(list(self.repo.iterdir()), [])

    def test_detect_finds_existing_host_configuration(self):
        (self.repo / ".cursor").mkdir()
        (self.repo / "CLAUDE.md").write_text("x", encoding="utf-8")
        self.assertEqual(agents.detect(self.repo), ["claude", "cursor"])

    def test_status_reports_missing_then_installed(self):
        before = {row["agent"]: row["installed"] for row in agents.status(self.repo)}
        self.assertFalse(any(before.values()))
        agents.install(self.repo, ["gemini"])
        after = {row["agent"]: row["installed"] for row in agents.status(self.repo)}
        self.assertTrue(after["gemini"])


if __name__ == "__main__":
    unittest.main()
