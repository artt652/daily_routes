"""The route component."""

import os
from datetime import datetime, timedelta
from aiohttp import web
import aiofiles
import logging
import voluptuous as vol
import pytz
import time

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_TOKEN, CONF_TIME_ZONE, CONF_DEVICES
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.frontend import async_register_built_in_panel
from zoneinfo import ZoneInfo

_LOGGER = logging.getLogger(__name__)

DOMAIN = "route"

SUPPORTED_DOMAINS = ["sensor"]

CONF_NUMBER_OF_DAYS = 'days'
DEFAULT_NUMBER_OF_DAYS = 10
CONF_MIN_DST = 'mindst'
DEFAULT_MIN_DST = 0.08
DEFAULT_TILES_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
CONF_TILES_URL = 'tiles_url'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_TILES_URL, default=DEFAULT_TILES_URL): cv.string,
        vol.Optional(CONF_NUMBER_OF_DAYS, default=DEFAULT_NUMBER_OF_DAYS): cv.positive_int,
        vol.Optional(CONF_MIN_DST, default=DEFAULT_MIN_DST): cv.small_float,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list),
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config) -> bool:
    hass.data[DOMAIN] = {}

    try:
        tzinfo = ZoneInfo(hass.config.time_zone)
        offset = datetime.now(tzinfo).strftime('%z')
        tz_str = offset[:3] + ':' + offset[3:]
    except Exception as e:
        _LOGGER.warning("Failed to determine timezone offset, defaulting to +00:00: %s", e)
        tz_str = "+00:00"

    myconfig = {  
        "mindst": config[DOMAIN].get(CONF_MIN_DST, DEFAULT_MIN_DST),  
        "numofd": config[DOMAIN].get(CONF_NUMBER_OF_DAYS, DEFAULT_NUMBER_OF_DAYS),  
        "tz": tz_str,
        "token": config[DOMAIN][CONF_TOKEN],  
        "devs": config[DOMAIN][CONF_DEVICES],
        "tiles_url": config[DOMAIN].get(CONF_TILES_URL, DEFAULT_TILES_URL),
    }

    sensors_gps = hass.data[DOMAIN]["sensors_gps"] = SensorsGps(hass, myconfig)

    try:  
        await sensors_gps.update()  
    except Exception as e:  
        _LOGGER.warning("Error creating sensors: %s", e)  
        return False  
  
    async_track_time_interval(hass, sensors_gps.async_update, timedelta(seconds=60))  
  
    for platform in SUPPORTED_DOMAINS:  
        hass.async_create_task(async_load_platform(hass, platform, DOMAIN, {}, config))  
  
    try:  
        view = Route(hass, myconfig)  
        await view.async_create_files()  
        hass.http.register_view(view)
  
        async_register_built_in_panel(
            hass,
            component_name="iframe",
            sidebar_title="Daily Routes",
            sidebar_icon="mdi:routes",
            frontend_url_path="myroute",
            config={"url": "/route/route.html"},
            require_admin=False,
        )
        
    except Exception as e:  
        _LOGGER.error("Error creating panel: %s", e)  
        return False  
  
    return True

class Route(HomeAssistantView):
    url = r"/route/{requested_file:.+}"
    name = "route"
    requires_auth = False

    def __init__(self, hass, myconfig):
        self.hass = hass
        self._cfg = myconfig

    async def get(self, request, requested_file):
      try:
        curr_dir = os.getcwd()
        base_path = os.path.join(curr_dir, 'custom_components', DOMAIN)
        requested_file = requested_file.split('?')[0]

        if requested_file == 'route.html':
            path = os.path.join(base_path, 'route_temp.html')
        else:
            path = os.path.join(base_path, requested_file)

        if not os.path.isfile(path):
            raise FileNotFoundError

        return web.FileResponse(path)
      except Exception as e:
        _LOGGER.error("Failed to serve file '%s': %s", requested_file, e)
        return web.Response(status=404, text=f"File not found: {requested_file}")
        
    async def async_create_files(self):
        try:
            curr_dir = os.getcwd()
            pathdomain = os.path.join(curr_dir, 'custom_components', DOMAIN)
            template_path = os.path.join(pathdomain, 'route.html')
            output_path = os.path.join(pathdomain, 'route_temp.html')

            async with aiofiles.open(template_path, 'r') as file:
                filedata = await file.read()

            filedata = filedata.replace('number_of_days_variable', str(self._cfg["numofd"]))
            filedata = filedata.replace('time_zone_variable', "'" + self._cfg["tz"] + "'")
            filedata = filedata.replace('access_token_variable', self._cfg["token"])
            filedata = filedata.replace('minimal_distance_variable', str(self._cfg["mindst"]))

            home_zone = self.hass.states.get('zone.home')
            home_lat = home_zone.attributes.get('latitude', 55.755826) if home_zone else 55.755826
            home_lon = home_zone.attributes.get('longitude', 37.617) if home_zone else 37.617
            filedata = filedata.replace('__default_lat_variable__', str(home_lat))
            filedata = filedata.replace('__default_lon_variable__', str(home_lon))
            
            filedata = filedata.replace('tiles_url_variable', "'" + self._cfg.get("tiles_url", DEFAULT_TILES_URL) + "'")
            
            devices_var = '['
            for device in self._cfg["devs"]:
                entity_domain = device.split('.')[0]
                fullname = device
                friendly_name = ''
                state = self.hass.states.get(device)
                if state:
                    friendly_name = state.attributes.get('friendly_name', '')
                if not friendly_name:
                    friendly_name = device
                if entity_domain == 'device_tracker':
                    fullname = 'sensor.virtual_' + device.replace(".", "_")
                if entity_domain == 'person':
                    fullname = 'sensor.virtual_' + device.replace(".", "_")
            
                devices_var += f"['{friendly_name}', '{fullname}'],"
            devices_var = '[]' if devices_var == '[' else devices_var[:-1] + ']'
            filedata = filedata.replace('array_of_devices_variable', devices_var)

            async with aiofiles.open(output_path, 'w') as file:
                await file.write(filedata)

        except Exception as e:
            _LOGGER.error("Couldn't generate route_temp.html: %s", e)
            
class SensorsGps:
    def __init__(self, hass: HomeAssistant, mycfg):
        self.hass = hass
        self.states = {}
        self._cfg = mycfg
        self._devs = self._cfg["devs"]

    async def update(self):
        self.get_device_trackers()

    async def async_update(self, now, **kwargs) -> None:
        try:
            await self.update()
        except Exception as e:
            _LOGGER.warning("Update failed: %s", e)
        async_dispatcher_send(self.hass, DOMAIN)

    def get_device_trackers(self):
        for device in self._devs:
            entity_domain = device.split('.')[0]
            #if entity_domain == "device_tracker":
            if entity_domain in ("device_tracker", "person"):
                lat = lon = 0
                state = self.hass.states.get(device)
                if state:
                    lat = state.attributes.get('latitude', 0)
                    lon = state.attributes.get('longitude', 0)
                    if lat == 0 or lon == 0:
                        self.states[device] = ["unknown", '', '']
                    else:
                        coordinates = f"{lat:.4f}, {lon:.4f}"
                        self.states[device] = [coordinates, lat, lon]
                else:
                    self.states[device] = ["unknown", '', '']
