# Installation

## 1. Install the integration

**Home Assistant Marketplace (HACS)**

1. Open the Marketplace, then **⋮ → Custom repositories**.
2. Add `https://github.com/tempus2016/tabdeck-companion` with type **Integration**.
3. Find **Tabdeck Companion**, download it, and restart Home Assistant.

**Manual**

1. Download `tabdeck.zip` from the [latest release](https://github.com/tempus2016/tabdeck-companion/releases/latest).
2. Unpack it into `config/custom_components/tabdeck/` (the folder holds `manifest.json`, `__init__.py` and the rest).
3. Restart Home Assistant.

## 2. Add the integration

**Settings → Devices & services → Add integration → Tabdeck Companion.** There is nothing to fill in. It can only be added once.

## 3. Turn it on in a deck

Add `companion: true` to each deck you want as an entity, and give the deck an `event_id`. The id becomes part of the entity id, so without one it can change when you edit the deck.

```yaml
type: custom:tabdeck-card
event_id: main
companion: true
tabs: [ ... ]
```

The next time a browser opens that dashboard, a device **Tabdeck <browser>** appears with a select entity for the deck, for example `select.tabdeck_kitchen_tablet_main`. See [Select entity](Select-Entity) for how the browser gets its name.

## Updating

Update through the Marketplace (or replace the folder by hand) and restart Home Assistant.

## Removing

Delete the integration under **Settings → Devices & services**, remove it in the Marketplace (or delete `config/custom_components/tabdeck`), and restart. Decks with `companion: true` keep working and simply send nothing.
