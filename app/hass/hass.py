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

HA_AUTODISCOVERY_PREFIX = "homeassistant"



def getHassStateTopic(device):
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/{HASS_COMPONENT_SENSOR}/gazpar/state"
    return topic

def getHassConfigTopic():
    
    configTopic = f"{HA_AUTODISCOVERY_PREFIX}/{HASS_COMPONENT_SENSOR}/gazpar/config"
    return configTopic
    
    
def getHassConfigPayload(device):
    
    # Set state topic
    state_topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/gazpar/state"
    
    # Gas consumption daily
    if device == daily_gas:
        
        config= {
            "device_class" : "gas"
            "name" : "gaspar_daily_gas"
            "unique_id" : "gaspar_daily_gas"
            "state_topic" = state_topic
            "unit_of_measurement" : HASS_UNIT_CLASS_GAS
            "value_template" : "{{ value_json.daily_gas}}"
        }
    
    # Gas consumption monthly
    elif device == monthly_gas:
        
        config= {
            "device_class" : "gas"
            "name" : "gaspar_monthly_gas"
            "unique_id" : "gaspar_monthly_gas"
            "state_topic" = state_topic
            "unit_of_measurement" : HASS_UNIT_CLASS_GAS
            "value_template" : "{{ value_json.monthly_gas}}"
        }
    
    # Energy consumption daily
    elif device == daily_energy:
        
        config= {
            "device_class" : "energy"
            "name" : "gaspar_daily_energy"
            "unique_id" : "gaspar_daily_energy"
            "state_topic" = {getHassStateTopic(device)}
            "unit_of_measurement" : HASS_UNIT_CLASS_ENERGY
            "value_template" : "{{ value_json.daily_energy}}"
        }
    
    # Energy consumption monthly
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
    
    return config
