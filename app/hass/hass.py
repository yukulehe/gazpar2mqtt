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

def getHassStateTopic(device):
    
    topic = f"{ha_autodiscovery_prefix}/{ha_device_class_gas}/gazpar/state"
    return topic

def getHassTopic(device):
    
    if device == gas:
        topic = f"{ha_autodiscovery_prefix}/{ha_device_class_gas}/gazpar/state"
    elif device == energy:
        topic = f"{ha_autodiscovery_prefix}/{ha_device_class_gas}/gazpar/state"
    else:
        topic = "error"
    
    return topic
    

    
def getHassConfig(device,value):
    
    if device == daily_gas:
        
        config= {
            "device_class" : "gas"
            "name" : "gaspar_daily_gas"
            "unique_id" : "gaspar_daily_gas"
            "state_topic" = getHassStateTopic(device)
            "unit_of_measurement" : HASS_UNIT_CLASS_GAS
            "value_template" : "{{ value_json.daily_gas}}"
        }
    
    elif device == monthly_gas:
        
        config= {
            "device_class" : "gas"
            "name" : "gaspar_monthly_gas"
            "unique_id" : "gaspar_monthly_gas"
            "state_topic" = getHassStateTopic(device)
            "unit_of_measurement" : HASS_UNIT_CLASS_GAS
            "value_template" : "{{ value_json.monthly_gas}}"
        }
        
    elif device == daily_energy:
        
        config= {
            "device_class" : "energy"
            "name" : "gaspar_daily_energy"
            "unique_id" : "gaspar_daily_energy"
            "state_topic" = {getHassStateTopic(device)}
            "unit_of_measurement" : HASS_UNIT_CLASS_ENERGY
            "value_template" : "{{ value_json.daily_energy}}"
        }
     
    elif device == monthly_energy:
        
        config= {
            "device_class" : "energy"
            "name" : "gaspar_monthly_energy"
            "unique_id" : "gaspar_monthly_energy"
            "state_topic" = getHassStateTopic(device)
            "unit_of_measurement" : HASS_UNIT_CLASS_ENERGY
            "value_template" : "{{ value_json.monthly_energy}}"
        }
        
    else:
        topic = "error"
    
