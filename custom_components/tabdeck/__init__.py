"""Tabdeck Companion: a select entity per browser + Tabdeck deck.

Cards with `companion: true` open a `tabdeck/register` websocket subscription (HA's websocket
API only serves authenticated users) and send `tabdeck/update` when the tab list or the open tab
changes. Selecting an option on the entity sends `{"command": "select", "tab": ...}` down that
subscription, and the card switches. Only browser/deck ids, a browser label, tab names and the
open tab are accepted, stored or exposed.
"""

from __future__ import annotations

from typing import Any, Callable

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store

from .const import DOMAIN, SIGNAL_DECK_UPDATED, SIGNAL_NEW_DECK, STORAGE_KEY, STORAGE_VERSION
from .logic import MAX_TABS, Deck, DeckError, Decks

PLATFORMS = [Platform.SELECT]
SUBS_KEY = f"{DOMAIN}_subscriptions"
WS_KEY = f"{DOMAIN}_ws_registered"

_TEXT = vol.All(str, vol.Length(max=500))
_TABS = vol.All([_TEXT], vol.Length(max=MAX_TABS * 2))


class Companion:
    """The decks, their store, and the open browser subscriptions."""

    def __init__(self, hass: HomeAssistant, store: Store, decks: Decks) -> None:
        self.hass = hass
        self.store = store
        self.decks = decks
        # (browser_id, deck_id) -> {(connection, msg_id)}; kept in hass.data so a reload of the
        # entry doesn't lose browsers that are still subscribed.
        self.subs: dict[tuple[str, str], set[tuple[Any, int]]] = hass.data.setdefault(SUBS_KEY, {})

    def connected(self, key: tuple[str, str]) -> bool:
        return bool(self.subs.get(key))

    def attach(self, key: tuple[str, str], connection: Any, msg_id: int) -> Callable[[], None]:
        entry = (connection, msg_id)
        self.subs.setdefault(key, set()).add(entry)

        @callback
        def detach() -> None:
            subs = self.subs.get(key)
            if subs is not None:
                subs.discard(entry)
                if not subs:
                    del self.subs[key]
            self._notify(key)

        return detach

    def send(self, key: tuple[str, str], tab: str) -> bool:
        """Ask every browser window showing this deck to open `tab`."""
        subs = list(self.subs.get(key, ()))
        for connection, msg_id in subs:
            connection.send_message(websocket_api.event_message(msg_id, {"command": "select", "tab": tab}))
        return bool(subs)

    @callback
    def changed(self, deck: Deck, created: bool) -> None:
        self.save()
        if created:
            async_dispatcher_send(self.hass, SIGNAL_NEW_DECK, deck)
        else:
            self._notify(deck.key)

    @callback
    def _notify(self, key: tuple[str, str]) -> None:
        deck = self.decks.get(*key)
        if deck is not None:
            async_dispatcher_send(self.hass, SIGNAL_DECK_UPDATED.format(deck.unique_id))

    @callback
    def save(self) -> None:
        self.store.async_delay_save(lambda: {"decks": self.decks.as_list()}, 5)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    data = await store.async_load() or {}
    hass.data[DOMAIN] = Companion(hass, store, Decks.from_list(data.get("decks")))
    if not hass.data.get(WS_KEY):
        websocket_api.async_register_command(hass, ws_register)
        websocket_api.async_register_command(hass, ws_update)
        hass.data[WS_KEY] = True
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        companion: Companion | None = hass.data.pop(DOMAIN, None)
        if companion is not None:
            await companion.store.async_save({"decks": companion.decks.as_list()})
    return ok


async def async_remove_config_entry_device(hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry) -> bool:
    """Deleting a browser's device forgets its decks (they come back if that browser registers again)."""
    companion: Companion | None = hass.data.get(DOMAIN)
    if companion is None:
        return True
    for ident_domain, browser_id in device.identifiers:
        if ident_domain == DOMAIN:
            companion.decks.remove_browser(browser_id)
    companion.save()
    return True


def _companion(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> Companion | None:
    companion = hass.data.get(DOMAIN)
    if companion is None:
        connection.send_error(msg["id"], "not_loaded", "Tabdeck Companion isn't set up")
    return companion


@websocket_api.websocket_command(
    {
        vol.Required("type"): "tabdeck/register",
        vol.Required("browser_id"): _TEXT,
        vol.Required("deck_id"): _TEXT,
        vol.Optional("browser_name"): vol.Any(_TEXT, None),
        vol.Optional("tabs", default=[]): _TABS,
        vol.Optional("tab"): vol.Any(_TEXT, None),
    }
)
@callback
def ws_register(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Register a deck and stay subscribed for select commands."""
    companion = _companion(hass, connection, msg)
    if companion is None:
        return
    try:
        deck, created = companion.decks.register(
            msg["browser_id"], msg["deck_id"], msg.get("browser_name"), msg["tabs"], msg.get("tab")
        )
    except DeckError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.subscriptions[msg["id"]] = companion.attach(deck.key, connection, msg["id"])
    connection.send_result(msg["id"])
    companion.changed(deck, created)


@websocket_api.websocket_command(
    {
        vol.Required("type"): "tabdeck/update",
        vol.Required("browser_id"): _TEXT,
        vol.Required("deck_id"): _TEXT,
        vol.Optional("tabs"): _TABS,
        vol.Optional("tab"): vol.Any(_TEXT, None),
    }
)
@callback
def ws_update(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """A registered deck's tab list or open tab changed."""
    companion = _companion(hass, connection, msg)
    if companion is None:
        return
    try:
        deck = companion.decks.update(msg["browser_id"], msg["deck_id"], msg.get("tabs"), msg.get("tab"))
    except DeckError as err:
        connection.send_error(msg["id"], err.code, str(err))
        return
    connection.send_result(msg["id"])
    companion.changed(deck, False)
