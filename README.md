<p align="center"><img src="assets/icon.svg" width="88" alt="PatchProof logo"></p>

<h1 align="center">PatchProof</h1>
<p align="center"><strong>Tests passed. Do they still match your code?</strong></p>
<p align="center">Local check receipts for AI-assisted development.<br>A Codex plugin, a Python recorder, and a browser viewer.</p>
<p align="center"><a href="INSTALL.md">Install</a> · <a href="examples/README.md">Try the demo</a> · <a href="docs/README.md">Documentation</a> · <a href="CONTRIBUTING.md">Contribute</a></p>
<p align="center"><a href="https://github.com/Parthiv-kota/patchproof/actions/workflows/checks.yml"><img alt="Checks" src="https://github.com/Parthiv-kota/patchproof/actions/workflows/checks.yml/badge.svg"></a> <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-17634e"></a> <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-17634e"></p>

PatchProof records the command you ran, its exit code, and fingerprints of the files you chose to watch. Before handing over a change, compare those files again. If they changed, the earlier pass no longer describes the current inputs.

The Codex skills bring that habit into **review → fix → handoff**, with explanations a beginner can follow and evidence a maintainer can inspect.

**v0.2.0 · early preview · MIT · Python standard library only**

## See the difference

| Without a receipt | With PatchProof |
|---|---|
| “Tests passed.” | The exact command, exit code, time, and watched-file list. |
| Another edit happens after the test. | Changed fingerprints mark the old result as out of date. |
| A reviewer cannot tell what was covered. | Explicit scope and limitations travel with the result. |

A matching pass means the recorded command exited zero and the watched bytes match. It does **not** prove correctness, security, or complete test coverage. Receipts are editable local records, not signed attestations.

## Try it in one minute

Download or clone this source, open a terminal in the `patchproof` folder, and run with Python 3.11 or newer:

```sh
python scripts/demo.py
```

Open the `index.html` path printed at the end. The demo creates an isolated calculator, catches a real bug, fixes it, records a passing test, and makes another edit so you can see the old pass become stale. The first failing test is intentional. Your own project is not changed.

For the interactive viewer:

```sh
python -m http.server 8790 --bind 127.0.0.1
```

Open **<http://127.0.0.1:8790/site/>**. Explore the three saved examples, or import a receipt and select its project folder. You can search watched paths, compare files, export a Markdown summary, and switch between light and dark themes. Selected files are compared inside the browser; they are not uploaded.

The demo, recorder, and viewer need **no AI account or API key**. [Step-by-step walkthrough →](examples/README.md)

## Use it in Codex

From the source folder, with a signed-in Codex CLI:

```sh
codex plugin marketplace add .
codex plugin add patchproof@patchproof-local
```

Start a fresh Codex session in the project you want to work on. Then ask:

> Use PatchProof to review my changes, explain any bugs in plain English, and record the checks you run. Ask before publishing anything.

| Workflow | What to ask | What it does |
|---|---|---|
| `patchproof-review` | “Review this change and explain the risks.” | Reads the change and connected code; reports concrete regressions and verification gaps. |
| `patchproof-fix` | “Fix this bug and show that it works.” | Makes a focused correction and checks the relevant behavior. |
| `patchproof-handoff` | “Prepare a maintainer handoff.” | Summarizes what changed, what ran, and what remains uncertain. |

Tested with **Codex CLI 0.160.0 on Windows**. Desktop picker activation and other AI hosts are unverified. Installation from a synced Windows folder can fail; [INSTALL.md](INSTALL.md) covers the working local-folder route, updates, and removal.

AI review and fixes use **your Codex model, tools, permissions, and usage allowance**. PatchProof does not bundle a model or free AI access. It has no automatic execution hooks or background model calls.

## Record a check yourself

From the PatchProof folder, replace the example project path and filenames with your own. Choose a new output filename each time:

```sh
python scripts/receipt.py run --repo /path/to/project --watch app.py --watch test_app.py --out receipt.json -- python -B -m unittest
python scripts/receipt.py status --repo /path/to/project --receipt receipt.json --html report.html
```

Watching a whole folder or a pattern is usually easier than listing files:

```sh
python scripts/receipt.py run --repo /path/to/project --watch-dir tests --watch-glob 'src/**/*.py' --out receipt.json -- python -B -m pytest -q
```

Install it once and drop the `scripts/` prefix:

```sh
pipx install .        # or: pip install -e .
patchproof run --repo /path/to/project --watch-dir tests --out receipt.json -- python -B -m pytest -q
patchproof status --repo /path/to/project --receipt receipt.json
```

On Windows, use a quoted path such as `--repo 'C:\Projects\my-app'`. Repeat `--watch` for relevant source, tests, configuration, and lock files. Output paths are relative to the terminal's current folder; the check runs inside the named project.

Commands run with your normal account permissions. The recorder is **not a sandbox**. Unwatched files, environment changes, installed dependencies, and edits restored between snapshots are outside its coverage. Existing receipt and report files are never replaced. [All options, states, and limits →](docs/CLI.md)

## What has been checked

| Evidence | Scope |
|---|---|
| 27 Python tests | Git inventory, receipt validation, command outcomes, timeouts, file changes, watch expansion, and safe output handling. |
| 13 JavaScript tests | Receipt parsing, comparison states, watched-file scope, per-file labels, and summary output. |
| Controlled Codex integration | Installed all three skills; reproduced two failing tests, fixed the calculator without weakening tests, and detected a later edit. |
| Browser walkthrough | Saved examples, receipt import, actual file comparison, path search, export fallback, and theme switching. |

Read the [validation record](docs/VALIDATION.md) and [Codex integration evidence](docs/CODEX_TEST.md). These checks do not establish broad AI-review quality or comparative savings. A [paired evaluation plan](docs/EVALUATION.md) is included; no benchmark advantage is claimed.

## How the pieces fit

```text
Codex skills       → review, focused fixes, and factual handoffs
snapshot.py        → read-only inventory of local Git changes
receipt.py run     → watched hashes + chosen command + outcome
receipt.py status  → compare current files with the recorded inputs
Browser viewer    → open, compare, and explain receipts locally
web/              → the static project website
```

No third-party Python packages, build framework, database, or MCP server are required. See the [architecture and data boundaries](docs/ARCHITECTURE.md).

## Questions

**Does the website fix code?** No. Codex performs AI-assisted changes. The website displays receipts and compares fingerprints; it does not execute commands.

**Does anything leave my computer?** The helpers have no network client, and the viewer does not upload selected files. Your chosen check command may use the network. AI-host data policies apply separately when Codex reads your project. See [privacy](PRIVACY.md).

**Does it add watermarks?** PatchProof adds no watermark or attribution comments to your project files. Its viewer and reports carry PatchProof branding. Redistribution of PatchProof must preserve its MIT notice.

**Is this Ponytail?** No. [Ponytail](https://github.com/DietrichGebert/ponytail) inspired the focused-plugin format. PatchProof's code, skills, and symbol were authored separately. Its purpose is keeping check evidence tied to watched files. No Ponytail code or benchmark results are included.

## Develop and contribute

Python 3.11+, Git, and Node.js 24 are used by the development checks:

```sh
python -m unittest discover -s tests -v
node --test tests/test_viewer.mjs
python scripts/build.py
```

The build validates the manifests and creates a clean source ZIP under `outputs/`, excluding private logs and generated files. The GitHub Actions workflow is configured to run the checks on Windows and Linux; its presence alone is not evidence of a successful hosted run.

Bug reports with small reproductions, clearer explanations, and focused fixes are welcome. Read [contributing](CONTRIBUTING.md) and [security reporting](SECURITY.md) before sharing sensitive details.

[MIT license](LICENSE) · [Authors and acknowledgments](AUTHORS.md) · [Changelog](CHANGELOG.md)
