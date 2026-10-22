# Command reference

Requires Python 3.11+. Only the inventory command needs Git. Helpers use the Python standard library and do not require an API key. Run these commands from the PatchProof source folder.

## Teach any coding agent to record its checks

```sh
pp agents list                     # every supported host, and whether it is set up here
pp agents detect                   # which hosts this repository already uses
pp agents install claude codex cursor windsurf aider copilot cline roo gemini
pp agents install claude --dry-run
```

Writes the same short instruction into whichever rule file each host reads. Existing files are never replaced — the block is appended between `<!-- patchproof:start -->` and `<!-- patchproof:end -->`, and re-running is a no-op.

| Agent | File written |
|---|---|
| Claude Code | `CLAUDE.md` |
| Codex | `AGENTS.md` |
| Cursor | `.cursor/rules/patchproof.mdc` (with `alwaysApply: true`) |
| Windsurf | `.windsurf/rules/patchproof.md` |
| Cline | `.clinerules/patchproof.md` |
| Roo Code | `.roo/rules/patchproof.md` |
| Aider | `CONVENTIONS.md` |
| Gemini CLI | `GEMINI.md` |
| GitHub Copilot | `.github/instructions/patchproof.instructions.md` (with `applyTo: "**"`) |
| Anything else | `.patchproof/AGENTS.md` to point the host at |

The instruction is deliberately four lines: record checks with `pp verify`, re-check with `pp audit`, treat `changed_since_check` as "not passing", and never claim a check that was not run.

## Verify a command (the short way)

```sh
patchproof verify -- pytest -q
```

Watch sensible defaults, run the command, print one plain sentence, write a receipt. Watches `src/ lib/ app/ pkg/ tests/ test/ spec/`, any dependency manifest, and top-level source files. No flags required.

| Option | Meaning |
|---|---|
| `--repo` | Project root; defaults to the current folder. |
| `--watch` / `--watch-dir` / `--watch-glob` | Narrow the watch set; the defaults are used only when none are given. |
| `--out` | New receipt path; default `patchproof-receipt.json`. Never overwritten. |
| `--badge` | Also write a badge SVG for this result. |
| `--timeout` | Whole seconds, 1–3600; default 600. |
| `--quiet` | Print nothing on success. |

Exit code **0** when the check passed and the files still match, **1** for any other state, **2** for an input error.

## Audit a repository

```sh
patchproof audit
patchproof audit --glob '**/receipts/*.json' --json
```

Finds receipts (default `**/*receipt*.json`), re-checks each against the current files, prints one line per receipt, and exits **1** if any are out of date. This is the command to run in CI, or before trusting a green check you did not see run.

## Badge

```sh
patchproof badge --receipt patchproof-receipt.json --out pp.svg
```

Writes a self-contained SVG reading `up to date`, `out of date`, `failing` or `unknown`. A stale receipt can never produce a passing badge. The exit code follows the receipt's state.

### Publish it from CI

```yaml
- uses: Parthiv-kota/patchproof/badge@v0.2.0
  with:
    command: pytest -q          # required
    branch: patchproof-badges   # where the SVG is committed
    path: badge.svg             # file name inside that branch
    label: check                # left-hand text
    watch-dir: src,tests        # optional; defaults to the usual trees
```

The action runs the check, renders the badge, and commits it to the badge branch only when the SVG changed. It also writes `state` and `badge-url` as outputs and renders the badge into the job summary. The receipt is uploaded as an artifact whether the check passed or failed, so a failing run produces a **failing** badge rather than leaving the last green one in place.

## Record a command

```sh
python scripts/receipt.py run --repo /path/to/project --watch app.py --watch test_app.py --out receipt.json -- python -B -m unittest
```

On Windows, replace `/path/to/project` with a quoted path such as `'C:\Projects\my-app'`.

| Option | Meaning |
|---|---|
| `--repo` | Existing project root; the command runs here. |
| `--watch` | Existing file relative to that root. Repeat for each input. Use forward slashes. |
| `--watch-dir` | Existing folder relative to that root; watches every regular file inside it. Repeatable. |
| `--watch-glob` | Project-relative glob such as `'src/**/*.py'` or `'tests/test_*.py'`. Repeatable. |
| `--out` | New receipt JSON path. Its parent folder must exist. |
| `--timeout` | Whole seconds, 1–3600; default 120. |
| `--` | Separates recorder options from the executable and its arguments. |

Output paths are relative to your terminal's current directory, not `--repo`. Paths containing spaces must be quoted. The command is launched directly without a shell. Shell operators such as pipes or `&&` are not interpreted. Direct `.bat`, `.cmd`, and `.ps1` executables are rejected. Use an appropriate executable for a trusted check.

At least one of `--watch`, `--watch-dir` or `--watch-glob` is required. Directory and glob expansion skips `.git`, `.hg`, `.svn`, `node_modules`, virtual environments, caches, and `dist`/`build` folders, follows no symbolic links, and is resolved once before the command runs. Expansion that matches nothing, or more than 2,000 files, is an error rather than a partial receipt.

```sh
# One folder and one pattern instead of dozens of --watch flags
patchproof run --repo . --watch-dir tests --watch-glob 'src/**/*.py' --out receipt.json -- python -B -m pytest -q
```

The recorder hashes watched files before and after execution. Standard output and error remain in your terminal; the receipt does not capture them. It stores command arguments, outcome, start time, duration, and hashes. Keep credentials out of arguments.

Commands run with your normal account permissions and can modify files or use the network. PatchProof is not an execution sandbox. Timeout cleanup targets the launched process tree; detached children may escape it.

## Inspect freshness

```sh
python scripts/receipt.py status --repo /path/to/project --receipt receipt.json
python scripts/receipt.py status --repo /path/to/project --receipt receipt.json --html report.html
```

`--html` optionally writes a new self-contained report. A saved report describes the time it was generated; it does not update itself. Run `status` again after edits. Existing receipt/report files are never overwritten.

| State | Meaning | Next step |
|---|---|---|
| `current_passed` | Exit zero; before, after, and current watched bytes match. | Review whether the command and watched scope are sufficient. |
| `current_failed` | The command exited nonzero; watched bytes still match. | Investigate the failure. |
| `current_error` | The command could not be launched. | Check the executable and environment. |
| `current_timed_out` | The command exceeded its time limit. | Investigate the timeout before choosing a new limit. |
| `changed_since_check` | Current watched files differ from the recorded after snapshot. | Run a new check and write a new receipt. |
| `changed_during_check` | Watched inputs changed between the before/after snapshots. | Inspect the mutation and rerun on stable inputs. |
| `snapshot_unavailable` | The after snapshot could not be collected. | Resolve inaccessible or invalid inputs and rerun. |

If several problems apply, a changed-during-check or unavailable snapshot takes precedence over later freshness. Deleted watched files count as changes when comparing current files.

For both `run` and `status`, the process exit code is **0** for `current_passed`, **1** for another check state, and **2** for an input/tool error. It is not a direct passthrough of the child command's exit code; that value is stored in the receipt.

### Limits that matter

- Watch 1–2,000 explicit files, at most 64 MiB of total content. Directories, symbolic links, absolute paths, and parent traversal are rejected.
- Receipt JSON input is limited to 2 MiB.
- Include relevant source, tests, configuration, and lock files yourself. New/unwatched files, installed dependency contents, environment variables, and remote services are not tracked automatically.
- Hashing uses before/after samples, not an atomic filesystem snapshot. Changes restored between samples can go undetected.
- Receipts are editable and unsigned. They do not authenticate the author or prove a command was honestly recorded by someone else.

## Inventory Git changes

```sh
python scripts/snapshot.py --repo /path/to/repository
python scripts/snapshot.py --repo /path/to/repository --scope staged --max-files 200
```

Use the repository root of a Git repository with an initial commit.

| Option | Meaning |
|---|---|
| `--scope working` | Default: tracked working-tree contents compared with HEAD, including the net effect of staged and unstaged changes. |
| `--scope staged` | Index compared with HEAD. Later unstaged edits are excluded. |
| `--max-files` | Maximum reported entries, 1–2,000; default 200. This bounds the report, not Git's own memory use. |

The inventory returns changed-file counts, line counts where available, binary flags, untracked paths, and review hints. Renames appear as a deletion and an addition. Ignored files are excluded; submodule contents are not expanded. Review hints are path heuristics, not detected bugs.

This helper reads Git metadata without contacting remotes, returning source bodies, changing the repository, or executing project tests. Its output always says `verification: not_run`. It is neither a secret scanner nor a verification result. Filenames themselves may be sensitive.

## Demo, viewer, and package

```sh
python scripts/demo.py
python -m http.server 8790 --bind 127.0.0.1
python scripts/build.py
```

The demo creates a unique folder under `outputs/`. The server exposes this source folder only on loopback; visit <http://127.0.0.1:8790/site/> and stop the server with Ctrl+C. The viewer compares files and never executes test commands. If folder selection or browser hashing is unavailable, use `receipt.py status` instead.

The build validates plugin metadata and writes `outputs/PatchProof-v0.2.0.zip`. It replaces that generated archive on later builds, but never edits your receipts. Private development logs, generated outputs, caches, and internal publishing notes are excluded.
