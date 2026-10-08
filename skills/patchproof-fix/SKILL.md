---
name: patchproof-fix
description: Fix a concrete bug with a focused change and regression evidence. Use when the user asks PatchProof to fix a reported failure or implement a verified review finding.
---

# PatchProof fix

1. Identify the requested failure and expected behavior. Read repository guidance and relevant code. Preserve unrelated user work.
2. Reproduce the bug where feasible. Record whether it was observed, inferred from source, or reported but unconfirmed. Do not write a test that merely duplicates the proposed implementation.
3. Look for an existing function, type or supported platform capability that fits. Choose the smallest understandable change that meets the requirement. Do not prefer clever brevity over readable, correct behavior.
4. Make the correction within the user's authorized scope. Preserve validation, permissions, error behavior and accessibility. Do not perform broad cleanup alongside an unrelated fix.
5. Run checks that exercise the changed behavior, including the previously failing case and relevant boundary cases. If a check fails, investigate it; do not mark it passed or silently remove coverage. Run repository-required checks where applicable.
6. Review the final diff for accidental scope, generated files and secret material. Use `scripts/snapshot.py` at the plugin root for metadata if useful; its output is not a correctness score.
7. Explain what changed, what now works, the actual verification results and unresolved limits. Include a reusable regression test when the risk warrants it.

No automatic commits, pushes, external messages, deployments, model calls or dependency installations are authorized by this skill. Follow the user's existing authorization and host permission policy; do not add redundant approval steps to routine local edits.

When a durable local check record helps, use the receipt workflow described in `../patchproof-review/SKILL.md`. Watch the relevant source and test inputs explicitly, and recheck the receipt after any later edits. Explain unwatched inputs and never present a passing command as a guarantee.
