"""Create three real local check receipts in an isolated calculator example."""
from pathlib import Path
import sys
import tempfile

from receipt import inspect_receipt, report_html, run_check, write_new
import json


def demo_report(record, state):
    return report_html(record, state).replace("<main>", '<main><p><a href="index.html">← Back to demo</a></p>', 1)


def main():
    root = Path(__file__).resolve().parents[1]
    output_root = root / "outputs"
    output_root.mkdir(exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="demo-", dir=output_root))
    project = folder / "calculator"
    project.mkdir()
    app = project / "calculator.py"
    check = project / "test_calculator.py"
    app.write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    check.write_text("import unittest\nfrom calculator import add\n\nclass CalculatorTest(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n", encoding="utf-8")
    # -B prevents bytecode reuse when this deliberately tiny fixture changes quickly.
    command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", ".", "-v"]
    watched = ["calculator.py", "test_calculator.py"]
    failed = run_check(project, watched, command)
    failed_state = inspect_receipt(project, failed)
    write_new(folder / "1-failed.html", demo_report(failed, failed_state))
    write_new(folder / "1-failed.json", json.dumps(failed, indent=2))
    app.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    passed = run_check(project, watched, command)
    passed_state = inspect_receipt(project, passed)
    write_new(folder / "2-passed.html", demo_report(passed, passed_state))
    write_new(folder / "2-passed.json", json.dumps(passed, indent=2))
    app.write_text("def add(a, b):\n    return a + b + 1\n", encoding="utf-8")
    stale_state = inspect_receipt(project, passed)
    write_new(folder / "3-outdated.html", demo_report(passed, stale_state))
    assert [s["state"] for s in [failed_state, passed_state, stale_state]] == ["current_failed", "current_passed", "changed_since_check"]
    index = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Try PatchProof</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f3f6f5;color:#173d42;font:17px/1.6 system-ui}main{max-width:980px;margin:40px auto;padding:28px}header{font-weight:750;font-size:21px;display:flex;align-items:center;gap:12px}img{width:45px}h1{font-size:clamp(32px,6vw,52px);line-height:1.12;max-width:760px}p{color:#526a6d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin:30px 0}.card{background:white;border:1px solid #d4e3df;border-radius:18px;padding:24px;display:flex;flex-direction:column}h2{font-size:22px}.number{font-size:12px;letter-spacing:.1em;text-transform:uppercase}a{color:#0f766e;font-weight:700;margin-top:auto;padding-top:20px}.note{border-left:3px solid #36ba97;padding:10px 20px}footer{font-size:14px;margin-top:28px}</style>
<main><header><img src="../../assets/icon.svg" alt="">PatchProof <span style="font-size:12px;font-weight:500">PRIVATE LOCAL DEMO</span></header>
<h1>The AI says it works.<br>See what was checked.</h1><p>Check receipts show what ran, which files were watched, and when a result is out of date.</p>
<div class="grid"><section class="card"><span class="number">01 · Real failing test</span><h2>A bug is caught</h2><p>The calculator subtracts instead of adding. Its test fails.</p><a href="1-failed.html">See the failed check →</a></section>
<section class="card"><span class="number">02 · Real passing test</span><h2>The fix passes</h2><p>The demo fixes addition, runs the test again, and records the file fingerprints.</p><a href="2-passed.html">See the passing check →</a></section>
<section class="card"><span class="number">03 · Real file change</span><h2>Old results expire</h2><p>The code changes again. PatchProof warns that the earlier pass no longer matches.</p><a href="3-outdated.html">See the outdated check →</a></section></div>
<div class="note"><strong>Try one step at a time.</strong><p>Start with the failed check, return here, then open the passing and outdated checks. These reports are saved snapshots from an actual local demo run.</p></div>
<footer>A passing command is not a guarantee of correct or secure software. Only explicitly watched files are tracked. No account, API key, or model is needed for this demo. Nothing was published.</footer></main></html>'''
    write_new(folder / "index.html", index)
    print("DEMO=" + str(folder / "index.html"))


if __name__ == "__main__":
    main()
