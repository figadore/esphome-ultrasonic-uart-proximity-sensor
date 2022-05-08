"""Platform for sensor integration."""
from __future__ import annotations
import time

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import LENGTH_MILLIMETERS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([ProximitySensor()])


class ProximitySensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None
        self.should_poll = False

    @property
    def force_update(self) -> bool:
        # trigger a state change even when value is the same
        # needed if we're going to trigger anything when the device hasn't checked in with a new level for a while
        return True

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'Sump Pump Level'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        return {"time": time.time()}

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return LENGTH_MILLIMETERS

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = 23
        pass