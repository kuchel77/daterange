"""Sensor to indicate whether the current day is in a range of dates."""
from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    BinarySensorEntity,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Date Range Sensor"
DEFAULT_OFFSET = 0
DEFAULT_DATES = [["1970-01-01","1970-01-01"]]

CONF_OFFSET = "days_offset"
CONF_DATES = "dates"

PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_DATES, default=[DEFAULT_DATES]): vol.All(cv.ensure_list),
        vol.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): cv.string
    }
)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Workday sensor."""
    days_offset: int = config[CONF_OFFSET]
    sensor_name: str = config[CONF_NAME]
    dates: list = config[CONF_DATES]
    
    add_entities(
        [IsDateRangeSensor(dates, days_offset, sensor_name)],
        True,
    )

def get_date(input_date: date) -> date:
    """Return date. Needed for testing."""
    return input_date


class IsDateRangeSensor(BinarySensorEntity):
    """Implementation of a date range sensor."""

    def __init__(
        self,
        dates: list,
        days_offset: int,
        name: str,
    ) -> None:
        """Initialize the date range sensor."""
        self._attr_name = name
        self._dates = dates
        self._days_offset = days_offset
        self._attr_extra_state_attributes = {
            CONF_OFFSET: days_offset
        }

    def is_in_date_range(self, now: date) -> bool:
        """Check if given day is in the includes list."""
        for datepair in self._dates:
            if now >= dt.parse_datetime(datepair[0]).astimezone() and now <= dt.parse_datetime(datepair[1]).astimezone():
                return True
        
        return False

    async def async_update(self) -> None:
        """Get date and look whether it is in a date range."""
        self._attr_is_on = False
        adjusted_date = dt.now() + timedelta(days=int(self._days_offset))
        if self.is_in_date_range(adjusted_date):
            self._attr_is_on = True
