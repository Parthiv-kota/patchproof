"""Console entry points for patchproof.

Thin wrappers so `pipx install .` provides the `pp` / `patchproof` commands.
The recording engine stays in scripts/receipt.py, which is also usable directly;
the agent-host adapter lives in patchproof/agents.py.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import receipt as _receipt  # noqa: E402
from patchproof import agents as _agents  # noqa: E402

__all__ = ["main"]


def _agents_main(argv):
    parser = argparse.ArgumentParser(
        prog="pp agents",
        description="Write rule files so any coding agent records its checks with patchproof.")
    sub = parser.add_subparsers(dest="action", required=True)
    add = sub.add_parser("install", help="Write rule files for one or more agents")
    add.add_argument("agents", nargs="+", metavar="AGENT",
                     help=", ".join(sorted(_agents.AGENTS)))
    add.add_argument("--repo", type=Path, default=Path("."))
    add.add_argument("--dry-run", action="store_true")
    lst = sub.add_parser("list", help="Show every supported agent and whether it is installed here")
    lst.add_argument("--repo", type=Path, default=Path("."))
    det = sub.add_parser("detect", help="Show which agents this repository already uses")
    det.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        if args.action == "install":
            for agent, path, action in _agents.install(args.repo, args.agents, args.dry_run):
                print(f"{action:>18}  {path}  ({_agents.AGENTS[agent]['label']})")
            return 0
        if args.action == "detect":
            found = _agents.detect(args.repo)
            print(", ".join(found) if found else "no agent configuration found")
            return 0
        for row in _agents.status(args.repo):
            mark = "installed" if row["installed"] else "missing"
            print(f"{mark:>10}  {row['agent']:<10} {row['path']}  ({row['label']})")
        return 0
    except (_agents.AdapterError, OSError) as error:
        print("patchproof agents: " + str(error), file=sys.stderr)
        return 2


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["agents"]:
        return _agents_main(argv[1:])
    return _receipt.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
