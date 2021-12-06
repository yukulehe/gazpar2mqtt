#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Work in progress...

import os
import sys
import datetime
import schedule
import time
from dateutil.relativedelta import relativedelta
import json
import logging

import gazpar
import mqtt
import standalone
import hass
import param


# gazpar2mqtt constants
G2M_VERSION = '0.6.0'


#######################################################################
#### Functions
#######################################################################

# Sub to get date with day offset
def _getDayOfssetDate(day, number):
    return day - relativedelta(days=number)

# Sub to get date with month offset
def _getMonthOfssetDate(day, number):
    return _dayToStr(day - relativedelta(months=number))

# Sub to get date with year offset
def _getYearOfssetDate(day, number):
    return day - relativedelta(years=number)

# Sub to return format wanted
def _dateTimeToStr(datetime):
    return datetime.strftime("%d/%m/%Y - %H:%M:%S")

# Sub to wait between 2 GRDF tries
def _waitBeforeRetry(tryCount):
    waitTime = gazpar._getRetryTimeSleep(tryCount)
    if waitTime < 200:
        logging.info("Wait %s seconds (%s min) before next try",waitTime,round(waitTime/60))
    else:
        logging.info("Wait %s minutes before next try",round(waitTime/60))

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
        myMqtt = mqtt.Mqtt(myParams.mqttClientId,myParams.mqttUsername,myParams.mqttPassword,myParams.mqttSsl,myParams.mqttQos,myParams.mqttRetain)

        # Connect mqtt broker
        myMqtt.connect(myParams.mqttHost,myParams.mqttPort)

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
                #myGrdf.login(myParams.grdfUsername,myParams.grdfPassword)
                
                # Check connexion
                if myGrdf.isConnected:
                    logging.info("GRDF connected !")
                    break
                else:
                    logging.info("Unable to login to GRDF website")
                    _waitBeforeRetry(tryCount)

            except:
                myGrdf.isConnected = False
                logging.info("Unable to login to GRDF website")
                _waitBeforeRetry(tryCount)
            

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
                startDate = _getYearOfssetDate(datetime.date.today(), 3)
                endDate = datetime.date.today()

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
        and myParams.standalone \
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
                prefix = myParams.mqttTopic + '/' + myPce.pceId

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
        and myParams.hassDiscovery \
        and myGrdf.isConnected:

        try:

            logging.info("-----------------------------------------------------------")
            logging.info("Home assistant publication mode")
            logging.info("-----------------------------------------------------------")

            # Create hass instance
            myHass = hass.Hass(myParams.hassPrefix)

            # Loop on PCEs
            for myPce in myGrdf.pceList:

                logging.info("Publishing values of PCE %s alias %s...",myPce.pceId,myPce.alias)
                logging.info("---------------------------------")


                # Create the device corresponding to the PCE
                deviceId = myParams.hassDeviceName.replace(" ","_") + "_" +  myPce.pceId
                deviceName = myParams.hassDeviceName + " " +  myPce.alias
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
            
    
    if myParams.scheduleTime is not None:
        logging.info("gazpar2mqtt next run scheduled at %s",myParams.scheduleTime)
    
    logging.info("-----------------------------------------------------------")
    logging.info("End of program")
    logging.info("-----------------------------------------------------------")
        
        
#######################################################################
#### Main
#######################################################################                
if __name__ == "__main__":
    
    # Load params
    myParams = param.Params()
        
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
    
    
    # Log params info
    logging.info("-----------------------------------------------------------")
    logging.info("Program parameters")
    logging.info("-----------------------------------------------------------")
    myParams.logParams()
    
    # Check params
    logging.info("Check parameters...")
    if myParams.checkParams():
        logging.info("Parameters are ok !")
    else:
        logging.error("Error on parameters. End of program.")
        quit()
    
    # Run
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
