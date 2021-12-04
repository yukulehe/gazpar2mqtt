#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Work in progress...

import os
import sys
import datetime
import schedule
import time
#import locale
from dateutil.relativedelta import relativedelta
import json
import logging

import gazpar
import mqtt
import standalone
import hass
import param

#import requests
#import argparse

#import pprint
#from envparse import env

# gazpar2mqtt constants
G2M_VERSION = '0.5.3'


# Hass global
HASS_AUTODISCOVERY_PREFIX = None
HASS_DEVICE_NAME = None

#######################################################################
#### Functions
#######################################################################

# Sub to get date with day offset
def _getDayOfssetDate(day, number):
    return day - relativedelta(days=number)

# Sub to get date with month offset
def _getMonthOfssetDate(day, number):
    return _dayToStr(day - relativedelta(months=number))

# Sub to return format wanted
def _dateTimeToStr(datetime):
    return datetime.strftime("%d/%m/%Y - %H:%M:%S")

# Get environment parameters
def _getEnvParams():
    
    # Check and get mandatory environment parameters
    params = {}
    
    if not "GRDF_USERNAME" in os.environ:
        params['grdf','username'] = None
    else:
        params['grdf','username'] = os.environ['GRDF_USERNAME']
        
    if not "GRDF_PASSWORD" in os.environ:
        params['grdf','password'] = None
    else:
        params['grdf','password'] = os.environ['GRDF_PASSWORD']
        
    if not "MQTT_HOST" in os.environ:
        params['mqtt','host'] = None
    else:
        params['mqtt','host'] = os.environ['MQTT_HOST']
        
    # Check and get optional environment parameters
    
    if not "SCHEDULE_TIME" in os.environ:
        params['schedule','time'] = None
    else:
        params['schedule','time'] = os.environ['SCHEDULE_TIME']
        
    if not "MQTT_PORT" in os.environ:
        params['mqtt','port'] = 1883
    else:
        myPort = os.environ['MQTT_PORT'].replace('"','') # Fix issue #13
        params['mqtt','port'] = int(myPort)
        
    if not "MQTT_CLIENTID" in os.environ:
        params['mqtt','clientId'] = 'gazpar2mqtt'
    else:
        params['mqtt','clientId'] = os.environ['MQTT_CLIENTID']
    
    if not "MQTT_USERNAME" in os.environ:
        params['mqtt','username'] = ''
    else:
        params['mqtt','username'] = os.environ['MQTT_USERNAME']
    
    if not "MQTT_PASSWORD" in os.environ:
        params['mqtt','password'] = ''
    else:
        params['mqtt','password'] = os.environ['MQTT_PASSWORD']
        
    if not "MQTT_QOS" in os.environ:
        params['mqtt','qos'] = 1
    else:
        params['mqtt','qos'] = int(os.environ['MQTT_QOS'])
        
    if not "MQTT_TOPIC" in os.environ:
        params['mqtt','topic'] = "gazpar"
    else:
        params['mqtt','topic'] = os.environ['MQTT_TOPIC']
        
    if not "MQTT_RETAIN" in os.environ:
        params['mqtt','retain'] = "False"
    else:
        params['mqtt','retain'] = os.environ['MQTT_RETAIN']
    
    if not "MQTT_SSL" in os.environ:
        params['mqtt','ssl'] = "False"
    else:
        params['mqtt','ssl'] = os.environ['MQTT_SSL']
    
    if not "STANDALONE_MODE" in os.environ:
        params['standalone','mode'] = "True"
    else:
        params['standalone','mode'] = os.environ['STANDALONE_MODE']
        
    if not "HASS_DISCOVERY" in os.environ:
        params['hass','discovery'] = "False"
    else:
        params['hass','discovery'] = os.environ['HASS_DISCOVERY']
    
    if not "HASS_PREFIX" in os.environ:
        params['hass','prefix'] = "homeassistant"
    else:
        params['hass','prefix'] = os.environ['HASS_PREFIX']
    
    if not "HASS_DEVICE_NAME" in os.environ:
        params['hass','device_name'] = "gazpar"
    else:
        params['hass','device_name'] = os.environ['HASS_DEVICE_NAME']
        
    if not "DEBUG" in os.environ:
        params['debug','enable'] = "False"
    else:
        params['debug','enable'] = os.environ['DEBUG']
    
    return params


#######################################################################
#### Running program
#######################################################################
def run(params):
    
    
    # Store time now
    dtn = _dateTimeToStr(datetime.datetime.now())
    
    # STEP 1 : Log to MQTT broker
    logging.info("-----------------------------------------------------------")
    logging.info("Connexion to Mqtt broker")
    logging.info("-----------------------------------------------------------")
    
    try:
        
        logging.info("Connect to Mqtt broker...")

        # Create mqtt client
        myMqtt = mqtt.Mqtt(params['mqtt','clientId'],params['mqtt','username'],params['mqtt','password'],params['mqtt','ssl'],params['mqtt','qos'],params['mqtt','retain'])

        # Connect mqtt brocker
        myMqtt.connect(params['mqtt','host'],params['mqtt','port'])

        # Wait mqtt callback (connexion confirmation)
        time.sleep(2)

        if myMqtt.isConnected:
            logging.info("Mqtt broker connected !")
        
    except:
        logging.error("Unable to connect to Mqtt broker. Please check that broker is running, or check broker configuration.")
        
    
     
    # STEP 2 : Get data from GRDF website
    
    if myMqtt.isConnected:
    
        logging.info("-----------------------------------------------------------")
        logging.info("Get data from GRDF website")
        logging.info("-----------------------------------------------------------")

        tryCount = 0
        # Connexion
        while tryCount < gazpar.GRDF_API_MAX_RETRIES :
            try:
                
                tryCount += 1
                
                # Create Grdf instance
                logging.info("Connexion to GRDF, try %s/%s...",tryCount,gazpar.GRDF_API_MAX_RETRIES)
                myGrdf = gazpar.Grdf()

                # Connect to Grdf website
                myGrdf.login(params['grdf','username'],params['grdf','password'])
                
                # Check connexion
                if myGrdf.isConnected:
                    logging.info("GRDF connected !")
                    break
                else:
                    logging.info("Unable to login to GRDF website")
                    logging.info("Wait %s seconds berfore next try",gazpar.GRDF_API_WAIT_BTW_RETRIES)
                    wait(gazpar.GRDF_API_WAIT_BTW_RETRIES)

            except:
                myGrdf.isConnected = False
                logging.info("Unable to login to GRDF website")
                logging.info("Wait %s seconds before next try",gazpar.GRDF_API_WAIT_BTW_RETRIES)
                time.sleep(gazpar.GRDF_API_WAIT_BTW_RETRIES)
            

        # When GRDF is connected
        if myGrdf.isConnected:

            # Get account informations
            logging.info("Retrieve account informations")
            try:
                myGrdf.getWhoami()
                logging.info("GRDF account informations retrieved !")
            except:
                myGrdf.isConnected = False
                logging.info("Unable to get GRDF account informations !")

            # Get list of PCE
            logging.info("Retrieve list of PCEs...")
            try:
                myGrdf.getPceList()
                logging.info("%s PCE found !",myGrdf.countPce())
            except:
                myGrdf.isConnected = False
                logging.info("Unable to get PCE !")

            # Get measures for each PCE
            for pce in myGrdf.pceList:

                # Set date range
                startDate = _getDayOfssetDate(datetime.date.today(), 7)
                endDate = _getDayOfssetDate(datetime.date.today(), 1)

                # Get measures of the PCE
                logging.info("Get measures of PCE %s alias %s",pce.pceId,pce.alias)
                logging.info("Range period : from %s to %s...",startDate,endDate)
                myGrdf.getPceDailyMeasures(pce,startDate,endDate)
                logging.info("%s measures retrieved, %s seems ok !",pce.countDailyMeasure(), pce.countDailyMeasureOk() )

                # Log last valid measure
                myMeasure = pce.getLastMeasureOk()
                logging.info("Last valid measure : Date = %s, Volume = %s m3, Energy = %s kWh.",myMeasure.gasDate,myMeasure.volume,myMeasure.energy)
        
    
    # STEP 3A : Standalone mode
    if myMqtt.isConnected \
        and params['standalone','mode'].lower()=="true" \
        and myGrdf.isConnected:   

        try:

            logging.info("-----------------------------------------------------------")
            logging.info("Stand alone publication mode")
            logging.info("-----------------------------------------------------------")

            # Loop on PCEs
            for myPce in myGrdf.pceList:

                logging.info("Publishing values of PCE %s alias %s...",myPce.pceId,myPce.alias)
                logging.info("---------------------------------")

                # Set parameters
                prefix = params['mqtt','topic'] + '/' + myPce.pceId

                # Instantiate Standalone class by PCE
                mySa = standalone.Standalone(prefix)

                # Set values
                if not myPce.isOk(): # PCE is not correct

                    ## Publish status values
                    logging.info("Publishing to Mqtt status values...")
                    myMqtt.publish(mySa.statusDateTopic, dtn)
                    myMqtt.publish(mySa.statusValueTopic, 'OFF')
                    logging.info("Status values published !")


                else: # Values when Grdf succeeded

                    myDailyMeasure = myPce.getLastMeasureOk()

                    # Publish daily values
                    logging.info("Publishing to Mqtt the last daily values...")
                    logging.debug("Date %s, Energy = %s, Volume %s",myDailyMeasure.gasDate,myDailyMeasure.energy,myDailyMeasure.volume)
                    myMqtt.publish(mySa.dailyDateTopic, myDailyMeasure.gasDate)
                    myMqtt.publish(mySa.dailyKwhTopic, myDailyMeasure.energy)
                    myMqtt.publish(mySa.dailyMcubeTopic, myDailyMeasure.volume)
                    myMqtt.publish(mySa.indexTopic, myDailyMeasure.endIndex)
                    logging.info("Daily values published !")


                    ## Publish status values
                    logging.info("Publishing to Mqtt status values...")
                    myMqtt.publish(mySa.statusDateTopic, dtn)
                    myMqtt.publish(mySa.statusValueTopic, 'ON')
                    logging.info("Status values published !")

        except:
            logging.error("Standalone mode : unable to publish value to mqtt broker")

    # STEP 3B : Home Assistant discovery mode
    if myMqtt.isConnected \
        and params['hass','discovery'].lower() == 'true' \
        and myGrdf.isConnected:

        try:

            logging.info("-----------------------------------------------------------")
            logging.info("Home assistant publication mode")
            logging.info("-----------------------------------------------------------")

            # Create hass instance
            myHass = hass.Hass(params['hass','prefix'])

            # Loop on PCEs
            for myPce in myGrdf.pceList:

                logging.info("Publishing values of PCE %s alias %s...",myPce.pceId,myPce.alias)
                logging.info("---------------------------------")


                # Create the device corresponding to the PCE
                deviceId = params['hass','device_name'].replace(" ","_") + "_" +  myPce.pceId
                deviceName = params['hass','device_name'] + " " +  myPce.alias
                myDevice = hass.Device(myHass,myPce.pceId,deviceId,deviceName)

                # Process hass's entities to be valuated
                if not myPce.isOk(): # Values when PCE is not correct

                    # Create entities and set values
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'connectivity','Connectivity',hass.CONNECTIVITY_TYPE,None,None).setValue('ON')

                else: # Values when PCE is correct   

                    # Get last daily measure
                    myDailyMeasure = myPce.getLastMeasureOk()

                    # Create entities and set values
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'index','index',hass.GAS_TYPE,hass.ST_TTI,'m³').setValue(myDailyMeasure.endIndex)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'daily_gas','daily gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myDailyMeasure.volume)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'daily_energy','daily energy',hass.ENERGY_TYPE,hass.ST_MEAS,'kWh').setValue(myDailyMeasure.energy)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'consumption_date','consumption date',hass.NONE_TYPE,None,None).setValue(str(myDailyMeasure.gasDate))
                    myEntity = hass.Entity(myDevice,hass.BINARY,'connectivity','connectivity',hass.CONNECTIVITY_TYPE,None,None).setValue('ON')


                # Publish config
                logging.info("Publishing devices configuration ...")
                for myEntity in myDevice.entityList:
                    myMqtt.publish(myEntity.configTopic, myEntity.getConfigPayloadJson())
                logging.info("Devices configuration published !")

                # Publish state of all entities of the device, one call by device class
                logging.info("Publishing devices state ...")
                for topic,payload in myDevice.getStatePayload().items():
                    myMqtt.publish(topic,json.dumps(payload))
                logging.info("Devices state published !")



        except:
            logging.error("Home Assistant discovery mode : unable to publish value to mqtt broker")
            sys.exit(1)


    # STEP 4 : Disconnect mqtt broker
    if myMqtt.isConnected:
        
        logging.info("-----------------------------------------------------------")
        logging.info("Disconnexion from MQTT")
        logging.info("-----------------------------------------------------------")
        
        try:
            myMqtt.disconnect()
            logging.info("Mqtt broker disconnected")
        except:
            logging.error("Unable to disconnect mqtt broker")
            sys.exit(1)
            
    
    if params['schedule','time'] is not None:
        logging.info("gazpar2mqtt next run scheduled at %s",params['schedule','time'])
    
    logging.info("-----------------------------------------------------------")
    logging.info("End of program")
    logging.info("-----------------------------------------------------------")
    

        
        
        
#######################################################################
#### Main
#######################################################################                
if __name__ == "__main__":
    
    
    # Load params
    myParams = param.Params
    
    # Check params
    myParams.checkParams()
        
    # Set logging
    if myParams.debug:
        myLevel = logging.DEBUG
        logging.basicConfig(format='%(asctime)s %(message)s', level=myLevel)
    else:
        myLevel = logging.INFO
    
    logging.basicConfig(format='%(asctime)s %(message)s', level=myLevel)
    
    
    # Say welcome and be nice
    logging.info("Welcome to gazpar2mqtt")
    logging.info("-----------------------------------------------------------")
    logging.info("Version " + G2M_VERSION)
    logging.info("Please note that the the tool is still under development, various functions may disappear or be modified.")
    logging.debug("If you can read this line, you are in DEBUG mode.")
    logging.info("-----------------------------------------------------------")
        
    
    
    # STEP 7 : Log params info
    logging.info("-----------------------------------------------------------")
    logging.info("Program parameters")
    logging.info("-----------------------------------------------------------")
    myParams.logParams()

    

    # STEP 8 : Run
    if myParams.scheduleTime is not None:
        
        # Run once at lauch
        run(myParams)

        # Then run at scheduled time
        schedule.every().day.at(myParams.scheduleTime).do(run,myParams)
        while True:
            schedule.run_pending()
            time.sleep(1)
        logging.info("End of gazpar2mqtt. See u...")
        
    else:
        
        # Run once
        run(myParams)
        logging.info("End of gazpar2mqtt. See u...")
