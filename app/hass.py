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
NONE_TYPE = None
MANUFACTURER = "GRDF"
UNIT_BY_CLASS = {
    "gas": "m3",
    "energy": "kWh",
    "connectivity": None,
}


# Return the unit related to the device class
def _getUnitFromClass(deviceClass):
    print(deviceClass)
    if deviceClass is not None:
        return UNIT_BY_CLASS[deviceClass]
    else
        return None


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
            "identifiers": [self.id],
            "name": self.name,
            "model": pceId,
            "manufacturer": MANUFACTURER
            }
        
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
        self.deviceClass = deviceClass
        self.unit = _getUnitFromClass(self.deviceClass)
        self.valueTemplate = "{{ value_json. " + self.id + " }}"
        
        # Set topics
        self.configTopic = f"{self.device.hass.prefix}/{type}/{self.device.id}/{self.id}/config"
        self.stateTopic = f"{self.device.hass.prefix}/{type}/{self.device.id}/state"
        
        # Set config payload
        self.configPayload = {}
        self.configPayload["device_class"] = self.deviceClass
        self.configPayload["name"] = f"{self.device.name} {self.name}"
        self.configPayload["unique_id"] = f"{self.device.id}_{self.id}"
        self.configPayload["state_topic"] = self.stateTopic
        if self.unit is not None:
            self.configPayload["unit_of_measurement"] = self.unit
        self.configPayload["value_template"] = self.valueTemplate
        self.configPayload["device"] = self.device.configPayload
        
        #self.configPayload = {
        #    "device_class": self.deviceClass,
        #    "name": f"{self.device.name} {self.name}",
        #    "unique_id": f"{self.device.id}_{self.id}",
        #    "state_topic": self.stateTopic,
        #    "unit_of_measurement": self.unit,
        #    "value_template": self.valueTemplate,
        #    "device": self.device.configPayload
        #    }
        
        self.statePayload = None
        
        # Add entity to device
        self.device.addEntity(self)
    
    # Return config payload in Json format
    def getConfigPayloadJson(self):
        return json.dumps(self.configPayload)
    
    # Set state payload
    def setValue(self,value):
        self.value = value
