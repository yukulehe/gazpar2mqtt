#!/usr/bin/env python3

import argparse
import os
import logging

def _isItTrue(val):
  
  if val.lower() == 'true':
    return True
  else:
    return False

class Param:
  
  def __init(self):
    
    # Grdf params
    self.grdfUsername = None
    self.grdfPassword = None
    
    # Mqtt params
    self.mqttHost = None
    self.mqttPort = 1883
    self.mqttClientId = 'gazpar2mqtt'
    self.mqttUsername = None
    self.mqttPassword = None
    self.mqttQos = 1
    self.mqttTopic = 'gazpar'
    self.mqttRetain = False
    self.mqttSsl = False
    
    # Run params
    scheduleTime = None
    
    # Publication params
    self.standalone = True
    self.hassDiscovery = False
    self.hassPrefix = 'homeassistant'
    self.hassDeviceName = 'gazpar'
    
    # Debug param
    self.debug = False
    
    
      
  # Load params from Os environment variables 
  def getFromOs(self):
    
    if "GRDF_USERNAME" in os.environ: self.grdfUsername = os.environ["GRDF_USERNAME"]
    if "GRDF_PASSWORD" in os.environ: self.grdfPassword = os.environ["GRDF_PASSWORD"]
      
    if "MQTT_HOST" in os.environ: self.mqttHost = os.environ["MQTT_HOST"]
    if "MQTT_PORT" in os.environ: self.mqttPort = os.environ["MQTT_PORT"]
    if "MQTT_CLIENTID" in os.environ: self.mqttClientId = os.environ["MQTT_CLIENTID"]
    if "MQTT_USERNAME" in os.environ: self.mqttUsername = os.environ["MQTT_USERNAME"]
    if "MQTT_PASSWORD" in os.environ: self.mqttPassword = os.environ["MQTT_PASSWORD"]
    if "MQTT_QOS" in os.environ: self.mqttQos = os.environ["MQTT_QOS"]
    if "MQTT_TOPIC" in os.environ: self.mqttTopic = os.environ["MQTT_TOPIC"]
    if "MQTT_RETAIN" in os.environ: self.mqttRetain = _isItTrue(os.environ["MQTT_RETAIN"])
    if "MQTT_SSL" in os.environ: self.mqttSsl = _isItTrue(os.environ["MQTT_SSL"])
      
    if "SCHEDULE_TIME" in os.environ: self.scheduleTime = os.environ["SCHEDULE_TIME"]
      
    if "STANDALONE_MODE" in os.environ: self.standalone = _isItTrue(os.environ["STANDALONE_MODE"])
    if "HASS_DISCOVERY" in os.environ: self.hassDiscovery = _isItTrue(os.environ["HASS_DISCOVERY"])
    if "HASS_PREFIX" in os.environ: self.hassPrefix = os.environ["HASS_PREFIX"]
    if "HASS_DEVICE_NAME" in os.environ: self.hassDeviceName = os.environ["HASS_DEVICE_NAME"]
    
    if "DEBUG" in os.environ: self.debug = _isItTrue(os.environ["DEBUG"])
      
  # Get params from arguments in command line
  def getFromArgs(self,args):
    
    # do something
    
  # Check mandatory parameters
  def checkMandatory(self):
    
    if self.grdfUsername is None:
      logging.error("Parameter GRDF username is mandatory.")
      return False
    elif self.grdfPassword is None:
      logging.error("Parameter GRDF password is mandatory.")
      return False
    elif self.mqttHost is None:
      logging.error("Parameter MQTT host is mandatory.")
      return False
    else:
      return True
