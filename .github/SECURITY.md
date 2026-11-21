# Security Policy

Tabdeck Companion is a Home Assistant **custom integration**. It runs inside
Home Assistant and adds a few websocket commands (`tabdeck/register`,
`tabdeck/update`, `tabdeck/usage`) that the Tabdeck card uses, plus a
select entity and a usage sensor per deck. It talks to no external service.

The websocket commands sit behind Home Assistant's own authentication, so only
signed-in users can call them. The integration stores a browser id, a deck id,
a browser label, the tab names, the open tab and minutes per tab, with limits
on the size of every field and on the number of decks. The most likely classes
of issue are:

- A websocket command accepting input it shouldn't: oversized or malformed
  values, or more decks or tabs than the limits allow.
- One user's browser being able to switch, rename or read another user's deck
  in a way Home Assistant's normal permissions wouldn't allow.
- Stored values (tab names, labels) reaching other parts of Home Assistant
  without the escaping its frontend normally applies.

## Supported versions

Only the **latest released version** receives security fixes. Before reporting,
please update to the newest release and confirm the issue still reproduces.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately using GitHub's
[private vulnerability reporting](https://github.com/tempus2016/tabdeck-companion/security/advisories/new)
(the **Report a vulnerability** button under the repository's **Security** tab).
This keeps the details private until a fix is available.

When reporting, please include:

- The Tabdeck Companion, Tabdeck card and Home Assistant versions.
- A description of the issue and its impact.
- Steps to reproduce, for example the websocket messages sent.

## What to expect

This is a community project maintained in spare time, so timelines are
best-effort:

- **Acknowledgement** of your report as soon as is practical.
- An assessment and, if confirmed, a fix in a subsequent release.
- Credit in the release notes, unless you'd prefer to stay anonymous.

Thank you for helping keep Tabdeck Companion and its users safe.
