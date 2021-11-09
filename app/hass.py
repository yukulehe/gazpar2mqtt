### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json


HA_AUTODISCOVERY_PREFIX = "homeassistant"
MQTT_PREFIX = "gazpar"

# Return the state topic for sensors
def getStateTopicSensor():
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/{MQTT_PREFIX}/state"
    return topic

# Return the state topic for binary sensors
def getStateTopicSensorBinary():
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/{MQTT_PREFIX}/state"
    return topic

# Return the configuration topic for sensors
def getConfigTopicSensor():
        
    topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/{MQTT_PREFIX}/config"
    return topic


# Return the configuration topic for binary sensors
def getConfigTopicBinary():
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/{MQTT_PREFIX}/config"
    return topic
    
    
# Return the configuration payload    
def getConfigPayload(device):
    
    # Gas consumption daily
    if device == 'daily_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.daily_gas}}"
        }
    
    # Gas consumption monthly
    elif device == 'monthly_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.monthly_gas}}"
        }
    
    # Energy consumption daily
    elif device == 'daily_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.daily_energy}}"
        }
    
    # Energy consumption monthly
    elif device == 'monthly_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getStateTopicSensor(),
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
            "state_topic": getStateTopicSensor(),
            "value_template": "{{ value_json.consumption_date}}"
        }
    
    # Gazpar consumption month
    elif device == 'consumption_month':
        
        configPayload= {
            "device_class": "",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getStateTopicSensor(),
            "value_template": "{{ value_json.consumption_month}}"
        }
    
    # Gazpar connectivity
    elif device == 'connectivity':
        
        configPayload= {
            "device_class": "connectivity",
            "name": f"{MQTT_PREFIX}_{device}",
            "unique_id": f"{MQTT_PREFIX}_{device}",
            "state_topic": getStateTopicBinary(),
            "value_template": "{{ value_json.connectivity}}"
        }
        
    else:
        topic = "error"
    
    return configPayload
