# Changelog

## 0.2.0 — unreleased

### Added

- `badge/action.yml` — a composite action that runs a check, renders the badge and commits it to a badge branch, with `state` and `badge-url` outputs. A failing check publishes a failing badge instead of leaving the last green one.
- A self-badge workflow: this repository now publishes its own live badge from its own test suite.
- `pp agents` — writes the verification instruction into the rule file each coding host reads: Claude Code (`CLAUDE.md`), Codex (`AGENTS.md`), Cursor (`.cursor/rules/*.mdc`), Windsurf, Cline, Roo Code, Aider (`CONVENTIONS.md`), Gemini CLI and GitHub Copilot. Existing files are appended to, never replaced; `pp agents detect` and `pp agents list` show what a repository already uses.
- `pp verify` — one command, no flags: watches source and test trees plus dependency manifests, runs the command, prints one plain sentence, writes a receipt. Exit 1 the moment the result is stale.
- `pp audit` — re-checks every receipt in a repository and exits nonzero if any is out of date. The line that belongs in CI.
- `pp badge` — a self-contained SVG that can never claim a pass for a stale receipt.
- `pp` as a short alias for `patchproof`, plus a composite GitHub Action (`action.yml`) so adoption is one workflow step.
- `scripts/render_demo.py` — renders the site's demo from a real verify/audit run instead of hand-written terminal text.
- Homepage rebuilt around the stale-check provocation, with the 12-second demo embedded.


- Added `--watch-dir` and `--watch-glob` so a check can watch a folder or a pattern instead of every file by hand. Expansion skips VCS metadata, virtual environments, caches and dependency folders, keeps the existing containment checks, and fails loudly on an empty or oversized selection.
- Added an installable `pyproject.toml` with `patchproof` and `patchproof-snapshot` console commands, so the recorder no longer has to be run from the source folder.
- Fixed the viewer labelling a saved demonstration's files as a live comparison; per-file states now come from `fileLabel()` in `site/core.mjs`.
- Corrected the CI action versions, widened the Python matrix to 3.11–3.14, and made the demo step assert that all three report states were generated.
- Added Dependabot configuration for actions and packaging metadata.
- Added a GitHub Pages workflow that publishes the website and re-checks links and policy before deploying.
- Added a rendered 1200×630 social preview with `og:image` and Twitter card metadata on every page; the checks fail if it is missing.
- Documentation: expanded the documentation index and refreshed version references.

## 0.1.0 — initial preview

- Added Codex skills for review, focused fixes and factual handoff.
- Added a read-only Git change-inventory helper.
- Added local command receipts with explicit watched-file fingerprints, exit codes and timeout handling.
- Added freshness checks for edits during or after a recorded check.
- Added an accessible local website with saved demonstration states, receipt import, browser-side file comparison, path search, Markdown export and light/dark themes.
- Added Python and JavaScript checks, installation instructions and a controlled Codex CLI integration test.
- Added a command reference, architecture guide, hands-on example, author credits, release notes, and a Windows/Linux CI configuration.

This version is an early preview. Marketplace approval, a production security audit, comparative performance improvement and broad compatibility have not been established. See [validation](docs/VALIDATION.md) for the checks actually performed.
