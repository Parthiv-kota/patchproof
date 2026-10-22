# Changelog

## 0.2.0 — unreleased

- Added `--watch-dir` and `--watch-glob` so a check can watch a folder or a pattern instead of every file by hand. Expansion skips VCS metadata, virtual environments, caches and dependency folders, keeps the existing containment checks, and fails loudly on an empty or oversized selection.
- Added an installable `pyproject.toml` with `patchproof` and `patchproof-snapshot` console commands, so the recorder no longer has to be run from the source folder.
- Fixed the viewer labelling a saved demonstration's files as a live comparison; per-file states now come from `fileLabel()` in `site/core.mjs`.
- Corrected the CI action versions, widened the Python matrix to 3.11–3.14, and made the demo step assert that all three report states were generated.
- Added Dependabot configuration for actions and packaging metadata.
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
