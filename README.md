[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Static Badge](https://img.shields.io/badge/Donate-ЮMoney-darkviolet?style=flat)](https://yoomoney.ru/fundraise/1B4FAD8FDBD.250626)
# Daily Routes

<p>See your daily movements on custom map.</p>

Updated version of [ha_routes](https://github.com/mavrikkk/ha_routes) integration.

<p><b>1. Installation</b></p>

- Use HACS (recommended):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=artt652&category=integration&repository=daily_routes) 

add repo, than click "download".

- Manually:

<p>Copy of "route" folder content to  /homeassistant/custom_components/route</p>

<p><b>2. Set-up</b></p>

- Config flow setup: *Not implemented yet.*
- [Manually](info.md "Manually"):
 
 Add to ```configuration.yaml```: </p>
```yaml
route:
  token: <your_long_life_token>
  devices:
    - <device_tracker.entity_id>
    - <person.entity_id>
```

