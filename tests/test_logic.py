"""Unit tests of the pure bookkeeping (logic.py); no Home Assistant needed."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parents[1] / "custom_components" / "tabdeck" / "logic.py"
_spec = importlib.util.spec_from_file_location("tabdeck_logic", _PATH)
logic = importlib.util.module_from_spec(_spec)
sys.modules["tabdeck_logic"] = logic
_spec.loader.exec_module(logic)


def test_ids_are_checked():
    assert logic.clean_id(" kitchen_tablet ", "browser_id") == "kitchen_tablet"
    for bad in ["", "a b", "x" * 65, None, "../etc", "<script>"]:
        with pytest.raises(logic.DeckError) as err:
            logic.clean_id(bad, "browser_id")
        assert err.value.code == "invalid_format"


def test_tabs_are_cleaned():
    assert logic.clean_tabs(["Home", " Home ", "", "  Lights\n", 3, "x" * 150]) == ["Home", "Lights", "3", "x" * 100]
    assert logic.clean_tabs("Home") == []
    assert len(logic.clean_tabs([f"t{i}" for i in range(300)])) == logic.MAX_TABS


def test_register_update_and_current():
    decks = logic.Decks()
    deck, created = decks.register("kitchen_tablet", "main", None, ["Home", "Cameras"], "Home")
    assert created and deck.browser_name == "Kitchen tablet" and deck.current == "Home"
    again, created = decks.register("kitchen_tablet", "main", "Kitchen", ["Home", "Cameras", "Lights"], "Lights")
    assert again is deck and not created
    assert deck.browser_name == "Kitchen" and deck.tabs == ["Home", "Cameras", "Lights"]
    decks.update("kitchen_tablet", "main", tab="Cameras")
    assert deck.current == "Cameras"
    decks.update("kitchen_tablet", "main", tab="Gone")
    assert deck.current is None
    decks.update("kitchen_tablet", "main", tabs=["Gone"])
    assert deck.current == "Gone" and deck.unique_id == "kitchen_tablet__main"
    with pytest.raises(logic.DeckError) as err:
        decks.update("other", "main", tab="Home")
    assert err.value.code == "not_found"


def test_limit_and_remove_browser():
    decks = logic.Decks(limit=2)
    decks.register("a", "one")
    decks.register("a", "two")
    with pytest.raises(logic.DeckError) as err:
        decks.register("b", "one")
    assert err.value.code == "too_many"
    decks.register("a", "one", tab="x")  # existing decks still update
    assert [d.deck_id for d in decks.remove_browser("a")] == ["one", "two"]
    assert len(decks) == 0


def test_store_round_trip_skips_bad_rows():
    decks = logic.Decks()
    decks.register("kitchen", "main", "Kitchen", ["Home", "Cameras"], "Cameras")
    data = decks.as_list() + [{"browser_id": "bad id"}, "junk", {"deck_id": "x"}]
    back = logic.Decks.from_list(data)
    assert [d.as_dict() for d in back] == decks.as_list()
    assert len(logic.Decks.from_list(None)) == 0


def test_slug_and_label():
    assert logic.slug("Kitchen Tablet!") == "kitchen_tablet"
    assert logic.slug("***") == "browser"
    assert logic.browser_label("hall-panel", "") == "Hall panel"
    assert logic.browser_label("x", "  Wall   tablet ") == "Wall tablet"


def test_usage_adds_up_and_ignores_junk():
    decks = logic.Decks()
    decks.register("kitchen", "main", None, ["Home", "Cameras"], "Home")
    decks.add_usage("kitchen", "main", {"Home": 2.5, "Cameras": "1.25", "Bad": "x", "Neg": -3, "Nan": float("nan"), "": 4})
    deck = decks.add_usage("kitchen", "main", {"Home": 0.5, "Huge": 10**9})
    assert deck.usage == {"Home": 3.0, "Cameras": 1.25, "Huge": logic.MAX_MINUTES_PER_REPORT}
    assert decks.add_usage("kitchen", "main", "junk").usage == deck.usage
    back = logic.Decks.from_list(decks.as_list())
    assert back.get("kitchen", "main").usage == deck.usage
    import pytest as _p
    with _p.raises(logic.DeckError):
        decks.add_usage("nobody", "main", {"Home": 1})
