"""patchproof: local check receipts for AI-assisted development."""
import importlib.util
import sys
from pathlib import Path

# The recording engine lives in scripts/receipt.py so it stays usable without an
# install. Expose it as patchproof.receipt for callers that do have one.
_ENGINE = Path(__file__).resolve().parents[1] / "scripts" / "receipt.py"
_spec = importlib.util.spec_from_file_location("patchproof.receipt", _ENGINE)
receipt = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("patchproof.receipt", receipt)
_spec.loader.exec_module(receipt)

__version__ = "0.2.0"
