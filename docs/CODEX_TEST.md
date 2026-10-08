# Codex integration test

**Result: passed on Windows, 5 October 2026, Codex CLI 0.160.0.**

PatchProof was registered in a local marketplace, installed with Codex's plugin installer, and listed as installed and enabled. A fresh, bounded Codex CLI session discovered and read all three skills from the installed plugin cache: review, fix, and handoff. It used the installed Python helpers, not a substitute workspace implementation.

The test used a disposable Git repository containing an addition function and two existing tests. Its local change deliberately replaced addition with subtraction.

| Stage | Observed result |
|---|---|
| Review | Identified the subtraction regression in the changed function. |
| Reproduce | Both tests failed; receipt recorded command exit 1. |
| Fix | Restored addition; both tests passed; a new receipt recorded exit 0. |
| Freshness check | Matching files returned `current_passed`. |
| Later edit | A harmless source comment made the earlier receipt return `changed_since_check`. |
| Test preservation | Test-file hashes matched before and after; no tests were weakened. |
| Handoff | Reported actual results, watched scope, and limitations. |

An initial byte comparison with the Git baseline differed because of Windows CRLF versus LF. Normalized content matched; hashes confirmed that the test file stayed unchanged during the workflow. This was investigated rather than hidden.

Direct installation from the OneDrive-backed development directory failed with a Windows access error. Installing a clean ZIP copy from a normal local folder succeeded. The exact filesystem cause was not established. This workaround is documented in INSTALL.md.

This is a single controlled integration test, not a broad quality benchmark. It establishes Codex CLI discovery and operation on this fixture. Activation through the desktop plugin picker, other AI hosts, other operating systems, arbitrary repositories, and security certification have not been established by this test.

Raw local session logs are excluded from the release package. The public demonstration receipts contain only synthetic calculator metadata. The integration test itself did not upload, push, or submit anything.
