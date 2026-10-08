# Install and try PatchProof

Download the repository source ZIP with **Code → Download ZIP**, or use a source archive attached to a release. Extract it before continuing. Keep the hidden `.agents` and `.codex-plugin` directories. A normal local folder outside OneDrive is recommended on Windows.

## Without an AI host

Requires Python 3.11+. Git is required only for the change-inventory helper. Node.js is required only to run the website's automated tests; the website itself runs in a browser.

From the extracted project folder (it may be named `patchproof-main`):

```powershell
python scripts/demo.py
python -m http.server 8790 --bind 127.0.0.1
```

Open <http://127.0.0.1:8790/site/> for the receipt viewer. Keep this terminal running. The saved demo snapshots are included. The viewer can import a receipt JSON and compare the watched files from a selected project folder, without uploading those files. Do not expose this simple development server to the public internet.

Follow the [calculator walkthrough](examples/README.md) to compare real files, or read the [command reference](docs/CLI.md) to record checks for your own project. If port 8790 is already in use, choose another unused port in both the server command and URL. Stop the server with Ctrl+C.

## Codex local plugin

Tested with Codex CLI 0.160.0 on Windows. Sign in to Codex normally before using its AI workflows. No separate PatchProof API key is required. Your Codex account's normal usage limits apply.

1. Extract the source archive to a normal local folder, such as `C:\Projects\patchproof`. Keep hidden directories such as `.agents` and `.codex-plugin`.
2. In that folder, register and install the local plugin:

```powershell
codex plugin marketplace add .
codex plugin add patchproof@patchproof-local
codex plugin list --marketplace patchproof-local --json
```

3. Start a fresh Codex session in the project you want to review. Ask:

> Use PatchProof to review my changes, explain any bugs in plain English, and record the checks you run. Ask before publishing anything.

The three bundled skills are `patchproof-review`, `patchproof-fix`, and `patchproof-handoff`. The model uses the host's normal tools and permissions. The plugin does not bypass approvals or provide its own model.

If an older CLI does not support these commands, use the local marketplace installation flow supported by that host. See [OpenAI's plugin packaging guidance](https://developers.openai.com/plugins/build/plugins). In the desktop app, a restart or new chat may be needed for discovery. Desktop picker activation has not been verified for this release.

### Windows folder access error

In the development test, Codex could register the OneDrive project but could not copy its plugin files. A clean ZIP extracted outside the synced folder installed successfully. If you hit the same issue, extract to a regular local folder and register that directory. Avoid registering two different sources under the same `patchproof-local` marketplace name. Remove the old catalog with `codex plugin marketplace remove patchproof-local` before registering the replacement you intend to use.

### Updating a local installation

Update the source folder registered by your marketplace, then reinstall/refresh it using your host's supported flow. Do not edit files inside Codex's plugin cache. Verify the loaded version and start a new session after updates.

### Removing

Use your host's plugin removal UI, or inspect `codex plugin remove --help` for your CLI version. Removing the local marketplace is a separate operation. No GitHub publication is needed for installation or testing.
