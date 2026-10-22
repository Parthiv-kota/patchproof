# PatchProof documentation

Start with [installation](../INSTALL.md), then [try the calculator example](../examples/README.md).

| Guide | What you will learn |
|---|---|
| [Command reference](CLI.md) | Record and inspect receipts, read states and exit codes, inventory Git changes. |
| [Architecture](ARCHITECTURE.md) | Components, data flow, and the boundaries of the evidence. |
| [Validation](VALIDATION.md) | Checks actually run and what remains unverified. |
| [Codex integration](CODEX_TEST.md) | The installed-plugin test and its observed results. |
| [Evaluation plan](EVALUATION.md) | How future quality comparisons should be measured. |
| [Release notes](RELEASE.md) | Scope, requirements, and known limitations of v0.2.0. |
| [Privacy](../PRIVACY.md) | What is read, recorded, and shared. |
| [Security](../SECURITY.md) | Trust boundaries and vulnerability reporting. |
| [Contributing](../CONTRIBUTING.md) | Development checks and contribution expectations. |
| [Authors](../AUTHORS.md) | Project ownership, AI assistance, and acknowledgments. |

## Reading order

1. [Installation](../INSTALL.md) — get the source and run the demo.
2. [Example walkthrough](../examples/README.md) — a real failure, a real pass, and a stale result.
3. [Command reference](CLI.md) — record and inspect checks, including folder and glob watch selection.
4. [Architecture](ARCHITECTURE.md) — components and data boundaries.
5. [Validation](VALIDATION.md) — what has actually been checked.

## Conventions

All CLI examples run from the PatchProof source folder unless stated otherwise. With an editable install (`pipx install .` or `pip install -e .`) the same commands are available as `patchproof run …` and `patchproof-snapshot --repo …`.

## Where the website lives

| Path | Purpose |
|---|---|
| [`site/`](../site/index.html) | The receipt viewer: import a receipt, compare watched files locally, export a summary. |
| [`web/`](../web/index.html) | The project website: what PatchProof is, how the evidence works, install steps and limits. |

Both are static files with no build step. Serve them with `python -m http.server 8790 --bind 127.0.0.1` from the source folder; the viewer is at `/site/` and the website at `/web/`.

The [main README](../README.md) is the short introduction.
