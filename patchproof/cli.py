"""Console entry point for the receipt recorder.

Thin wrapper so `pipx install .` provides a `patchproof` command. The
implementation stays in scripts/receipt.py, which is also usable directly.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from receipt import main  # noqa: E402

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
