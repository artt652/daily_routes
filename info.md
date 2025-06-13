**Описание**

<p>Интеграция позволяет отображать историю перемещений на карте, используя библиотеку Leaflet, плагин <a href='https://github.com/bbecquet/Leaflet.PolylineDecorator'>Leaflet PolylineDecorator</a>, а так же строить маршрут по дорогам используя <a href='https://project-osrm.org/'>OSRM</a>.</p>

<p>В Homeassistant использутся отслеживание на основе зон, и координаты передвижения объектов хранятся не все, а только те, которые зафиксированы при смене зоны. Чтобы этого избежать, интеграцией создаются новые виртуальные sensor, у которых атрибуты будут скопированы из нужного device_tracker или person, это позволяет сохранить всю историю предвижений.</p>

**Пример конфигурации**

```yaml
route:
  token: your_long_life_token
  days: 10
  mindst: 0.08
  time_zone: "+03:00"
  tiles_url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
  devices:
    - device_tracker.entity_id
    - person.entity_id
```

**Описание параметров:**  
  
key |  |description  
:--- | |:---  
**days** | *Optional* | Number of days to show / количество дней для выбора из истории
**mindst** | *Optional* | Minimal distance between two points on map / минимальная дистанция между точками на карте)
**time_zone** | *Optional* | Timezone, for example ```"+03:00"``` / часовой пояс, например ```"+03:00"```
**tiles_url** | *Optional* | map tiles source / источник подложки карты
**token** | *Required* | Long-lived access [token](https://my.home-assistant.io/redirect/profile_security/ "token") to use REST API (долгосрочный [токен](https://my.home-assistant.io/redirect/profile_security/ "token") доступа для использования REST API)
**devices** | *Required* | ```entity_id``` for tracking, in```device_tracker``` or ```person``` domains  / ```entity_id``` для отслеживания, из доменов ```device_tracker``` или ```person```

**Как добавить Яндекс-карту**

1. В Кабинете разработчика Яндекса получите бесплатный [API ключ](https://developer.tech.yandex.ru/ "API ключ") для пакета «Tiles API». Ключ будет активирован в течение 15 минут после получения.
2. В конфигурации укажите ```tiles_url: "https://tiles.api-maps.yandex.ru/v1/tiles/?{x}&y={y}&z={z}&lang=ru_RU&l=map&scale=2&projection=web_mercator&maptype=future_map&apikey=YOUR_API_KEY"```, либо измените url согласно [формату запроса.](https://yandex.ru/maps-api/docs/tiles-api/request.html "Формат запроса")
3. Укажите в атрибутах карты [логотип](https://yandex.ru/maps-api/docs/tiles-api/index.html#using-logo "логотип") Яндекса.


**Как это все выглядит**

![example][exampleimg]



***

[exampleimg]: map.jpeg