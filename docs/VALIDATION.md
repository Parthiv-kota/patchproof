# Validation record

## Release preparation — 8 October 2026

Re-ran the existing suites on Windows with Python 3.14.7 and Node.js 24.21.0: **24 Python tests passed; 12 JavaScript tests passed**. The isolated calculator demo also completed its asserted failure → pass → stale sequence. No additional AI model session was launched for this release preparation.

The package build validates matching manifests, skill metadata, icon paths, archive integrity, and required documentation. Internal publishing notes, grant-readiness notes, generated outputs, and raw test logs are excluded from the clean source archive. The public README and command reference were checked against the implementation.

The new GitHub Actions configuration targets Python 3.11 and 3.14 on Windows and Linux, with Node.js 24. Hosted CI has not run yet. The configuration is not evidence that those environments passed.

Browser/Computer automation could not start during this release preparation because the app's Windows sandbox setup failed. The only website change in this pass was the footer wording; no fresh browser rendering or desktop plugin-picker check is claimed.

## Earlier functional and integration checks — 5 October 2026

The Python helper suite passes 24 tests on this Windows machine. It covers real Git changes, staged/working scope, binary and unusual paths, ignored/untracked files, scope limits, unchanged worktree/index, successful and failed subprocesses, timeout, missing executable, modifications during/after a check, deletion, invalid receipts/paths, HTML escaping, refusing output replacement and CLI exit codes.

The calculator demonstration runs an actual failing unittest, repairs the isolated fixture, runs a passing unittest, then edits it again and confirms the receipt becomes stale. All edits remain in a newly created demo folder. The intentionally failing demo test is expected behavior, not a failing PatchProof test.

The website core passes 12 JavaScript tests covering current, failed, stale, changed-during-check and unavailable snapshots; malformed receipts; invalid paths and hashes; incomplete after snapshots; and factual export scope. Browser verification covers the saved demo, real receipt import and comparison against the calculator fixture. Download delivery depends on the browser; exports also have an inline copyable fallback.

Package checks verify manifest identity/version consistency, skill front matter, local icon paths and ZIP members. They are structural checks, not a host compatibility certification.

Codex CLI 0.160.0 on Windows installed and enabled PatchProof from a clean local source copy. A fresh CLI session loaded all three installed skills and completed review, regression reproduction, focused fix, passing check, stale-receipt detection and handoff on a disposable calculator repository. See CODEX_TEST.md.

Not verified: desktop plugin-picker activation, Claude Code or other AI hosts, Linux/macOS execution, large repositories, adversarial filesystem races, escaped/detached process cleanup, broad model-review quality, security certification, adoption or token savings. The runner is not a sandbox. Fingerprinting is scoped to explicit files and takes before/after snapshots, not an atomic filesystem snapshot. User-editable receipts are not signed.
