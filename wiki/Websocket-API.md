# Websocket API

The card talks to the integration over Home Assistant's normal, signed-in websocket connection, so only logged-in users can register decks. Other front-ends can use the same commands.

| Command | Fields | |
|---|---|---|
| `tabdeck/register` | `browser_id`, `deck_id`, `browser_name?`, `tabs`, `tab?` | Subscription. Sends `{ "command": "select", "tab": "…" }` events when the entity is set. |
| `tabdeck/update` | `browser_id`, `deck_id`, `tabs?`, `tab?` | The deck's tab list or open tab changed. |
| `tabdeck/usage` | `browser_id`, `deck_id`, `minutes` | Minutes per tab since the last report, added to the totals (at most a day per tab per report). |

## Limits

- Ids: 1–64 letters, digits, `_`, `.` or `-`.
- At most 100 tabs per deck, each at most 100 characters.
- At most 200 decks in total.

The integration stores only the browser id, deck id, browser label, tab names, the open tab and minutes per tab. It reads nothing else from the browser and exposes nothing else.
