### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json
from importlib import import_module

# Return a formatted device Id
def getDeviceId(device_name):
    
    device_id = device_name.replace(' ','_')
    return device_id

# Return the device config
def getDeviceConfig(prefix,device_id,device_name):
    
    config = {
            "identifiers": [{device_id}],
            "name": {device_name},
            "model": "gazpar",
            "manufacturer": "GRDF"
    }
    
    return config
                        
# Return the state topic for sensors
def getStateTopicSensor(prefix,device_id):
    
    topic = f"{prefix}/sensor/{device_id}/state"
    return topic

# Return the state topic for binary sensors
def getStateTopicBinary(prefix,device_id):
    
    topic = f"{prefix}/binary_sensor/{device_id}/state"
    return topic

# Return the configuration topic for sensors
def getConfigTopicSensor(prefix,device_id,sensor):
    
    topic = f"{prefix}/sensor/{device_id}/{sensor}/config"
    return topic


# Return the configuration topic for binary sensors
def getConfigTopicBinary(prefix,device_id,sensor):
    
    topic = f"{prefix}/binary_sensor/{device_id}/{sensor}/config"
    return topic
    
    
# Return the configuration payload    
def getConfigPayload(prefix,device_name,sensor):
    
    # Get device Id
    device_id = getDeviceId(device_name)
    
    # Gas consumption daily
    if sensor == 'daily_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.daily_gas}}",
        }
    
    # Gas consumption monthly
    elif sensor == 'monthly_gas':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.monthly_gas}}",
        }
        
    
    # Gas consumption monthly of previous year
    elif sensor == 'monthly_gas_prev':
        
        configPayload= {
            "device_class": "gas",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "m3",
            "value_template": "{{ value_json.monthly_gas_prev}}",
        }
    
    # Energy consumption daily
    elif sensor == 'daily_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.daily_energy}}",
        }
    
    # Energy consumption monthly
    elif sensor == 'monthly_energy':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy}}",
        }
    
    # Energy consumption monthly threshold
    elif sensor == 'monthly_energy_tsh':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy_tsh}}",
        }
    
    # Energy consumption monthly of previous year
    elif sensor == 'monthly_energy_prev':
        
        configPayload= {
            "device_class": "energy",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "unit_of_measurement": "kWh",
            "value_template": "{{ value_json.monthly_energy_prev}}",
        }
        
    # Gazpar consumption date
    elif sensor == 'consumption_date':
        
        configPayload= {
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "value_template": "{{ value_json.consumption_date}}",
        }
    
    # Gazpar consumption month
    elif sensor == 'consumption_month':
        
        configPayload= {
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "value_template": "{{ value_json.consumption_month}}",
        }
    
    # Gazpar connectivity
    elif sensor == 'connectivity':
        
        configPayload= {
            "device_class": "connectivity",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicBinary(prefix,device_id),
            "value_template": "{{ value_json.connectivity}}",
        }
        
    else:
        topic = "error"
    
    # Add device config to payload
    configPayload["device"].append(getDeviceConfig(prefix,device_id,device_name))

    return configPayload
