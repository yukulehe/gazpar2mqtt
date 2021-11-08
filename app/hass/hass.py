"""Define Home Assistant-related functionality."""
import argparse
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

HASS_COMPONENT_BINARY_SENSOR = "binary_sensor"
HASS_COMPONENT_SENSOR = "sensor"

HASS_DEVICE_CLASS_GAS = "gas"
HASS_DEVICE_CLASS_ENERGY = "energy"

HASS_UNIT_CLASS_GAS = "m3"
HASS_UNIT_CLASS_ENERGY = "kWh"


@dataclass
class EntityDescription:
    """Define a description (set of characteristics) of a Home Assistant entity."""

    platform: str

    device_class: Optional[str] = None
    icon: Optional[str] = None
    unit: Optional[str] = None
    unit_class: Optional[str] = None


ENTITY_DESCRIPTIONS = {
    GASPAR_GAS: EntityDescription(
        platform=HASS_COMPONENT_SENSOR,
        device_class=HASS_DEVICE_CLASS_GAS,
        unit_class=HASS_UNIT_CLASS_GAS,
    ),
    GASPAR_ENERGYY: EntityDescription(
        platform=HASS_COMPONENT_SENSOR,
        device_class=HASS_DEVICE_CLASS_ENERGY,
        unit="HASS_UNIT_CLASS_ENERGY",
    ),
}

def get_entity_description(
    key: str, value: Union[float, int, str]
) -> EntityDescription:
    """Get an entity description for a data key.

    1. Return a specific data point if it exists.
    2. Return a globbed data point if it exists.
    3. Return defaults if no specific or globbed data points exist.
    """
    if DATA_POINT_GLOB_BATT in key and isinstance(value, str):
        # Because Ecowitt doesn't give us a clear way to know what sort of battery
        # we're looking at (a binary on/off battery or one that reports voltage), we
        # check its value: strings are binary, floats are voltage:
        return ENTITY_DESCRIPTIONS[DATA_POINT_GLOB_BATT_BINARY]

    if key in ENTITY_DESCRIPTIONS:
        return ENTITY_DESCRIPTIONS[key]

    globbed_descriptions = [v for k, v in ENTITY_DESCRIPTIONS.items() if k in key]
    if globbed_descriptions:
        return globbed_descriptions[0]

    LOGGER.info("No entity description found for key: %s", key)
    return EntityDescription(platform=PLATFORM_SENSOR)


class HassDiscovery:
    """Define a Home Assistant MQTT Discovery manager."""

    def __init__(self, device: Device, args: argparse.Namespace) -> None:
        """Initialize."""
        self._args = args
        self._config_payloads: Dict[str, Dict[str, Any]] = {}
        self._device = device

    def _get_topic(self, key: str, platform: str, topic_type: str) -> str:
        """Get the attributes topic for a particular entity type."""
        return (
            f"{self._args.hass_discovery_prefix}/{platform}/{self._device.unique_id}/"
            f"{key}/{topic_type}"
        )

    def get_config_payload(
        self, key: str, value: Union[float, int, str]
    ) -> Dict[str, Any]:
        """Return the config payload for a particular entity type."""
        if key in self._config_payloads:
            return self._config_payloads[key]

        description = get_entity_description(key, value)

        if description.unit_class:
            description.unit = UNIT_MAPPING[description.unit_class][
                self._args.output_unit_system
            ]

        self._config_payloads[key] = {
            "availability_topic": self._get_topic(
                key, description.platform, "availability"
            ),
            "device": {
                "identifiers": [self._device.unique_id],
                "manufacturer": self._device.manufacturer,
                "model": self._device.name,
                "name": self._device.name,
                "sw_version": self._device.station_type,
            },
            "name": key,
            "qos": 1,
            "state_topic": self._get_topic(key, description.platform, "state"),
            "unique_id": f"{self._device.unique_id}_{key}",
        }

        if description.device_class:
            self._config_payloads[key]["device_class"] = description.device_class
        if description.icon:
            self._config_payloads[key]["icon"] = description.icon
        if description.unit:
            self._config_payloads[key]["unit_of_measurement"] = description.unit

        return self._config_payloads[key]

    def get_config_topic(self, key: str, value: Union[float, int, str]) -> str:
        """Return the config topic for a particular entity type."""
        description = get_entity_description(key, value)
        return self._get_topic(key, description.platform, "config")
