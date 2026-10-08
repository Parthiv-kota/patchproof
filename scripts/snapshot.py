"""Read-only change inventory. No network, content collection or test execution."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


class SnapshotError(Exception):
    pass


def git(repo, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-c", "core.quotePath=false",
                                 "-C", str(repo), *args], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise SnapshotError("Git could not complete the local metadata query.") from None
    if result.returncode:
        raise SnapshotError("Git metadata query failed. Use an accessible repository with an initial commit.")
    return result.stdout


def parse_numstat(raw):
    result = []
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        parts = entry.split(b"\t", 2)
        if len(parts) != 3:
            raise SnapshotError("Unexpected Git numstat data.")
        added, removed, path = parts
        binary = added == b"-" or removed == b"-"
        try:
            result.append({"path": path.decode("utf-8", errors="surrogateescape"),
                           "added": None if binary else int(added),
                           "removed": None if binary else int(removed), "binary": binary})
        except ValueError:
            raise SnapshotError("Unexpected Git line count.") from None
    return result


def review_areas(paths):
    hints = set()
    for path in paths:
        lower = path.lower().replace("\\", "/")
        if any(part in lower for part in ("auth", "permission", "session", "token")):
            hints.add("Check authentication and permission boundaries in relevant changed code.")
        if any(part in lower for part in ("migration", "schema", "database")):
            hints.add("Check persisted-data compatibility and failure recovery.")
        if Path(lower).name in {"package.json", "package-lock.json", "pyproject.toml", "requirements.txt", "cargo.lock", "go.mod"}:
            hints.add("Review dependency or packaging changes and reproducibility.")
        if lower.startswith(".github/"):
            hints.add("Inspect workflow permissions, triggers and secret handling.")
    return sorted(hints)


def snapshot(repo, scope="working", max_files=200):
    repo = Path(repo).resolve()
    if scope not in {"working", "staged"} or not 1 <= max_files <= 2000:
        raise SnapshotError("Choose working/staged scope and a file limit from 1 to 2000.")
    if not repo.is_dir():
        raise SnapshotError("Repository directory does not exist.")
    root = Path(os.fsdecode(git(repo, "rev-parse", "--show-toplevel").strip())).resolve()
    if root != repo:
        raise SnapshotError("Pass the repository root to avoid silently widening a subdirectory review.")
    revision = git(repo, "rev-parse", "--verify", "HEAD").decode("ascii").strip()
    args = ["diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--numstat", "-z"]
    if scope == "staged":
        args.append("--cached")
    entries = parse_numstat(git(repo, *args, "HEAD", "--"))
    untracked = [os.fsdecode(path) for path in git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if path]
    visible = entries[:max_files]
    return {
        "schema_version": 1, "scope": scope, "base_revision": revision,
        "tracked_changed_count": len(entries), "tracked_changes": visible,
        "tracked_truncated": len(entries) > max_files,
        "untracked_count": len(untracked), "untracked_paths": untracked[:max_files],
        "untracked_truncated": len(untracked) > max_files,
        "review_hints": review_areas([e["path"] for e in visible]),
        "verification": "not_run",
        "limits": ["Metadata only; source contents and correctness were not inspected.",
                   "Working scope compares tracked working-tree content with HEAD; staged scope compares the index with HEAD.",
                   "Renames appear as removal/addition. Ignored files are excluded; untracked files are listed, not inspected.",
                   "Path hints are heuristic review areas, not findings. File names may themselves be sensitive."]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--scope", choices=["working", "staged"], default="working")
    parser.add_argument("--max-files", type=int, default=200)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(snapshot(args.repo, args.scope, args.max_files), indent=2, ensure_ascii=True))
        return 0
    except SnapshotError as error:
        print(json.dumps({"error": str(error), "verification": "not_run"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
