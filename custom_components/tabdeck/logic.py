"""Pure bookkeeping for Tabdeck Companion: no Home Assistant imports, so it can be unit-tested alone.

A *deck* is one Tabdeck card in one browser, keyed by (browser_id, deck_id). For each deck we keep
only what the select entity needs: the browser's label, the tab names and the open tab. Nothing
else from the browser is accepted or stored.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
MAX_DECKS = 200
MAX_TABS = 100
MAX_TEXT = 100
MAX_LABEL = 64


class DeckError(ValueError):
    """A request the integration refuses (bad id, too many decks, unknown deck)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def clean_id(value: Any, what: str) -> str:
    """A browser or deck id: 1-64 of letters, digits, `_`, `.` and `-`."""
    text = str(value if value is not None else "").strip()
    if not ID_RE.match(text):
        raise DeckError("invalid_format", f"{what} must be 1-64 letters, digits, '_', '.' or '-'")
    return text


def clean_text(value: Any, limit: int = MAX_TEXT) -> str:
    """One line of plain text, trimmed and cut to `limit` characters."""
    text = " ".join(str(value if value is not None else "").split())
    return text[:limit]


def clean_tabs(values: Any) -> list[str]:
    """Tab names: text, no blanks, no duplicates (first wins), at most MAX_TABS."""
    out: list[str] = []
    if not isinstance(values, (list, tuple)):
        return out
    for value in values:
        name = clean_text(value)
        if name and name not in out:
            out.append(name)
        if len(out) >= MAX_TABS:
            break
    return out


def slug(text: str) -> str:
    """Lower-case, `_`-joined words, as Home Assistant makes object ids."""
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "browser"


def unique_id(browser_id: str, deck_id: str) -> str:
    return f"{browser_id}__{deck_id}"


def browser_label(browser_id: str, name: str | None) -> str:
    """The browser's display name: the name the card sent, else its id with `_` as spaces."""
    label = clean_text(name, MAX_LABEL) if name else ""
    return label or browser_id.replace("_", " ").replace("-", " ").strip().capitalize()


@dataclass
class Deck:
    browser_id: str
    deck_id: str
    browser_name: str
    tabs: list[str] = field(default_factory=list)
    tab: str | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.browser_id, self.deck_id)

    @property
    def unique_id(self) -> str:
        return unique_id(self.browser_id, self.deck_id)

    @property
    def current(self) -> str | None:
        """The open tab when it is one of the options (a select entity's state must be)."""
        return self.tab if self.tab in self.tabs else None

    def as_dict(self) -> dict[str, Any]:
        return {
            "browser_id": self.browser_id,
            "deck_id": self.deck_id,
            "browser_name": self.browser_name,
            "tabs": list(self.tabs),
            "tab": self.tab,
        }


class Decks:
    """Every deck seen, persisted between restarts by the caller (as_list / from_list)."""

    def __init__(self, limit: int = MAX_DECKS) -> None:
        self._decks: dict[tuple[str, str], Deck] = {}
        self._limit = limit

    def __len__(self) -> int:
        return len(self._decks)

    def __iter__(self):
        return iter(list(self._decks.values()))

    def get(self, browser_id: str, deck_id: str) -> Deck | None:
        return self._decks.get((browser_id, deck_id))

    def register(
        self,
        browser_id: Any,
        deck_id: Any,
        browser_name: Any = None,
        tabs: Any = None,
        tab: Any = None,
    ) -> tuple[Deck, bool]:
        """Add or refresh a deck. Returns (deck, created)."""
        bid = clean_id(browser_id, "browser_id")
        did = clean_id(deck_id, "deck_id")
        deck = self._decks.get((bid, did))
        created = deck is None
        if created:
            if len(self._decks) >= self._limit:
                raise DeckError("too_many", f"at most {self._limit} decks")
            deck = Deck(bid, did, browser_label(bid, browser_name))
            self._decks[(bid, did)] = deck
        elif browser_name:
            deck.browser_name = browser_label(bid, browser_name)
        self.update(bid, did, tabs=tabs, tab=tab)
        return deck, created

    def update(self, browser_id: Any, deck_id: Any, tabs: Any = None, tab: Any = None) -> Deck:
        """New tab list and/or open tab for a known deck. Returns the deck."""
        deck = self._decks.get((clean_id(browser_id, "browser_id"), clean_id(deck_id, "deck_id")))
        if deck is None:
            raise DeckError("not_found", "unknown deck: register it first")
        if tabs is not None:
            deck.tabs = clean_tabs(tabs)
        if tab is not None:
            deck.tab = clean_text(tab) or None
        return deck

    def remove_browser(self, browser_id: str) -> list[Deck]:
        """Forget every deck of one browser (its device was deleted). Returns them."""
        gone = [d for d in self._decks.values() if d.browser_id == browser_id]
        for deck in gone:
            del self._decks[deck.key]
        return gone

    def as_list(self) -> list[dict[str, Any]]:
        return [d.as_dict() for d in self._decks.values()]

    @classmethod
    def from_list(cls, data: Any, limit: int = MAX_DECKS) -> "Decks":
        """Rebuild from stored data, skipping anything malformed."""
        decks = cls(limit)
        for item in data if isinstance(data, list) else []:
            if not isinstance(item, dict):
                continue
            try:
                decks.register(
                    item.get("browser_id"), item.get("deck_id"), item.get("browser_name"), item.get("tabs"), item.get("tab")
                )
            except DeckError:
                continue
        return decks
