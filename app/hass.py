### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json


HA_AUTODISCOVERY_PREFIX = "homeassistant"
HASS_DEVICE_NAME = "gazpar"

# Return the device config
def getDeviceConfig():
    
    deviceId = HASS_DEVICE_NAME.replace(' ','_')
    devicePayload = {
        "identifiers": [{deviceId}],
        "name": {HASS_DEVICE_NAME},
        "model": "gazpar",
        "manufacturer": "GRDF"
    }   
                        
# Return the state topic for sensors
def getStateTopicSensor():
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/{HASS_DEVICE_NAME}/state"
    return topic

# Return the state topic for binary sensors
def getStateTopicBinary():
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/{HASS_DEVICE_NAME}/state"
    return topic

# Return the configuration topic for sensors
def getConfigTopicSensor(sensor):
        
    topic = f"{HA_AUTODISCOVERY_PREFIX}/sensor/{HASS_DEVICE_NAME}/{sensor}/config"
    return topic


# Return the configuration topic for binary sensors
def getConfigTopicBinary(sensor):
    
    topic = f"{HA_AUTODISCOVERY_PREFIX}/binary_sensor/{HASS_DEVICE_NAME}/{sensor}/config"
    return topic
    
    
# Return the configuration payload    
def getConfigPayload(sensor):
    
    # Gas consumption daily
    if sensor == 'daily_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.daily_gas}}",
            "device": getDeviceConfig()
        }
    
    # Gas consumption monthly
    elif sensor == 'monthly_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.monthly_gas}}",
            "device": getDeviceConfig()
        }
        
    
    # Gas consumption monthly of previous year
    elif sensor == 'monthly_gas_prev':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.monthly_gas_prev}}",
            "device": getDeviceConfig()
        }
    
    # Energy consumption daily
    elif sensor == 'daily_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.daily_energy}}",
            "device": getDeviceConfig()
        }
    
    # Energy consumption monthly
    elif sensor == 'monthly_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy}}",
            "device": getDeviceConfig()
        }
    
    # Energy consumption monthly threshold
    elif sensor == 'monthly_energy_tsh':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy_tsh}}",
            "device": getDeviceConfig()
        }
    
    # Energy consumption monthly of previous year
    elif sensor == 'monthly_energy_prev':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy_prev}}",
            "device": getDeviceConfig()
        }
        
    # Gazpar consumption date
    elif sensor == 'consumption_date':
        
        configPayload= {
            "name": f"{HASS_DEVICE_NAME}_{device}",
            "unique_id": f"{HASS_DEVICE_NAME}_{device}",
            "state_topic": getStateTopicSensor(),
            "value_template": "{{ value_json.consumption_date}}",
            "device": getDeviceConfig()
        }
    
    # Gazpar consumption month
    elif sensor == 'consumption_month':
        
        configPayload= {
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicSensor(),
            "value_template": "{{ value_json.consumption_month}}",
            "device": getDeviceConfig()
        }
    
    # Gazpar connectivity
    elif sensor == 'connectivity':
        
        configPayload= {
            "device_class": "connectivity",
            "name": f"{HASS_DEVICE_NAME}_{sensor}",
            "unique_id": f"{HASS_DEVICE_NAME}_{sensor}",
            "state_topic": getStateTopicBinary(),
            "value_template": "{{ value_json.connectivity}}",
            "device": getDeviceConfig()
        }
        
    else:
        topic = "error"
    
    return configPayload
