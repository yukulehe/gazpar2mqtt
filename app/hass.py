### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json
from importlib import import_module

MANUFACTURER = "GRDF"
UNIT_BY_CLASS = {
    "gas": "m3"
    "energy": "kWh"
    "connectivity": None
}

# Return the unit related to the device class
def _getUnitFromClass(deviceClass):
    return UNIT_BY_CLASS[deviceClass]


# Class Home assistant
class hass:
    
    # Constructor
    def __init__(prefix):
        
        self.prefix = prefix # discovery prefix
              
# Class Home assistant Device
class device:
    
    # Constructor
    def __init__(self,hass,pceId,deviceId, deviceName):
        
        self.hass = hass
        self.id = deviceId
        self.name = deviceName
        
        self.configPayload = config = {
            "identifiers": [device_id],
            "name": device_name,
            "model": pceId,
            "manufacturer": MANUFACTURER
            }
        self.deviceId = deviceId
        self.deviceName = deviceName
    
# Class Home assistant Entity
class entity:
    
    # Constructor
    def __init__(self,device,type,id,name,deviceClass):
        
        self.device = device
        self.type = type
        self.id = id
        self.name = name
        self.class = deviceClass
        self.unit = _getUnitFromClass(self.class)
        self.valueTemplate = "{{ value_json. " + self.id + " }}"
        
        # Set topics
        self.configTopic = f"{self.device.hass.prefix}/{type}/{self.device_id}/{id}/config"
        self.stateTopic = f"{self.device.hass.prefix}/{type}/{self.device_id}/state"
        
        # Set config payload
        self.configPayload = {
            "device_class": self.class,
            "name": f"{self.device.name} {self.name}",
            "unique_id": f"{self.device.id}_{self.id}",
            "state_topic": self.stateTopic,
            "unit_of_measurement": self.unit,
            "value_template": self.valueTemplate,
            "device": self.device.configPayload
            }
        
        self.statePayload = None
        
    def _getValueTemplate()
        


# Return a formated device Id
def getDeviceId(device_name):
    
    device_id = device_name.replace(' ','_')
    return device_id

# Return the device config
def getDeviceConfig(prefix,device_id,device_name):
    
    config = {
        "identifiers": [device_id],
        "name": device_name,
        "model": "monespace.grdf.fr",
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
            "device": getDeviceConfig(prefix,device_id,device_name)
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
            "device": getDeviceConfig(prefix,device_id,device_name)
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
            "device": getDeviceConfig(prefix,device_id,device_name)
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
            "device": getDeviceConfig(prefix,device_id,device_name)
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
            "device": getDeviceConfig(prefix,device_id,device_name)
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
            "device": getDeviceConfig(prefix,device_id,device_name)
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
            "device": getDeviceConfig(prefix,device_id,device_name)
        }
        
    # Gazpar consumption date
    elif sensor == 'consumption_date':
        
        configPayload= {
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "value_template": "{{ value_json.consumption_date}}",
            "device": getDeviceConfig(prefix,device_id,device_name)
        }
    
    # Gazpar consumption month
    elif sensor == 'consumption_month':
        
        configPayload= {
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicSensor(prefix,device_id),
            "value_template": "{{ value_json.consumption_month}}",
            "device": getDeviceConfig(prefix,device_id,device_name)
        }
    
    # Gazpar connectivity
    elif sensor == 'connectivity':
        
        configPayload= {
            "device_class": "connectivity",
            "name": f"{device_id}_{sensor}",
            "unique_id": f"{device_id}_{sensor}",
            "state_topic": getStateTopicBinary(prefix,device_id),
            "value_template": "{{ value_json.connectivity}}",
            "device": getDeviceConfig(prefix,device_id,device_name)
        }
        
    else:
        topic = "error"
    

    return configPayload
