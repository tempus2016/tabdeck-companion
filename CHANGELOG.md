# Changelog

## v1.1.0 — 2026-11-27

Tabdeck Companion now follows the way Home Assistant 2026.11 sets up and unloads integrations, so it needs Home Assistant 2026.11 or later. Nothing changes in how decks, select entities or usage sensors behave, and nothing in your automations or card config needs to change.

## Changed

- **Needs Home Assistant 2026.11 or later.** Home Assistant 2026.11 changed how an integration tells it that setup or unloading worked: it now finishes, or raises an error that says what went wrong, instead of answering yes or no. The companion now does it that way. Home Assistant 2026.10 and older can't load an integration written like this, so the Marketplace won't install this update on those versions, and v1.0.0 keeps working. Update Home Assistant first, then the companion. ([#4](https://github.com/tempus2016/tabdeck-companion/pull/4))
- **A failed unload now says so.** If one of the companion's entities can't be unloaded when you reload or remove the integration, Home Assistant shows a translated "failed to unload" error, and the decks stay loaded and saved, as before. ([#4](https://github.com/tempus2016/tabdeck-companion/pull/4))
- **A shorter Marketplace page.** The release, download, licence and build badges at the top of the README are hidden on the integration's Marketplace page from Home Assistant 2026.12. GitHub still shows them. ([#4](https://github.com/tempus2016/tabdeck-companion/pull/4))

## Upgrading

- **Update Home Assistant to 2026.11 or later first.** On older versions the Marketplace won't install v1.1.0, and v1.0.0 keeps working.
- **Marketplace:** open **Settings → Marketplace**, open **Tabdeck Companion**, click **Update**, then restart Home Assistant.
- **Manual install:** replace `config/custom_components/tabdeck` with the folder from `tabdeck.zip` and restart.
- Your decks, entity ids and usage history carry over. See [Installation](https://github.com/tempus2016/tabdeck-companion/wiki/Installation) on the wiki.

**Full changelog:** https://github.com/tempus2016/tabdeck-companion/compare/v1.0.0...v1.1.0

## v1.0.0 — 2026-11-21

Tabdeck Companion is a small integration for the [Tabdeck card](https://github.com/tempus2016/tabdeck-card). It turns each browser's deck into a Home Assistant select entity, so an automation can see which tab a wall tablet shows and change it with `select.select_option`, and it can count how many minutes each tab is on screen. It needs the Tabdeck card 1.6.0 or later, where a deck opts in with `companion: true`. This is the first release.

## Added

- **Each browser's deck is a select entity.** When a browser opens a dashboard whose deck has `companion: true`, a device **Tabdeck <browser>** appears with one select per deck, such as `select.tabdeck_kitchen_tablet_main`. Its options are the tabs you can open and its state is the open tab. Tapping a tab on the tablet updates the entity, and `select.select_option` switches every open window of that browser showing the deck. Set `event_id` on the deck so the entity id doesn't change.

  ```yaml
  actions:
    - action: select.select_option
      target:
        entity_id: select.tabdeck_kitchen_tablet_main
      data:
        option: Cameras
  ```

- **A tab with a PIN stays locked.** Selecting a PIN-locked tab leaves the deck where it is unless the code was entered in that browser within the tab's `pin_timeout`, and the entity stays on the open tab. Selecting is also ignored during the deck's `quiet_hours`, and isn't remembered as the person's own choice.
- **Minutes per tab as a sensor.** With `usage_stats: true` on a companion deck, the card reports every 10 minutes (or every N with `usage_stats: N`) how long each tab was on screen. The deck gets a sensor such as `sensor.tabdeck_kitchen_tablet_main_usage`: total minutes as `total_increasing`, so long-term statistics and Utility Meter helpers work, with minutes per tab in its `tabs` attribute, busiest first.
- **Browsers keep a stable name.** The browser is named after the card's `companion_id`, the Tabdeck device name set once with `?tabdeck_device=kitchen_tablet`, browser_mod's browser id, or a random id kept in that browser, in that order. Rename the device or entity in Home Assistant as usual.
- **The entity goes unavailable while no window shows the deck**, and comes back with its last tab list after a restart. When the page is open during a restart, the deck registers again on its own.
- **It only stores tab names.** The card talks over Home Assistant's normal signed-in websocket, so only logged-in users can register a deck. The integration keeps a browser id, deck id, label, tab names, the open tab and minutes per tab, with limits on every field, and nothing else.
- **Set up from the UI.** **Settings → Devices & services → Add integration → Tabdeck Companion**, with nothing to fill in, and it ships its own icon.

## Upgrading

- **Home Assistant Marketplace (HACS):** add `https://github.com/tempus2016/tabdeck-companion` as a custom repository of type **Integration**, download **Tabdeck Companion** and restart Home Assistant.
- **Manual install:** copy `custom_components/tabdeck` into `config/custom_components/` and restart.
- Then add the integration under **Settings → Devices & services**, and add `companion: true` (and `event_id`) to each deck you want as an entity. See the card's [Remote control](https://github.com/tempus2016/tabdeck-card/wiki/Feature-Remote-Control) page.
