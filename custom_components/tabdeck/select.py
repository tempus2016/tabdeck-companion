"""One select entity per browser + deck: options are the tab names, the state is the open tab."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import Companion
from .const import DOMAIN, SIGNAL_DECK_UPDATED, SIGNAL_NEW_DECK
from .logic import Deck


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    companion: Companion = hass.data[DOMAIN]
    async_add_entities(TabdeckSelect(companion, deck) for deck in companion.decks)

    @callback
    def add(deck: Deck) -> None:
        async_add_entities([TabdeckSelect(companion, deck)])

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_DECK, add))


class TabdeckSelect(SelectEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:tab"

    def __init__(self, companion: Companion, deck: Deck) -> None:
        self._companion = companion
        self._key = deck.key
        self._attr_unique_id = deck.unique_id
        self._attr_name = deck.deck_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, deck.browser_id)},
            name=f"Tabdeck {deck.browser_name}",
            manufacturer="Tabdeck",
            model="Browser",
        )

    @property
    def _deck(self) -> Deck | None:
        return self._companion.decks.get(*self._key)

    @property
    def available(self) -> bool:
        return self._deck is not None and self._companion.connected(self._key)

    @property
    def options(self) -> list[str]:
        deck = self._deck
        return list(deck.tabs) if deck else []

    @property
    def current_option(self) -> str | None:
        deck = self._deck
        return deck.current if deck else None

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_DECK_UPDATED.format(self.unique_id), self.async_write_ha_state)
        )

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="unknown_tab", translation_placeholders={"tab": option}
            )
        if not self._companion.send(self._key, option):
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="not_connected")
        # The state changes when the browser reports the switch (tabdeck/update).
