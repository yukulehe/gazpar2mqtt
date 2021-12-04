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
    if "MQTT_PORT" in os.environ: self.mqttPort = int(os.environ["MQTT_PORT"])
    if "MQTT_CLIENTID" in os.environ: self.mqttClientId = os.environ["MQTT_CLIENTID"]
    if "MQTT_USERNAME" in os.environ: self.mqttUsername = os.environ["MQTT_USERNAME"]
    if "MQTT_PASSWORD" in os.environ: self.mqttPassword = os.environ["MQTT_PASSWORD"]
    if "MQTT_QOS" in os.environ: self.mqttQos = int(os.environ["MQTT_QOS"])
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
    
    if args.grdf_username is not None: self.grdfUsername = args.grdf_username
    if args.grdf_password is not None: self.grdfPassword = args.grdf_password
      
    if args.mqtt_host is not None: self.mqttHost = args.mqtt_host
    if args.mqtt_port is not None: self.mqttPort = int(args.mqtt_port)
    if args.mqtt_clientId is not None: self.mqttClientId = args.mqtt_clientId
    if args.mqtt_username is not None: self.mqttUsername = args.mqtt_username
    if args.mqtt_password is not None: self.mqttPassword = args.mqtt_password
    if args.mqtt_qos is not None: self.mqttQos = int(args.mqtt_qos)
    if args.mqtt_topic is not None: self.mqttTopic = args.mqtt_topic
    if args.mqtt_retain is not None: self.mqttRetain = isItTrue(args.mqtt_retain)
    if args.mqtt_ssl is not None: self.mqttSsl = isItTrue(args.mqtt_ssl)
      
    if args.schedule is not None: self.scheduleTime = args.schedule
      
    if args.standalone_mode is not None: self.standalone = isItTrue(args.standalone_mode)
    if args.hass_discovery is not None: self.hassDiscovery = isItTrue(args.hass_discovery)
    if args.hass_prefix is not None: self.hassPrefix = args.hass_prefix
    if args.hass_device_name is not None: self.hassDeviceName = args.hass_device_name
      
    if args.debug is not None: self.debug = isItTrue(args.debug)
    
    
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
