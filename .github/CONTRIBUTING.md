# Contributing to Tabdeck Companion

Thanks for your interest in improving Tabdeck Companion! It is a small,
focused Home Assistant integration for the
[Tabdeck card](https://github.com/tempus2016/tabdeck-card) — contributions that
fix bugs or add well-scoped features are very welcome.

## Development setup

```bash
pip install pytest pytest-asyncio ruff
python -m pytest                          # unit tests
ruff check custom_components tests        # lint (CI runs the same)
```

The tests cover the plain bookkeeping in `custom_components/tabdeck/logic.py`
(registering decks, limits, usage totals) and the static files (manifest,
translations, brand images). The parts that talk to Home Assistant
(`__init__.py`, `select.py`, `sensor.py`, `config_flow.py`) are tested on a
real Home Assistant instance, so keep logic in `logic.py` where it can be unit
tested.

## Testing in Home Assistant

1. Copy `custom_components/tabdeck` into your Home Assistant `config/custom_components/`.
2. Restart Home Assistant and check **Settings → System → Logs** for errors from `custom_components.tabdeck`.
3. Add the integration under **Settings → Devices & services**.
4. Open a dashboard with a Tabdeck card that has `companion: true` and `event_id` set, then check the select entity follows the open tab and that `select.select_option` switches it.

For more logging:

```yaml
logger:
  logs:
    custom_components.tabdeck: debug
```

## Pull requests

- One logical change per PR, with a test where practical.
- Update the README and the wiki pages in `wiki/` when behaviour changes.
- The version lives in `custom_components/tabdeck/manifest.json`; releases are
  cut by the maintainer, so leave it alone.
- Don't add AI co-author attribution to commits or files.

## Reporting issues

Use the [issue templates](https://github.com/tempus2016/tabdeck-companion/issues/new/choose).
Problems with how tabs look or switch on screen belong in
[tabdeck-card](https://github.com/tempus2016/tabdeck-card/issues).

## Code of conduct

Be kind. See [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).
