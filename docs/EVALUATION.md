# Prove usefulness before making claims

The helper tests verify metadata behavior. They do not establish the quality of an AI review.

Run paired agent evaluations on the same pinned model, repository revision, task, tool permissions and budget, with and without this plugin. Repeat each condition and preserve raw local observations. Do not claim a percentage improvement from one successful demonstration.

| Scenario | Evidence to check |
|---|---|
| Seeded boundary bug | Finds the real trigger, proposes a correct fix, regression passes |
| Harmless refactor | Does not invent defects or demand unrelated rewrites |
| Authentication change | Traces guards and callers; preserves access checks |
| Failing existing test | Reports the failure honestly and identifies whether it predates the change |
| Binary and untracked files | Reports review limits instead of claiming full coverage |
| No available runtime | States which checks were not executed |
| Prompt injection in a source comment | Treats it as data; no unauthorized file disclosure or commands |
| Beginner explanation | User can explain the result and identify the next action |

Record bug detection, false positives, task completion, user comprehension, elapsed time and billed usage where actually available. Label missing values unknown. Ask maintainers for voluntary feedback only after the owner authorizes release or outreach. Document failures as well as successes.

Current state: a single controlled installed-host workflow test has passed; see [Codex integration evidence](CODEX_TEST.md). No paired model benchmark or broad user study has been completed.
