"""Console entry point for the read-only Git change inventory."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from snapshot import main  # noqa: E402

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
