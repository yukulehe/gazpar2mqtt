### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json

HASS_COMPONENT_BINARY_SENSOR = "binary_sensor
HASS_COMPONENT_SENSOR = "sensor"

HASS_UNIT_CLASS_GAS = "m3"
HASS_UNIT_CLASS_ENERGY = "kWh"

HA_AUTODISCOVERY_PREFIX = "homeassistant"

# Return the state topic
def getStateTopic(device):
    
    if device in ('daily_gas','monthly_gas','daily_energy','monthly_energy','consumption_date','consumption_month'):
        
        topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/gazpar/state"
        
    elif device in ('connectivity')
    
        topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/gazpar/state"
    
    return topic

# Return the configuration topic
def getConfigTopic(device):
    
    if device in ('daily_gas','monthly_gas','daily_energy','monthly_energy' /
                  , 'gazpar_consumption_date', 'gazpar_consumption_month'):
        
        topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/gazpar/config"
        
    elif device in ('connectivity')
    
        topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/gazpar/config"
    
    return topic
    
# Return the configuration payload    
def getConfigPayload(device):
    
    # Set state topic
    stateTopic = getStateTopic(device)
    
    # Gas consumption daily
    if device == 'daily_gas':
        
        configPayload= {
            "device_class" : "gas"
            "name" : "gazpar_daily_gas"
            "unique_id" : "gazpar_daily_gas"
            "state_topic" = stateTopic
            "unit_of_measurement" : "m3"
            "value_template" : "{{ value_json.daily_gas}}"
        }
    
    # Gas consumption monthly
    elif device == 'monthly_gas':
        
        configPayload= {
            "device_class" : "gas"
            "name" : "gazpar_monthly_gas"
            "unique_id" : "gazpar_monthly_gas"
            "state_topic" = stateTopic
            "unit_of_measurement" : "m3"
            "value_template" : "{{ value_json.monthly_gas}}"
        }
    
    # Energy consumption daily
    elif device == 'daily_energy':
        
        configPayload= {
            "device_class" : "energy"
            "name" : "gazpar_daily_energy"
            "unique_id" : "gazpar_daily_energy"
            "state_topic" = stateTopic
            "unit_of_measurement" : "kWh"
            "value_template" : "{{ value_json.daily_energy}}"
        }
    
    # Energy consumption monthly
    elif device == 'monthly_energy':
        
        configPayload= {
            "device_class" : "energy"
            "name" : "gazpar_monthly_energy"
            "unique_id" : "gazpar_monthly_energy"
            "state_topic" = stateTopic
            "unit_of_measurement" : "kWh"
            "value_template" : "{{ value_json.monthly_energy}}"
        }
        
    # Gazpar consumption date
    elif device == 'consumption_date':
        
        configPayload= {
            "device_class" : "time_date"
            "display_options": "date"
            "name" : "gazpar_consumption_date"
            "unique_id" : "gazpar_consumption_date"
            "state_topic" = getHassStateTopic(device)
            "value_template" : "{{ value_json.consumption_date}}"
        }
    
    # Gazpar consumption month
    elif device == 'consumption_month':
        
        configPayload= {
            "device_class" : ""
            "name" : "gazpar_consumption_month"
            "unique_id" : "gazpar_consumption_month"
            "state_topic" = getHassStateTopic(device)
            "value_template" : "{{ value_json.gazpar_consumption_month}}"
        }
    
    # Gazpar connectivity
    elif device == 'connectivity':
        
        configPayload= {
            "device_class" : "connectivity"
            "name" : "gazpar_monthly_energy"
            "unique_id" : "gazpar_monthly_energy"
            "state_topic" = getHassStateTopic(device)
            "value_template" : "{{ value_json.connectivity}}"
        }
        
    else:
        topic = "error"
    
    return configPayload
