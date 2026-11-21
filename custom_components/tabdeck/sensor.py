"""Usage stats: one sensor per deck, total minutes, with minutes per tab as attributes."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import Companion
from .const import DOMAIN, SIGNAL_DECK_UPDATED, SIGNAL_NEW_USAGE
from .logic import Deck


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    companion: Companion = hass.data[DOMAIN]
    async_add_entities(TabdeckUsage(companion, deck) for deck in companion.decks if deck.usage)

    @callback
    def add(deck: Deck) -> None:
        async_add_entities([TabdeckUsage(companion, deck)])

    entry.async_on_unload(async_dispatcher_connect(hass, SIGNAL_NEW_USAGE, add))


class TabdeckUsage(SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:chart-bar"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_suggested_display_precision = 0

    def __init__(self, companion: Companion, deck: Deck) -> None:
        self._companion = companion
        self._key = deck.key
        self._signal = SIGNAL_DECK_UPDATED.format(deck.unique_id)
        self._attr_unique_id = f"{deck.unique_id}__usage"
        self._attr_name = f"{deck.deck_id} usage"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, deck.browser_id)})

    @property
    def _deck(self) -> Deck | None:
        return self._companion.decks.get(*self._key)

    @property
    def available(self) -> bool:
        return self._deck is not None

    @property
    def native_value(self) -> float | None:
        deck = self._deck
        return round(sum(deck.usage.values()), 2) if deck else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        deck = self._deck
        if not deck:
            return {}
        # Busiest first, like the mockup's bars.
        return {"tabs": dict(sorted(deck.usage.items(), key=lambda kv: -kv[1]))}

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self._signal, self.async_write_ha_state)
        )
