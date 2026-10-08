# Security and privacy

PatchProof is an early local developer tool, not a sandbox or a security certification service.

- Selected check commands run with the invoking account's permissions and may access files or networks. Review commands before execution.
- Receipts are editable, unsigned JSON. Do not treat another person's receipt as trusted proof.
- Fingerprints cover only explicit files at sampled moments. Unwatched inputs, environments and changes restored between snapshots are not covered.
- Receipt arguments and paths may contain private information. Review them before sharing.
- The website reads selected files locally. Its viewer has no upload endpoint, analytics, or external scripts.
- The AI host is separate: its data handling and access policies apply when the plugin reads project context.

## Reporting a vulnerability

Do not open a public issue containing secrets, exploit details against someone else's project, or private logs. If the repository provides GitHub's **Report a vulnerability** option, use it for a private report. Otherwise open a minimal issue requesting a private contact channel, without the sensitive details. No dedicated security inbox or response-time guarantee is currently advertised.

Include the affected version, minimal synthetic reproduction, expected and actual behavior, and proposed mitigation if available. Never test against a third-party system without authorization.

Only the current preview is maintained; no long-term support commitment is made. See PRIVACY.md for data handling and docs/VALIDATION.md for test limitations.
