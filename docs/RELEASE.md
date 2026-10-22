# PatchProof v0.2.0

**Initial preview: local check receipts for AI-assisted code.**

PatchProof helps answer whether an earlier “tests passed” still describes the watched inputs in front of you. It combines Codex workflows for review, focused fixes, and maintainer handoff with a local command recorder and browser receipt viewer.

## Included

- Three Codex skills and a local marketplace descriptor.
- Read-only Git change inventory.
- Check receipts with command outcomes and explicit watched-file fingerprints.
- Detection of changed inputs during or after a check.
- Browser import, local file comparison, path search, Markdown export, and light/dark themes.
- Folder and glob watch selection, plus `patchproof` console commands from an editable install.
- A runnable calculator demonstration, automated checks, and maintainer documentation.

## Requirements and verification

Python 3.11+ runs the helpers. Git is needed for inventory. Node.js 24 is used for website tests. Codex access is needed only for the AI workflows; normal account limits apply.

Local validation covers 27 Python and 13 JavaScript tests. A controlled Windows Codex CLI test loaded the installed skills, reproduced and fixed a calculator regression without weakening its tests, and detected a later edit. Read [the exact validation scope](VALIDATION.md) and [integration evidence](CODEX_TEST.md).

## Known limits

The runner is not a sandbox. Receipts are editable, unsigned, and limited to explicit watched files and sampled moments. A passing check is not a correctness or security guarantee. Desktop picker activation, other AI hosts, and broad platform compatibility remain unverified. No comparative performance or approval claim is made.

Start with [installation](../INSTALL.md) or [the demo](../examples/README.md). See [contributing](../CONTRIBUTING.md) for feedback and [security reporting](../SECURITY.md) for sensitive issues.
