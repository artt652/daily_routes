#!/usr/local/bin/python3
# coding: utf-8

import logging
from . import DOMAIN
from homeassistant.helpers.entity import Entity
from homeassistant.const import (ATTR_LATITUDE, ATTR_LONGITUDE)

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None) -> None:
    sensors_gps = hass.data[DOMAIN]["sensors_gps"]
    for key, value in sensors_gps.states.items():
        async_add_entities([GPSSensor(hass, sensors_gps, key)])

class GPSSensor(Entity):

    def __init__(self, hass, sensors_gps, entity_id):
        self._icon = 'mdi:crosshairs-gps'
        self._sensors_gps = sensors_gps
        self._entity = entity_id
        self._hass = hass
        self._name = 'virtual_' + self._entity.replace('.', '_')
        self._state = ''

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._sensors_gps.states[self._entity][0]

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        attrs = {
            ATTR_LATITUDE: self._sensors_gps.states[self._entity][1],
            ATTR_LONGITUDE: self._sensors_gps.states[self._entity][2],
        }

        if (entity_state := self._hass.states.get(self._entity)):
            if entity_state.attributes.get("entity_picture"):
                attrs["entity_picture"] = entity_state.attributes["entity_picture"]
            if "gps_accuracy" in entity_state.attributes:
                attrs["gps_accuracy"] = entity_state.attributes["gps_accuracy"]

        return attrs
