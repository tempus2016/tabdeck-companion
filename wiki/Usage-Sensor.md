# Usage sensor

With `usage_stats: true` on a `companion: true` deck, the card counts how many minutes each tab is on screen and reports it to Home Assistant every 10 minutes (or every N minutes with `usage_stats: N`).

```yaml
type: custom:tabdeck-card
event_id: main
companion: true
usage_stats: 10
tabs: [ ... ]
```

The deck then gets a sensor such as `sensor.tabdeck_kitchen_tablet_main_usage`:

- **State:** total minutes on screen, as `total_increasing`, so long-term statistics, the history graph and Utility Meter helpers work.
- **`tabs` attribute:** minutes per tab, busiest first.

```yaml
{{ state_attr('sensor.tabdeck_kitchen_tablet_main_usage', 'tabs')['Cameras'] }}
```

## Minutes per day or week

Add a **Utility Meter** helper (Settings → Devices & services → Helpers → Utility Meter) with the usage sensor as input and a daily or weekly cycle.

## What counts

Only time the tab is actually on screen: the page has to be visible, so a backgrounded browser tab or a screen that's off doesn't count. A report adds at most a day per tab, and odd values are dropped.

## Without the integration

`usage_stats` falls back to firing a `tabdeck_usage` event that an automation can count. That event needs the dashboard to be opened by an admin user, because Home Assistant only lets admins fire events.
