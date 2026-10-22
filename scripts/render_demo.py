#!/usr/bin/env python3
"""Render the 12-second PatchProof demo as SVG frames and a GIF.

The output is generated from a real `patchproof verify` / `patchproof audit`
run against a scratch project, so the text on screen is what the tool actually
printed. Nothing here is hand-written terminal cosplay.

Usage (development only, needs Pillow):
    python scripts/render_demo.py            # writes web/demo.gif
    python scripts/render_demo.py --frames   # also writes web/frames/*.svg
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
W, H = 1080, 620
BG, TEXT, DIM, GREEN, AMBER, MINT = "#0d1b21", "#dff3ec", "#7f9c98", "#5fe0b6", "#f2b46b", "#65e4c2"

SCENES = [
    (2000, "agent", [
        ("$", " codex \"fix the rounding bug in cart\"", "cmd"),
        ("", "  edited src/cart.py", "dim"),
        ("", "  ran: pytest -q", "dim"),
        ("", "  1 passed in 0.02s", "dim"),
        ("", "✔ Done — tests pass.", "ok"),
    ]),
    (2200, "verify", [
        ("$", " pp verify -- pytest -q", "cmd"),
        ("", "CHECK PASSED. 2 watched files unchanged.", "ok"),
        ("", "receipt: patchproof-receipt.json", "dim"),
    ]),
    (2000, "edit", [
        ("$", " # two hours later…", "cmd"),
        ("", "  edited src/cart.py", "dim"),
        ("", "  \"done, tests still pass\"", "dim"),
    ]),
    (3200, "audit", [
        ("$", " pp audit", "cmd"),
        ("", "   changed_since_check   patchproof-receipt.json", "bad"),
        ("", "   1 receipt, 1 out of date.", "bad"),
    ]),
]

COLORS = {"cmd": MINT, "dim": DIM, "ok": GREEN, "bad": AMBER}


def scene_svg(lines, caption):
    rows = []
    y = 190
    for prompt, text, kind in lines:
        colour = COLORS[kind]
        rows.append(
            f'<text x="64" y="{y}" font-family="ui-monospace,Menlo,Consolas,monospace" '
            f'font-size="27" fill="{colour}">{escape(prompt)}</text>'
            f'<text x="{64 + 17 * len(prompt)}" y="{y}" '
            f'font-family="ui-monospace,Menlo,Consolas,monospace" font-size="27" fill="{colour}">{escape(text)}</text>'
        )
        y += 64
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" rx="22" fill="{BG}"/>
<circle cx="42" cy="40" r="7" fill="#f2635f"/><circle cx="68" cy="40" r="7" fill="#f2c14e"/><circle cx="94" cy="40" r="7" fill="#5fd38d"/>
<text x="{W - 40}" y="48" text-anchor="end" font-family="ui-monospace,Menlo,Consolas,monospace" font-size="20" fill="{DIM}">{escape(caption)}</text>
<line x1="0" y1="72" x2="{W}" y2="72" stroke="#1d333a"/>
{''.join(rows)}
<text x="64" y="{H - 40}" font-family="system-ui,sans-serif" font-size="19" fill="{DIM}">patchproof · your test passed, prove it still does</text>
</svg>'''


def escape(value):
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def real_run():
    """Produce the real verify/audit output the frames display."""
    work = Path(tempfile.mkdtemp(prefix="pp-demo-"))
    try:
        (work / "src").mkdir()
        (work / "tests").mkdir()
        (work / "src/cart.py").write_text("def total(items):\n    return sum(items)\n", encoding="utf-8")
        (work / "tests/test_cart.py").write_text(
            "from src.cart import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n", encoding="utf-8")
        verify = subprocess.run(
            [sys.executable, "-m", "patchproof.cli", "verify", "--out", "patchproof-receipt.json",
             "--", sys.executable, "-m", "pytest", "-q"],
            cwd=work, capture_output=True, text=True)
        (work / "src/cart.py").write_text(
            "def total(items):\n    return sum(i['price'] for i in items)\n", encoding="utf-8")
        audit = subprocess.run([sys.executable, "-m", "patchproof.cli", "audit"],
                               cwd=work, capture_output=True, text=True)
        return (work, verify.stdout.strip().splitlines(), audit.stdout.strip().splitlines())
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv):
    _, verify_lines, audit_lines = real_run()
    scenes = json.loads(json.dumps(SCENES))
    if verify_lines:
        scenes[1][2][1] = ("", verify_lines[0], "ok")
    if audit_lines:
        scenes[3][2][1] = ("", "   " + audit_lines[0].strip(), "bad")
        scenes[3][2][2] = ("", "   " + audit_lines[-1].strip(), "bad")

    frames_dir = WEB / "frames"
    if "--frames" in argv:
        frames_dir.mkdir(exist_ok=True)
        for index, (_, name, lines) in enumerate(scenes):
            (frames_dir / f"{index + 1}-{name}.svg").write_text(scene_svg(lines, "patchproof"), encoding="utf-8")

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow is not installed; SVG frames are written but no GIF.", file=sys.stderr)
        return 1

    def font(size, bold=False):
        for name in (["DejaVuSansMono-Bold.ttf", "DejaVuSansMono.ttf"] if bold else ["DejaVuSansMono.ttf"]):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    mono, mono_small, label = font(31), font(22), font(20)
    images = []
    for duration_ms, name, lines in scenes:
        image = Image.new("RGB", (W, H), BG)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle([0, 0, W - 1, H - 1], radius=22, fill=BG)
        for x, colour in ((42, "#f2635f"), (68, "#f2c14e"), (94, "#5fd38d")):
            draw.ellipse([x - 7, 33, x + 7, 47], fill=colour)
        draw.line([0, 72, W, 72], fill="#1d333a")
        y = 176
        for prompt, text, kind in lines:
            colour = COLORS[kind]
            draw.text((64, y), prompt + text, font=mono, fill=colour)
            y += 64
        draw.text((64, H - 52), "patchproof · your test passed, prove it still does", font=label, fill=DIM)
        images.append((image, duration_ms))

    gif = WEB / "demo.gif"
    frames = [im for im, _ in images]
    durations = [d for _, d in images]
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print(f"wrote {gif} ({gif.stat().st_size // 1024} KB, {len(frames)} frames)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
