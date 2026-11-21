# Automation examples

Replace `select.tabdeck_kitchen_tablet_main` with your own entity.

## Show the cameras when the doorbell rings, then go back

```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.doorbell
    to: "on"
actions:
  - variables:
      previous: "{{ states('select.tabdeck_kitchen_tablet_main') }}"
  - action: select.select_option
    target:
      entity_id: select.tabdeck_kitchen_tablet_main
    data:
      option: Cameras
  - delay: "00:01:00"
  - action: select.select_option
    target:
      entity_id: select.tabdeck_kitchen_tablet_main
    data:
      option: "{{ previous }}"
mode: restart
```

The card can also do this on its own with `takeover`, which shows a banner and countdown; see the card's [Remote control](https://github.com/tempus2016/tabdeck-card/wiki/Feature-Remote-Control) page.

## Switch by time of day

```yaml
triggers:
  - trigger: time
    at: "07:00:00"
    id: Kitchen
  - trigger: time
    at: "22:00:00"
    id: Bedroom
actions:
  - action: select.select_option
    target:
      entity_id: select.tabdeck_kitchen_tablet_main
    data:
      option: "{{ trigger.id }}"
```

## Do something when a tab is opened

```yaml
triggers:
  - trigger: state
    entity_id: select.tabdeck_kitchen_tablet_main
    to: Cameras
actions:
  - action: camera.turn_on
    target:
      entity_id: camera.front_door
```

## Every tablet shows the same tab

```yaml
triggers:
  - trigger: state
    entity_id: select.tabdeck_hall_tablet_main
actions:
  - action: select.select_option
    target:
      entity_id: select.tabdeck_kitchen_tablet_main
    data:
      option: "{{ trigger.to_state.state }}"
conditions:
  - condition: template
    value_template: "{{ trigger.to_state.state in state_attr('select.tabdeck_kitchen_tablet_main', 'options') }}"
```

For decks on the same dashboard and device, the card's own `sync_group` does this without an automation.
