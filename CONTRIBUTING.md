# Contributing to PatchProof

Help users tell a current, scoped check result from an old or incomplete one.

## Before changing code

- Describe the concrete problem and a reproducible example.
- Keep fixes focused. Preserve existing user files and permission boundaries.
- Never add telemetry, remote uploads, automatic dependency installation, or shell execution to the viewer without an explicit design discussion.
- Do not claim security, correctness, token savings or host compatibility without evidence.

## Local checks

```powershell
python -m unittest discover -s tests -v
node --test tests/test_viewer.mjs
python scripts/build.py
```

For UI changes, serve the project locally and verify receipt import, current/stale states, invalid input, search, export, keyboard access, and narrow layouts. Record what you actually tested. Test the Codex integration in a disposable repository if a skill or helper contract changes.

## Pull requests

Explain the triggering behavior, what changes for users, the checks you ran, and anything unverified. Add a focused regression test where it protects meaningful behavior. Do not add fabricated adoption metrics, unsupported performance claims, or unrelated formatting changes.

AI assistance is welcome. You remain responsible for reviewing the result, checking source licenses and running appropriate validation. Disclose material AI assistance in your pull request; do not submit credentials, private logs or third-party source without permission.

## Community

Be respectful and specific. Discuss code and evidence rather than attacking people. Harassment, discrimination, credential disclosure and spam are not welcome. Maintainers may moderate participation and close off-topic or abusive threads.
