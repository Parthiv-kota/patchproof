"""Run an explicitly selected check and track whether its watched files change."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import signal
import subprocess
import sys
import time

MAX_FILES = 2000
MAX_BYTES = 64 * 1024 * 1024


class ReceiptError(Exception):
    pass


SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
             ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", ".idea", ".vscode"}


def _relative_files(root, base):
    """Yield project-relative POSIX paths for every regular file under base."""
    for path in sorted(base.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        yield relative.as_posix()


def expand_watches(root, names=(), dirs=(), patterns=()):
    """Turn explicit paths, directories and globs into a validated, sorted watch list."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ReceiptError("The project directory does not exist.")
    found = set(names)
    for name in dirs:
        target = root / name
        if not target.is_dir():
            raise ReceiptError("Watch directories must exist inside the project: " + str(name))
        found.update(_relative_files(root, target))
    for pattern in patterns:
        if PurePosixPath(pattern).is_absolute() or ".." in PurePosixPath(pattern).parts:
            raise ReceiptError("Watch patterns must stay inside the project.")
        for path in root.glob(pattern):
            relative = path.relative_to(root)
            if any(part in SKIP_DIRS for part in relative.parts) or path.is_symlink() or not path.is_file():
                continue
            found.add(relative.as_posix())
    if not found:
        raise ReceiptError("No files matched. Check --watch, --watch-dir and --watch-glob.")
    if len(found) > MAX_FILES:
        raise ReceiptError(f"Watch selection matched {len(found)} files; the limit is {MAX_FILES}.")
    return sorted(found)


def fingerprint(root, names, allow_missing=False):
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or not 1 <= len(names) <= MAX_FILES:
        raise ReceiptError("Select between 1 and 2000 files in a project directory.")
    result, total = {}, 0
    for name in sorted(set(names)):
        if not isinstance(name, str) or not name or "\\" in name or ":" in name:
            raise ReceiptError("Use project-relative file paths with forward slashes.")
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or rel.as_posix() != name:
            raise ReceiptError("Watched paths must stay inside the project.")
        path = root.joinpath(*rel.parts)
        if any(p.is_symlink() for p in [path, *path.parents] if p != root and p.is_relative_to(root)):
            raise ReceiptError("Symbolic links cannot be watched in this version.")
        if not path.resolve().is_relative_to(root):
            raise ReceiptError("Watched paths must stay inside the project.")
        if not path.exists() and allow_missing:
            result[name] = None
            continue
        if not path.is_file():
            raise ReceiptError("Every watched path must be an existing regular file.")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                total += len(block)
                if total > MAX_BYTES:
                    raise ReceiptError("Watched files exceed the 64 MiB total limit.")
                digest.update(block)
        result[name] = digest.hexdigest()
    return result


def run_check(root, names, command, timeout=120):
    if not command or not all(isinstance(a, str) and a for a in command):
        raise ReceiptError("Provide an explicit executable and its arguments.")
    if Path(command[0]).suffix.lower() in {".bat", ".cmd", ".ps1"}:
        raise ReceiptError("Use an executable directly, such as python.exe or node.exe.")
    if not 1 <= timeout <= 3600:
        raise ReceiptError("Timeout must be between 1 and 3600 seconds.")
    before = fingerprint(root, names)
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    status, code = "error", None
    options = {"start_new_session": True} if os.name != "nt" else {}
    try:
        # Output stays in the caller's terminal; it is never stored in a receipt.
        process = subprocess.Popen(command, cwd=Path(root).resolve(), shell=False, **options)
        try:
            code = process.wait(timeout=timeout)
            status = "passed" if code == 0 else "failed"
        except subprocess.TimeoutExpired:
            if os.name == "nt":
                system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
                subprocess.run([str(system_root / "System32/taskkill.exe"), "/PID", str(process.pid), "/T", "/F"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            if process.poll() is None:
                process.kill()
            process.wait(timeout=10)
            status = "timed_out"
    except OSError:
        status = "error"
    try:
        after = fingerprint(root, names, allow_missing=True)
    except (ReceiptError, OSError):
        after = None
    return {"schema_version": 1, "started_at": started,
            "duration_seconds": round(time.monotonic() - tick, 3),
            "command": command, "exit_code": code, "check_status": status,
            "before": before, "after": after,
            "limits": "Only the listed files are watched. Exit zero does not prove correctness, security, or test coverage. Receipts are editable local records, not signed attestations."}


def inspect_receipt(root, receipt):
    try:
        if receipt["schema_version"] != 1 or receipt["check_status"] not in {"passed", "failed", "error", "timed_out"}:
            raise ValueError()
        before, after = receipt["before"], receipt["after"]
        if not isinstance(before, dict) or not before:
            raise ValueError()
        for value in before.values():
            if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError()
        if after is not None and (not isinstance(after, dict) or set(before) != set(after)):
            raise ValueError()
        if receipt["check_status"] == "passed" and receipt["exit_code"] != 0:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise ReceiptError("Invalid or inconsistent receipt.") from None
    current = fingerprint(root, list(before), allow_missing=True)
    changed = sorted(name for name in before if before[name] != current[name])
    if after is None:
        state = "snapshot_unavailable"
    elif before != after:
        state = "changed_during_check"
    elif current != after:
        state = "changed_since_check"
    else:
        state = "current_" + receipt["check_status"]
    return {"state": state, "changed_files": changed, "watched_count": len(before),
            "check_status": receipt["check_status"]}


DEFAULT_PREFIXES = ("src/", "lib/", "app/", "pkg/", "tests/", "test/", "spec/")
DEFAULT_SUFFIXES = (".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb",
                    ".java", ".kt", ".cs", ".php", ".c", ".h", ".cpp", ".swift", ".ex", ".exs",
                    ".toml", ".ini", ".cfg", ".lock", ".json", ".yaml", ".yml", ".lockfile")


def default_watches(root):
    """Everything PatchProof watches when the user names nothing.

    Source and test trees plus dependency manifests. Deliberately chatty: a
    check that silently watched too little would report freshness it cannot
    know about, which is the failure this tool exists to prevent.
    """
    root = Path(root).resolve(strict=True)
    found = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        name = relative.as_posix()
        if name.startswith(DEFAULT_PREFIXES) or relative.name in DEPENDENCY_MANIFESTS:
            found.append(name)
        elif len(relative.parts) == 1 and path.suffix in DEFAULT_SUFFIXES:
            found.append(name)
    if len(found) > MAX_FILES:
        raise ReceiptError(f"Default watch selection matched {len(found)} files; the limit is {MAX_FILES}. Use --watch-dir to narrow it.")
    return sorted(found)


DEPENDENCY_MANIFESTS = {"package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
                        "pyproject.toml", "requirements.txt", "poetry.lock", "uv.lock",
                        "go.mod", "go.sum", "Cargo.toml", "Cargo.lock", "Gemfile",
                        "Gemfile.lock", "composer.json", "pom.xml", "build.gradle"}

BADGE_COLORS = {"up_to_date": "#17634e", "failing": "#b45309",
                "out_of_date": "#b45309", "unknown": "#526066"}


def badge_svg(state, label="check"):
    """A self-contained SVG badge. `state` is a resolve_state() value.

    Character widths are measured, not guessed, so the two halves never overlap
    and the label is never clipped.
    """
    if state == "current_passed":
        word = "up to date"
    elif state in {"current_failed", "current_error", "current_timed_out"}:
        word = "failing"
    elif state in {"changed_since_check", "changed_during_check"}:
        word = "out of date"
    else:
        word = "unknown"
    colour = BADGE_COLORS[word.replace(" ", "_")]

    def text_width(value):
        # Verdana at 11px: digits and capitals are widest, so budget per glyph.
        return sum(8.2 if ch.isupper() or ch.isdigit() else 7.0 for ch in value)

    left = int(round(text_width(label))) + 14
    right = int(round(text_width(word))) + 14
    total = left + right
    label_x = left / 2
    word_x = left + right / 2
    return ("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{total}\" height=\"20\" "
            "role=\"img\" aria-label=\"{label}: {word}\">"
            "<title>{label}: {word}</title>"
            "<linearGradient id=\"s\" x2=\"0\" y2=\"100%\">"
            "<stop offset=\"0\" stop-color=\"#bbb\" stop-opacity=\".1\"/>"
            "<stop offset=\"1\" stop-opacity=\".1\"/></linearGradient>"
            "<clipPath id=\"r\"><rect width=\"{total}\" height=\"20\" rx=\"3\" fill=\"#fff\"/></clipPath>"
            "<g clip-path=\"url(#r)\">"
            "<rect width=\"{left}\" height=\"20\" fill=\"#152b35\"/>"
            "<rect x=\"{left}\" width=\"{right}\" height=\"20\" fill=\"{colour}\"/>"
            "<rect width=\"{total}\" height=\"20\" fill=\"url(#s)\"/></g>"
            "<g fill=\"#fff\" text-anchor=\"middle\" "
            "font-family=\"Verdana,DejaVu Sans,Geneva,sans-serif\" font-size=\"11\">"
            "<text x=\"{label_x:.1f}\" y=\"14\" fill-opacity=\".85\">{label}</text>"
            "<text x=\"{word_x:.1f}\" y=\"14\">{word}</text></g></svg>").format(
        total=total, label=html.escape(label, quote=True), word=html.escape(word, quote=True),
        left=left, right=right, colour=colour, label_x=label_x, word_x=word_x)


def summarise(result, receipt):
    """One human paragraph. Never claims more than the state supports."""
    state, changed = result["state"], result["changed_files"]
    watched = result["watched_count"]
    if state == "current_passed":
        return f"CHECK PASSED. {watched} watched file(s) unchanged since the run."
    if state == "changed_since_check":
        first = ", ".join(changed[:3]) + (f" (+{len(changed) - 3} more)" if len(changed) > 3 else "")
        return (f"STALE. {len(changed)} of {watched} watched file(s) changed since that check "
                f"passed: {first}. The recorded pass does not describe the current code.")
    if state == "changed_during_check":
        return "UNRELIABLE. Watched files changed while the command was running; rerun on stable inputs."
    if state == "current_failed":
        return f"CHECK FAILED with exit code {receipt.get('exit_code')}. Watched files still match that run."
    if state == "current_timed_out":
        return "CHECK TIMED OUT. The command did not finish inside its limit."
    if state == "current_error":
        return "CHECK DID NOT START. No verification was recorded."
    return "UNKNOWN. The after-check snapshot was unavailable, so freshness cannot be established."


LABELS = {
    "snapshot_unavailable": ("Files could not be rechecked", "The after-check snapshot was unavailable. Inspect the watched files and run again."),
    "current_passed": ("Check passed", "The selected command exited successfully. The watched files still match."),
    "current_failed": ("Check failed", "The selected command failed. The watched files still match that run."),
    "changed_since_check": ("Check is out of date", "Watched files changed after this run. Run the check again."),
    "changed_during_check": ("Files changed during the check", "The before and after snapshots differ. Review the changes and run again."),
    "current_timed_out": ("Check timed out", "The command did not finish within its time limit."),
    "current_error": ("Check could not start", "No successful check result was recorded."),
}


def report_html(receipt, result):
    title, message = LABELS[result["state"]]
    escape = lambda value: html.escape(str(value), quote=True)
    rows = "".join("<li><code>" + escape(name) + "</code></li>" for name in receipt["before"])
    color = "#0f766e" if result["state"] == "current_passed" else "#9a3412"
    command = json.dumps(receipt.get("command", []), ensure_ascii=True)
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>PatchProof — {escape(title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f6f5;color:#172e32;font:17px/1.6 system-ui,sans-serif}}
main{{max-width:880px;margin:48px auto;padding:28px}}header{{display:flex;align-items:center;gap:12px;font-weight:750}}
.icon{{background:#153e43;color:#9af0d0;border-radius:12px;padding:8px 16px;font-size:28px}}
.tag{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#536a6e}}h1{{font-size:clamp(30px,6vw,46px);line-height:1.12;margin-bottom:16px}}
.card{{background:white;border:1px solid #d9e4e1;border-radius:18px;padding:26px;margin:24px 0;box-shadow:0 7px 22px #183d3806}}
.status{{color:{color};font-weight:700}}code{{font-size:14px;overflow-wrap:anywhere}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f6f5;padding:16px;border-radius:10px}}
.muted{{color:#536a6e}}footer{{font-size:14px}}ul{{padding-left:24px}}a{{color:#0f766e}}</style>
<main><header><span class="icon" aria-hidden="true">✓</span>PatchProof <span class="tag">Local check receipt</span></header>
<section class="card"><span class="status">{escape(result['state'].replace('_', ' ').upper())}</span>
<h1>{escape(title)}</h1><p>{escape(message)}</p><p class="muted">Evaluated when this report was generated. This HTML does not update itself.</p></section>
<section class="card"><h2>What actually ran</h2><pre>{escape(command)}</pre>
<p>Exit code: <strong>{escape(receipt.get('exit_code'))}</strong> · Duration: {escape(receipt.get('duration_seconds'))} seconds</p>
<p class="muted">Started {escape(receipt.get('started_at'))}</p><h2>Files watched ({result['watched_count']})</h2><ul>{rows}</ul></section>
<footer><strong>What this means:</strong> {escape(receipt.get('limits', 'Scope is limited to the listed files.'))}<p>No watched file contents or captured test output are included. Command arguments and filenames are included; review them before sharing.</p></footer></main></html>'''


def write_new(path, text):
    with Path(path).open("x", encoding="utf-8") as stream:
        stream.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run")
    run.add_argument("--repo", required=True, type=Path)
    run.add_argument("--watch", action="append", default=[], help="Project-relative file; repeat for every input")
    run.add_argument("--watch-dir", action="append", default=[], help="Project-relative folder; watches every file inside it")
    run.add_argument("--watch-glob", action="append", default=[], help="Project-relative glob such as 'src/**/*.py'")
    run.add_argument("--out", required=True, type=Path)
    run.add_argument("--timeout", type=int, default=120)
    run.add_argument("command", nargs=argparse.REMAINDER)
    status = sub.add_parser("status")
    status.add_argument("--repo", required=True, type=Path)
    status.add_argument("--receipt", required=True, type=Path)
    status.add_argument("--html", type=Path)
    verify = sub.add_parser("verify", help="Watch sensible defaults, run the command, report plainly")
    verify.add_argument("--repo", type=Path, default=Path("."))
    verify.add_argument("--watch", action="append", default=[])
    verify.add_argument("--watch-dir", action="append", default=[])
    verify.add_argument("--watch-glob", action="append", default=[])
    verify.add_argument("--out", type=Path, default=Path("patchproof-receipt.json"))
    verify.add_argument("--badge", type=Path, help="Write a badge SVG for this result")
    verify.add_argument("--timeout", type=int, default=600)
    verify.add_argument("--quiet", action="store_true")
    verify.add_argument("command", nargs=argparse.REMAINDER)
    audit = sub.add_parser("audit", help="Find receipts in a repo and report which are stale")
    audit.add_argument("--repo", type=Path, default=Path("."))
    audit.add_argument("--glob", default="**/*receipt*.json")
    audit.add_argument("--json", action="store_true")
    badge = sub.add_parser("badge", help="Render a badge SVG from an existing receipt")
    badge.add_argument("--repo", type=Path, default=Path("."))
    badge.add_argument("--receipt", required=True, type=Path)
    badge.add_argument("--out", required=True, type=Path)
    badge.add_argument("--label", default="check")
    args = parser.parse_args(argv)
    try:
        if args.action == "verify":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            if not command:
                raise ReceiptError("Name the command to verify, for example: verify -- pytest -q")
            watched = (expand_watches(args.repo, args.watch, args.watch_dir, args.watch_glob)
                       if (args.watch or args.watch_dir or args.watch_glob)
                       else default_watches(args.repo))
            if args.out.exists():
                raise ReceiptError("Choose a new receipt path; existing files are never replaced.")
            if not args.out.parent.is_dir():
                raise ReceiptError("The receipt output directory must already exist.")
            record = run_check(args.repo, watched, command, args.timeout)
            write_new(args.out, json.dumps(record, indent=2, ensure_ascii=True) + "\n")
            result = inspect_receipt(args.repo, record)
            if args.badge:
                write_new(args.badge, badge_svg(result["state"]))
            if not args.quiet:
                print(summarise(result, record))
                print(f"receipt: {args.out} · {len(watched)} file(s) watched · exit {record['exit_code']}")
            return 0 if result["state"] == "current_passed" else 1
        if args.action == "audit":
            root = Path(args.repo).resolve(strict=True)
            found, rows = sorted(root.glob(args.glob)), []
            for path in found:
                if path.stat().st_size > 2 * 1024 * 1024:
                    rows.append({"receipt": path.relative_to(root).as_posix(), "state": "current_error",
                                 "detail": "receipt too large to inspect"})
                    continue
                try:
                    record = json.loads(path.read_text(encoding="utf-8"))
                    result = inspect_receipt(root, record)
                    rows.append({"receipt": path.relative_to(root).as_posix(),
                                 "state": result["state"], "changed": result["changed_files"],
                                 "command": record.get("command", [])})
                except (ReceiptError, OSError, ValueError, KeyError):
                    rows.append({"receipt": path.relative_to(root).as_posix(), "state": "current_error",
                                 "detail": "invalid receipt"})
            stale = [r for r in rows if r["state"] in {"changed_since_check", "changed_during_check"}]
            if args.json:
                print(json.dumps({"receipts": rows, "stale": len(stale)}, indent=2))
            else:
                if not rows:
                    print(f"No receipts found under {args.glob}. Run `verify` first.")
                for row in rows:
                    print(f"{row['state']:>22}  {row['receipt']}")
                if rows:
                    print(f"\n{len(rows)} receipt(s), {len(stale)} out of date.")
            return 0 if not stale else 1
        if args.action == "badge":
            if args.receipt.stat().st_size > 2 * 1024 * 1024:
                raise ReceiptError("Receipt is too large.")
            record = json.loads(args.receipt.read_text(encoding="utf-8"))
            result = inspect_receipt(args.repo, record)
            write_new(args.out, badge_svg(result["state"], args.label))
            print(f"badge: {args.out} ({result['state']})")
            return 0 if result["state"] == "current_passed" else 1
        if args.action == "run":
            if args.out.exists():
                raise ReceiptError("Choose a new receipt path; existing files are never replaced.")
            if not args.out.parent.is_dir():
                raise ReceiptError("The receipt output directory must already exist.")
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            if not (args.watch or args.watch_dir or args.watch_glob):
                raise ReceiptError("Watch at least one file with --watch, --watch-dir or --watch-glob.")
            watched = expand_watches(args.repo, args.watch, args.watch_dir, args.watch_glob)
            receipt = run_check(args.repo, watched, command, args.timeout)
            write_new(args.out, json.dumps(receipt, indent=2, ensure_ascii=True) + "\n")
        else:
            if args.receipt.stat().st_size > 2 * 1024 * 1024:
                raise ReceiptError("Receipt is too large.")
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        result = inspect_receipt(args.repo, receipt)
        if args.action == "status" and args.html:
            write_new(args.html, report_html(receipt, result))
        print(json.dumps(result, indent=2))
        return 0 if result["state"] == "current_passed" else 1
    except (ReceiptError, OSError, ValueError) as error:
        print("PatchProof could not complete: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
