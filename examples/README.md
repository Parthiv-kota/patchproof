# A real failure, a real pass, and an old result

This walkthrough uses only Python 3.11+ and a browser. No Codex session, API key, or model usage is needed.

## 1. Create the example

From the PatchProof source folder:

```sh
python scripts/demo.py
```

The first unittest fails on purpose. The script then fixes the addition function, runs a passing test, edits the function again, and checks the earlier receipt. A final `DEMO=.../index.html` line points to the finished reports.

Every run creates a unique `outputs/demo-.../` folder. The script changes only its own calculator fixture.

## 2. Open the three reports

Open the printed `index.html` in a browser. Take one card at a time:

1. **A bug is caught:** subtraction returns the wrong answer; the command fails.
2. **The fix passes:** addition works and the recorded command exits zero.
3. **Old results expire:** a later edit changes the watched bytes; the earlier passing result is stale.

These HTML reports are saved snapshots. They do not monitor your files.

## 3. Compare actual files in the viewer

```sh
python -m http.server 8790 --bind 127.0.0.1
```

Open <http://127.0.0.1:8790/site/#compare>. Choose `2-passed.json` from the new demo folder, then select that folder's `calculator` subfolder as the project root.

The viewer should show that the files changed since the check: the demo deliberately edited the calculator after recording the pass. Importing the JSON alone does not establish freshness; the file comparison is required.

Search for `calculator.py`, expand the command details, and use **Save summary**. If your browser blocks downloads, open the inline summary preview and copy it.

To create a new current pass, change the fixture's return expression back to `a + b`, then run a new check following [the command reference](../docs/CLI.md). Watch both `calculator.py` and `test_calculator.py`, and choose a new receipt filename. Import that new receipt and compare the same folder again.

Only the watched files are covered. A passing calculator test does not establish the correctness of another project.
