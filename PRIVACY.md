# Local data handling

PatchProof has no analytics, network client, account system or remote storage. The metadata helper reads Git metadata from the explicitly named repository and writes JSON to standard output. It does not collect working-file bodies, invoke test commands or execute project hooks intentionally; external diff/text conversion and filesystem monitor hooks are disabled for its Git queries.

The separate receipt helper reads the explicitly watched files to compute SHA-256 fingerprints and runs the command you select. That command has normal user permissions and may access files, network or services according to its own behavior. PatchProof does not isolate it. The receipt stores command arguments, paths, hashes, timestamps and exit code locally; test output stays in the terminal and is not captured in the receipt. Avoid secrets in command arguments. HTML reports include the same metadata and are saved snapshots, not live checks.

The static website reads selected receipt JSON and watched files using browser file APIs. It hashes matching files locally and does not send their contents over the network. It stores selection and comparison state only in page memory. Reloading clears that state. Theme selection also stays in memory. Downloaded summaries remain wherever the browser saves them. The included demo uses synthetic calculator receipts, not private project data.

Skills ask the host agent to inspect relevant source and perform authorized checks. Data shared with the AI host follows that host's settings and policies; local helper execution does not mean the surrounding AI conversation is offline. Repository content and filenames can be confidential.

Keep reports local by default. Never include credentials or unnecessary personal data in handoffs. This plugin provides no security certification and does not automatically detect secrets.
