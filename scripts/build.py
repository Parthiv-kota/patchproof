"""Validate package structure and create a clean source ZIP."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    overlay = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    for field in ["name", "version", "description", "author", "license"]:
        assert portable[field] == overlay[field], field
    interface = portable["extensions"]["com.openai"]["interface"]
    assert interface == overlay["interface"]
    assert 1 <= len(interface["shortDescription"]) <= 30
    assert overlay["skills"] == "./skills/"
    for field in ["logo", "composerIcon"]:
        asset = (ROOT / interface[field]).resolve()
        assert asset.is_relative_to(ROOT) and asset.is_file()
        svg = ET.parse(asset).getroot()
        assert svg.tag.endswith("svg") and svg.attrib["viewBox"] == "0 0 128 128"
    skills = list((ROOT / "skills").glob("*/SKILL.md"))
    assert len(skills) == 3
    for skill in skills:
        content = skill.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        front = content.split("---", 2)[1]
        assert re.search(r"^name: " + re.escape(skill.parent.name) + r"$", front, re.M)
        assert re.search(r"^description: .+", front, re.M)
    top = {"plugin.json", "README.md", "LICENSE", "PRIVACY.md", ".gitignore", "INSTALL.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "AUTHORS.md"}
    folders = {".codex-plugin", ".agents", ".github", "assets", "docs", "scripts", "skills", "tests", "site", "examples"}
    private_notes = {"docs/GITHUB_PUBLISHING_KIT.md", "docs/OSS_READINESS.md", "docs/INSPIRATION.md"}
    files = sorted(p for p in ROOT.rglob("*") if p.is_file()
                   and (p.relative_to(ROOT).as_posix() in top or p.relative_to(ROOT).parts[0] in folders)
                   and p.relative_to(ROOT).as_posix() not in private_notes
                   and "__pycache__" not in p.parts and p.suffix not in {".pyc", ".pyo"})
    assert all(not p.is_symlink() for p in files)
    marketplace = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
    assert marketplace["name"] == "patchproof-local"
    assert marketplace["plugins"][0]["source"]["path"] == "./"
    output = ROOT / f"outputs/PatchProof-v{portable['version']}.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for file in files:
            archive.write(file, "patchproof/" + file.relative_to(ROOT).as_posix())
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(files)
        assert all(name.startswith("patchproof/") and ".." not in Path(name).parts for name in archive.namelist())
        assert not any("patchproof/" + name in archive.namelist() for name in private_notes)
        assert "patchproof/AUTHORS.md" in archive.namelist()
        assert "patchproof/examples/README.md" in archive.namelist()
    print(f"Package structure validated. {len(files)} files. ZIP={output}")


if __name__ == "__main__":
    main()
