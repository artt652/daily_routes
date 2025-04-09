"""The route component."""

import os
from datetime import datetime, timedelta
from aiohttp import web
import aiofiles
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_TOKEN, CONF_TIME_ZONE, CONF_DEVICES
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components.http import HomeAssistantView
from homeassistant.components.frontend import async_register_built_in_panel

_LOGGER = logging.getLogger(__name__)

DOMAIN = "route"

SUPPORTED_DOMAINS = ["sensor"]

CONF_NUMBER_OF_DAYS = 'days'
DEFAULT_NUMBER_OF_DAYS = 10
CONF_MIN_DST = 'mindst'
DEFAULT_MIN_DST = 0.1
CONF_HADDR = 'haddr'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_NUMBER_OF_DAYS, default=DEFAULT_NUMBER_OF_DAYS): cv.positive_int,
        vol.Optional(CONF_MIN_DST, default=DEFAULT_MIN_DST): cv.small_float,
        vol.Required(CONF_HADDR): cv.string,
        vol.Required(CONF_TIME_ZONE): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_DEVICES): vol.All(cv.ensure_list),
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config) -> bool:
    hass.data[DOMAIN] = {}
    myconfig = {
        "mindst": config[DOMAIN][CONF_MIN_DST],
        "numofd": config[DOMAIN][CONF_NUMBER_OF_DAYS],
        "tz": config[DOMAIN][CONF_TIME_ZONE],
        "token": config[DOMAIN][CONF_TOKEN],
        "devs": config[DOMAIN][CONF_DEVICES],
        "haddr": config[DOMAIN][CONF_HADDR],
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
            "iframe",
            "Routes",
            "mdi:routes",
            "myroute",
            {"url": "/route/route.html"},
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
            path = curr_dir + '/custom_components/' + DOMAIN + '/route_temp.html'
            return web.FileResponse(path)
        except Exception as e:
            _LOGGER.error("Failed to serve route_temp.html: %s", e)
            return web.Response(status=404)

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
            filedata = filedata.replace('haddr_variable', "'" + self._cfg["haddr"] + "'")
            filedata = filedata.replace('minimal_distance_variable', str(self._cfg["mindst"]))

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
        timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for device in self._devs:
            entity_domain = device.split('.')[0]
            if entity_domain == "device_tracker":
                lat = lon = 0
                state = self.hass.states.get(device)
                if state:
                    lat = state.attributes.get('latitude', 0)
                    lon = state.attributes.get('longitude', 0)
                self.states[device] = [timenow, lat, lon]
