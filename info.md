**Description / Описание**
<p>This integration allows you to display the history of movements on the map of your HomeAssistant</p>
<p>Интеграция позволяет отображать историю перемещений на карте в вашем HomeAssistant</p>

What's new: / Что нового:

2025/04/04 Update code for work with HA 2025.4 / Обновление кода для совместимости с ХА 2025

**Pre-installation instructions**

<p>The homeassistant API is designed to receive history only when state is change. Since the state of device_tracker is location in some zone or "not_home", then not all coordinates will be, but only those that were fixed when the states changed. You only seem to be able to get list of state change locations (when moving from zones). To avoid this, it is neccecary to create a new sensor in HA, in which the attributes will be copied from the desired device_tracker, and the state will be last_updated. This happens automatically. You only need to add the neccecary device_tracker to the configuration file. ATTENTION. Make sure the base_url parameter is correctly configured in the HA configuration.yaml </p>
  
<p>API homeassistant устроен так, что позволяет получать историю только при изменении состояний. Так как состоянием у device_tracker является расположение в какой либо зоне или "not_home", то и координаты будут не все, а только те, которые зафиксированы при смене состояний. Чтобы этого избежать нужно создать в HA новый sensor, у которого атрибуты будут скопированы у нужного device_tracker, а состоянием будет last_updated. Это происходит автоматически. Вам нужно лишь добавить нужный device_tracker в конфигурационный файл. ВНИМАНИЕ. Для правильной работы интеграции убедитесь, что в конфигурации HA правильно заполнен параметр base_url. </p>

**Installation instructions:**

```yaml
route:
  days: num_days
  mindst: your_min_dst
  time_zone: your_timezone
  token: your_long_life_token
  devices:
    - your_device_tracker_entity_id1
    - your_sensor_entity_id1
```

**Configuration variables:**  
  
key | description  
:--- | :---  
**days (Option)** | is number of days to choose from in history (это количество дней, для выбора из истории)
**mindst (Option)** | is minimal distance between two points on map (минимальная дистанция между точками, для отображения на карте)
**time_zone (Required)** | is your timezone, for example '+03:00' (ваш часовой пояс, например '+03:00')
**token (Required)** | is the access token previously received in the frontend of HomeAssistant to use REST API (предварительно полученный во фронтенде HomeAssistant токен доступа для использования REST API)
**devices (Required)** | the HA entityid's of your device_trackers or sensors(это ID ваших устройств, за которыми будете наблюдать)

**Screenshots (very blurred!!!)**

![example][exampleimg]



***

[exampleimg]: map.jpeg
