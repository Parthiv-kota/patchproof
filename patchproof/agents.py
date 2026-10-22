"""Write agent-host rule files so any coding agent records its checks.

One instruction, many dialects. Every host that can read a repository-level
rules file gets the same four lines, worded for how that host reads them.
Files are never overwritten: an existing CLAUDE.md or AGENTS.md belongs to the
user, so the adapter appends a clearly marked block or refuses and says why.
"""
import json
from pathlib import Path

MARKER_START = "<!-- patchproof:start -->"
MARKER_END = "<!-- patchproof:end -->"

RULE = """## Verification (patchproof)

After you change code and run a check, record it so the result stays tied to the files it describes:

```sh
pp verify -- <your check command>
```

Before you hand work over, or whenever an earlier pass might be stale, run:

```sh
pp audit
```

If `pp audit` reports `changed_since_check`, the earlier pass no longer describes the current code. Rerun the check and say so. Never describe a stale pass as passing, and never claim a check you did not run.
"""

AGENTS = {
    "claude": {"path": "CLAUDE.md", "label": "Claude Code"},
    "codex": {"path": "AGENTS.md", "label": "Codex"},
    "cursor": {"path": ".cursor/rules/patchproof.mdc", "label": "Cursor"},
    "windsurf": {"path": ".windsurf/rules/patchproof.md", "label": "Windsurf"},
    "cline": {"path": ".clinerules/patchproof.md", "label": "Cline"},
    "roo": {"path": ".roo/rules/patchproof.md", "label": "Roo Code"},
    "aider": {"path": "CONVENTIONS.md", "label": "Aider"},
    "gemini": {"path": "GEMINI.md", "label": "Gemini CLI"},
    "copilot": {"path": ".github/instructions/patchproof.instructions.md", "label": "GitHub Copilot"},
    "generic": {"path": ".patchproof/AGENTS.md", "label": "any other agent (AGENTS.md convention)"},
}

CURSOR_FRONTMATTER = """---
description: Record checks with patchproof so a passing result stays tied to the code it describes.
alwaysApply: true
---

"""

COPILOT_FRONTMATTER = """---
applyTo: "**"
---

"""


class AdapterError(Exception):
    pass


def block_for(agent):
    body = RULE
    if agent == "cursor":
        body = CURSOR_FRONTMATTER + body
    if agent == "copilot":
        body = COPILOT_FRONTMATTER + body
    return body


def install(root, agents, dry_run=False):
    """Write rule files for the named agents. Returns a list of (agent, path, action)."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise AdapterError("The project directory does not exist.")
    unknown = [a for a in agents if a not in AGENTS]
    if unknown:
        raise AdapterError("Unknown agent(s): " + ", ".join(unknown) +
                           ". Choose from: " + ", ".join(sorted(AGENTS)))
    results = []
    for agent in agents:
        relative = AGENTS[agent]["path"]
        target = root / relative
        body = block_for(agent)
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if MARKER_START in existing:
                results.append((agent, relative, "already installed"))
                continue
            if dry_run:
                results.append((agent, relative, "would append"))
                continue
            target.write_text(existing.rstrip() + "\n\n" + MARKER_START + "\n" + body + MARKER_END + "\n",
                              encoding="utf-8")
            results.append((agent, relative, "appended"))
            continue
        if dry_run:
            results.append((agent, relative, "would create"))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(MARKER_START + "\n" + body + MARKER_END + "\n", encoding="utf-8")
        results.append((agent, relative, "created"))
    return results


def detect(root):
    """Guess which agents this repository already talks to."""
    root = Path(root).resolve(strict=True)
    hints = {
        "claude": ["CLAUDE.md", ".claude"],
        "codex": ["AGENTS.md", ".codex"],
        "cursor": [".cursor"],
        "windsurf": [".windsurf", ".windsurfrules"],
        "cline": [".clinerules"],
        "roo": [".roo"],
        "aider": ["CONVENTIONS.md", ".aider.conf.yml"],
        "gemini": ["GEMINI.md"],
        "copilot": [".github/copilot-instructions.md", ".github/instructions"],
    }
    return sorted(agent for agent, paths in hints.items()
                  if any((root / path).exists() for path in paths))


def status(root):
    root = Path(root).resolve(strict=True)
    return [{"agent": agent, "label": AGENTS[agent]["label"], "path": AGENTS[agent]["path"],
             "installed": (root / AGENTS[agent]["path"]).exists()}
            for agent in sorted(AGENTS)]
