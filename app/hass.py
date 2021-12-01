### Define Home Assistant-related functionality. ###
# More info on HA discovery : https://www.home-assistant.io/docs/mqtt/discovery

import json
from importlib import import_module

# Constants
SENSOR = "sensor"
BINARY = "binary_sensor"
GAS_TYPE = "gas"
ENERGY_TYPE = "energy"
CONNECTIVITY_TYPE = "connectivity"
NONE_TYPE = ""
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
class Hass:
    
    # Constructor
    def __init__(self,prefix):
        
        self.prefix = prefix # discovery prefix
        self.deviceList = []
        
    def addDevice(self,device):
        self.deviceList.append(device)
        return device
              

# Class Home assistant Device
class Device:
    
    # Constructor
    def __init__(self,hass,pceId,deviceId, deviceName):
        
        self.hass = hass
        self.id = deviceId
        self.name = deviceName
        
        self.entityList = []
        
        self.configPayload = config = {
            "identifiers": [device_id],
            "name": device_name,
            "model": pceId,
            "manufacturer": MANUFACTURER
            }
        self.deviceId = deviceId
        self.deviceName = deviceName
        
        # Add device to hass
        hass.addDevice(self)
        
        
    # Add entity
    def addEntity(self,entity):
        self.entityList.append(entity)
    
    # Return the state payload of all entities of the device
    def getStatePayload(self,entityType):
        payload = {}
        for myEntity in self.entityList:
            payload[myEntity.id]=myEntity.value
        return payload
    
    
# Class Home assistant Entity
class Entity:
    
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
        
        # Add entity to device
        self.device.addEntity(self)
    
    # Return config payload in Json format
    def getConfigPayloadJson(self):
        return json.dumps(self.configPayload)
    
    # Set state payload
    def setValue(self,value):
        self.value = value
