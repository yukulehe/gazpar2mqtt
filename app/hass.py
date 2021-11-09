### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json


HA_AUTODISCOVERY_PREFIX = "homeassistant"
MQTT_PREFIX = "gazpar"

# Return the state topic
def getStateTopic(device):
    
    if device in ('daily_gas','monthly_gas','daily_energy','monthly_energy','consumption_date','consumption_month'):
        
        topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/{MQTT_PREFIX}/state"
        
    elif device in ('connectivity'):
    
        topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/{MQTT_PREFIX}/state"
    
    return topic

# Return the configuration topic
def getConfigTopic(device):
    
    if device in ('daily_gas','monthly_gas','daily_energy','monthly_energy' \
                  , 'consumption_date', 'consumption_month'):
        
        topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/{MQTT_PREFIX}/config"
        
    elif device in ('connectivity'):
    
        topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/{MQTT_PREFIX}/config"
    
    return topic
    
# Return the configuration payload    
def getConfigPayload(device):
    
    # Set state topic
    stateTopic = getStateTopic(device)
    
    # Gas consumption daily
    if device == 'daily_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": stateTopic,
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.daily_gas}}"
        }
    
    # Gas consumption monthly
    elif device == 'monthly_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": stateTopic,
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.monthly_gas}}"
        }
    
    # Energy consumption daily
    elif device == 'daily_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": stateTopic,
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.daily_energy}}"
        }
    
    # Energy consumption monthly
    elif device == 'monthly_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": stateTopic,
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy}}"
        }
        
    # Gazpar consumption date
    elif device == 'consumption_date':
        
        configPayload= {
            "device_class": "time_date",
            "display_options": "date",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getHassStateTopic(device),
            "value_template": "{{ value_json.consumption_date}}"
        }
    
    # Gazpar consumption month
    elif device == 'consumption_month':
        
        configPayload= {
            "device_class": "",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getHassStateTopic(device),
            "value_template": "{{ value_json.consumption_month}}"
        }
    
    # Gazpar connectivity
    elif device == 'connectivity':
        
        configPayload= {
            "device_class": "connectivity",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getHassStateTopic(device),
            "value_template": "{{ value_json.connectivity}}"
        }
        
    else:
        topic = "error"
    
    return configPayload
