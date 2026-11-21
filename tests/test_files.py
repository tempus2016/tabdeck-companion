"""Static checks of the integration's files (no Home Assistant needed)."""

from __future__ import annotations

import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "custom_components" / "tabdeck"


def test_manifest():
    manifest = json.loads((COMP / "manifest.json").read_text())
    assert manifest["domain"] == "tabdeck"
    assert manifest["config_flow"] is True and manifest["single_config_entry"] is True
    assert manifest["requirements"] == []
    assert manifest["version"].count(".") == 2


def test_hacs_json():
    hacs = json.loads((ROOT / "hacs.json").read_text())
    assert hacs["name"] == "Tabdeck Companion"


def test_english_translation_matches_strings():
    assert json.loads((COMP / "strings.json").read_text()) == json.loads((COMP / "translations" / "en.json").read_text())


def test_every_module_compiles(tmp_path):
    for path in COMP.glob("*.py"):
        py_compile.compile(str(path), cfile=str(tmp_path / (path.name + "c")), doraise=True)
