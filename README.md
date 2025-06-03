[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Daily Routes

<p>Интеграция позволяет отображать историю перемещений на карте, используя библиотеку Leaflet, плагин <a href='https://github.com/bbecquet/Leaflet.PolylineDecorator'>Leaflet PolylineDecorator</a>, а так же строить маршрут по дорогам используя <a href='https://project-osrm.org/'>OSRM</a>.</p>
<p>В Homeassistant использутся отслеживание на основе зон, и координаты передвижения объектов хранятся не все, а только те, которые зафиксированы при смене зоны. Чтобы этого избежать, интеграцией создаются новые виртуальные sensor, у которых атрибуты будут скопированы из нужного device_tracker или person, это позволяет сохранить всю историю предвижений.</p>

Что нового:

2025/05/10 Большое обновление кода:

- Обновлены параметры конфигурации:
  - haddr: your_ha_address - удален
  - days: num_days - не обязателен ( по умолчанию 10 )
  - mindst: your_min_dst - не обязателен ( по умолчанию 0.08 )
  - time_zone: your_timezone - автоматически получаем из ХА
  - Добавлена возможность задать свой tiles_url:
  - Карта по-умолчанию центрируется на координатах из zone.home
- Виртуальные сенсоры создаются для доменов device_tracker и person. </p>
  Для снижения нарузки на БД в состояние виртуальных сенсоров теперь пишутся координаты с округлением до 4 знаков
- Добавлено отображение текущей позиции, с авто-обовлением позиции и отображение entity_picture: и gps_accuracy: если имеются
- Добвлена опция маршрутизации по дорогам используя <a href='https://project-osrm.org/'>OSRM</a> (режим "На автомобиле")

2025/04/04 Обновление кода для совместимости с ХА 2025.X.

<p><b>1. Установка</b></p>

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=artt652&category=integration&repository=daily_routes) 

и далее следовать указаниям мастера установки.

либо вручную:

<p>Содержимое папки "route" скопировать в директорию /homeassistant/custom_components/route</p>

<p><b>2. Настройка</b></p>
<p>Вручную, через добавление в  configuration.yaml: </p>

```yaml
route:
  #haddr: удален, не используется 
  token: your_long_life_token
  days: 10 # не обязательно, либо замените на своё количество дней для отображения
  mindst: 0.08 # минимальная дистанция между точками 
  time_zone: "+03:00" # не обязательно, либо замените на свой часовой пояс
  tiles_url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png" # не обязательно, либо замените на свой источник карт
  devices:
    - device_tracker.entity_id1
    - person.entity_id1
```

<p>
  "device_tracker.entity_id1", "person.entity_id1" - объекты отслеживания</p> 
  "your_long_life_token" - предварительно полученный во фронтенде HomeAssistant токен доступа для использования REST API.</p>
</p>

<p>С помощью мастера настройки:</p>

```yaml
Функционал в разработке #Следуйте указаниям мастера настройки.
```
