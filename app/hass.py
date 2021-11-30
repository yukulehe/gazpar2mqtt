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
        
        
