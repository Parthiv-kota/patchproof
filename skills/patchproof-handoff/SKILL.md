---
name: patchproof-handoff
description: Prepare a factual maintainer handoff or local PR-description draft from completed work and observed verification. Use when the user requests a PatchProof handoff, review summary, or draft release evidence.
---

# PatchProof handoff

Read the actual final diff and check results from this task. Do not infer that a check ran from the presence of a test file or CI configuration. If older evidence may be stale, identify it and rerun only when authorized and useful.

Produce a concise local draft describing:

1. The concrete problem and resulting behavior.
2. The change's relevant scope, compatibility and migration effects.
3. Checks executed, their outcomes and source revision if known.
4. Remaining risks, untested integrations and work still required.

Use real metrics only. Separate current users, downloads and releases from aspirations. Never invent adoption, benchmark savings, contributor history, security certification, program eligibility or approval.

Follow any repository PR template. Exclude secrets and unnecessary personal data. Creating this draft does not authorize posting it, changing GitHub, applying for grants or publishing the plugin. If publication was already explicitly authorized, follow that authorization and the host's rules instead of asking redundant permission.
