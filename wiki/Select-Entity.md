# Select entity

Each browser that opens a dashboard with a `companion: true` deck gets a device **Tabdeck <browser>**, with one select entity per deck on that dashboard, for example `select.tabdeck_kitchen_tablet_main`.

## What it shows

- **Options:** the tabs you can open in that deck right now. Navigation and action tabs (tabs with a `tap_action` that goes somewhere else) aren't options, and tabs hidden by their visibility conditions drop out until they show again.
- **State:** the open tab. Tapping a tab on the tablet updates it straight away.
- **Unavailable** while no browser window shows the deck. The entity and its last tab list come back after a Home Assistant restart, and a page that's open during the restart registers again on its own.

## Switching tabs

```yaml
actions:
  - action: select.select_option
    target:
      entity_id: select.tabdeck_kitchen_tablet_main
    data:
      option: Cameras
```

This switches every open window of that browser showing the deck. It works like the card's `remote_entity`:

- **A tab with a `pin` stays locked.** The deck only opens it if the code was entered in that browser within the tab's `pin_timeout`; otherwise the deck and the entity stay on the open tab.
- **Quiet hours win.** During the deck's `quiet_hours` a select is ignored.
- **It isn't remembered as the person's choice**, so `remember` and learned defaults aren't changed by automations.

## How the browser is named

The card picks the browser's id, in this order:

1. The deck's `companion_id`. Only use it for a dashboard that a single device shows, or every device shares one entity.
2. The Tabdeck device name, set once per browser by opening the dashboard with `?tabdeck_device=kitchen_tablet` in the URL.
3. browser_mod's browser id, if browser_mod is installed.
4. A random id the card keeps in that browser, such as `browser_1a2b3c4d`.

Rename the device or entity in Home Assistant as usual; the ids underneath don't change.

## Removing a browser

Delete its device on the integration's page. It comes back if that browser opens the dashboard again.
