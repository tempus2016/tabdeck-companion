# Troubleshooting

## No device or entity appears

- Check the integration is added under **Settings → Devices & services** (installing it isn't enough).
- Check the deck has `companion: true` and you're on Tabdeck card 1.6.0 or later.
- Open (or reload) the dashboard in the browser: a deck registers when it's shown.
- Look in **Settings → System → Logs** for errors from `custom_components.tabdeck`.

## The entity is unavailable

That's normal while no browser window shows the deck. Open the dashboard and it comes back.

## The entity id keeps changing

Give the deck an `event_id`. Without one the deck id is made from the deck itself and changes when you edit it.

## Every device shares one entity

Remove `companion_id` from the deck, or only use it on a dashboard that a single device shows. Name each browser once with `?tabdeck_device=<name>` instead.

## Selecting an option does nothing

- The tab has a `pin` and wasn't unlocked in that browser within `pin_timeout`.
- The deck is in its `quiet_hours`.
- The option isn't a tab you can open right now (hidden by visibility conditions, or a navigation/action tab).
- Turn on the card's `debug` to see why a switch was skipped in the browser console.

## More logging

```yaml
logger:
  logs:
    custom_components.tabdeck: debug
```
