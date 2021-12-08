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
import sqlite3

import gazpar
import mqtt
import standalone
import hass
import param
import database


# gazpar2mqtt constants
G2M_VERSION = '0.6'


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
    waitTime = round(gazpar._getRetryTimeSleep(tryCount))
    if waitTime < 200:
        logging.info("Wait %s seconds (%s min) before next try",waitTime,round(waitTime/60))
    else:
        logging.info("Wait %s minutes before next try",round(waitTime/60))
    time.sleep(waitTime)

#######################################################################
#### Running program
#######################################################################
def run(myParams):
    
    
    # Store time now
    dtn = _dateTimeToStr(datetime.datetime.now())
    
    # STEP 1 : Connect to database
    logging.info("-----------------------------------------------------------")
    logging.info("Connexion to SQLite database...")
    logging.info("-----------------------------------------------------------")
    
    # Create/Update database
    logging.info("Check local database/cache")
    myDb = database.Database(G2M_VERSION)
    
    
    # Connect to database
    myDb.connect()
    if myDb.isConnected() :
        logging.info("SQLite database connected !")
    else:
        logging.error("Unable to connect to SQLite database.")
    
    # Compare G2M version
    logging.info("Checking database version...")
    dbVersion = myDb.getG2MVersion()
    if dbVersion is not None:
        if dbVersion == G2M_VERSION:
            logging.info("Program and database are both at version %s.",G2M_VERSION)
        else:
            logging.warning("Program (%s) and database (%s) are not at the same version.",G2M_VERSION,dbVersion)
            logging.info("Reinitialization of the database...")
            myDb.reInit()
            dbVersion = myDb.getG2MVersion()
            logging.info("Database reinitialized in version %s !",dbVersion)
    else:
        logging.warning("Unable to get database version.")
    
    
    
    # STEP 2 : Log to MQTT broker
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
        
    
     
    # STEP 3 : Get data from GRDF website
    
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
                myGrdf.login(myParams.grdfUsername,myParams.grdfPassword)
                
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

            # Get account informations and store it to db
            logging.info("Retrieve account informations")
            myAccount = myGrdf.getWhoami()
            myAccount.store(myDb)
            myDb.commit()
            
            # Get list of PCE
            logging.info("Retrieve list of PCEs...")
            try:
                myGrdf.getPceList()
                logging.info("%s PCE found !",myGrdf.countPce())
            except:
                myGrdf.isConnected = False
                logging.info("Unable to get any PCE !")

            # Get measures for each PCE
            if myGrdf.pceList:
                for myPce in myGrdf.pceList:
                    
                    # Store PCE in database
                    myPce.store(myDb)
                    myDb.commit()
                    
                    # Get the latest slot
                    # TO BE COMPLETED IF REQUIRED

                    # Set date range
                    startDate = _getYearOfssetDate(datetime.date.today(), 3)
                    endDate = datetime.date.today()

                    # Get measures of the PCE
                    logging.info("Get measures of PCE %s alias %s",myPce.pceId,myPce.alias)
                    logging.info("Range period : from %s to %s...",startDate,endDate)
                    myGrdf.getPceDailyMeasures(myPce,startDate,endDate)
                    logging.info("%s measures retrieved, %s seems ok !",myPce.countDailyMeasure(), myPce.countDailyMeasureOk() )
                    
                    if myPce.dailyMeasureList:
                        for myMeasure in myPce.dailyMeasureList:
                            # Store measure into database
                            myMeasure.store(myDb)
                        
                        # Commmit database
                        myDb.commit()
                        
                        # Get last measure info
                        myMeasure = myPce.getLastMeasureOk()
                        logging.info("Last valid measure : Date = %s, Volume = %s m3, Energy = %s kWh.",myMeasure.gasDate,myMeasure.volume,myMeasure.energy)
                        
                        # Read calculated measures from database
                        myPce.calculateMeasures(myDb)
                            
                    else:
                        logging.info("Unable to get any measure for PCE !",myPce.pceId)
                        
                    
            else:
                logging.info("No PCE retrieved.")
        
    
    # STEP 4A : Standalone mode
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
                
                # Display topic root
                logging.info("You can retrieve published values subscribing topic %s/#",prefix)

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
                    logging.debug("Date %s, Energy = %s, Volume %s",myDailyMeasure.gasDate,myDailyMeasure.energy,myDailyMeasure.volume)

                    # Publish daily values
                    logging.info("Publishing to Mqtt...")

                    ## Last measures
                    myMqtt.publish(mySa.lastDateTopic, myDailyMeasure.gasDate)
                    myMqtt.publish(mySa.lastKwhTopic, myDailyMeasure.energy)
                    myMqtt.publish(mySa.lastMcubeTopic, myDailyMeasure.volume)
                    myMqtt.publish(mySa.indexTopic, myDailyMeasure.endIndex)

                    ## Calculated yearly measures
                    logging.debug("Creation of yearly entities")
                    myMqtt.publish(mySa.histoMcubeTopic+"/current_year", myPce.gasY0)
                    myMqtt.publish(mySa.histoMcubeTopic+"/previous_year", myPce.gasY1)

                    ## Calculated monthly measures
                    logging.debug("Creation of monthly entities")
                    myMqtt.publish(mySa.histoMcubeTopic+"/current_month", myPce.gasM0Y0)
                    myMqtt.publish(mySa.histoMcubeTopic+"/previous_month", myPce.gasM1Y0)
                    myMqtt.publish(mySa.histoMcubeTopic+"/current_month_previous_year", myPce.gasM0Y1)

                    ## Calculated weekly measures
                    logging.debug("Creation of weekly entities")
                    myMqtt.publish(mySa.histoMcubeTopic+"/current_week", myPce.gasW0Y0)
                    myMqtt.publish(mySa.histoMcubeTopic+"/previous_week", myPce.gasW1Y0)
                    myMqtt.publish(mySa.histoMcubeTopic+"/current_week_previous_year", myPce.gasW0Y1)

                    ## Calculated daily measures
                    logging.debug("Creation of daily entities")
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-1", myPce.gasD1)
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-2", myPce.gasD2)
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-3", myPce.gasD3)
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-4", myPce.gasD4)
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-5", myPce.gasD5)
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-6", myPce.gasD6)
                    myMqtt.publish(mySa.histoMcubeTopic+"/day-7", myPce.gasD7) 

                    logging.info("Daily values published !")


                    ## Publish status values
                    logging.info("Publishing to Mqtt status values...")
                    myMqtt.publish(mySa.statusDateTopic, dtn)
                    myMqtt.publish(mySa.statusValueTopic, 'ON')
                    logging.info("Status values published !")

        except:
            logging.error("Standalone mode : unable to publish value to mqtt broker")

    # STEP 4B : Home Assistant discovery mode
    if myMqtt.isConnected \
        and myParams.hassDiscovery \
        and myGrdf.isConnected:

        #try:

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
                
                # Create entity PCE
                logging.debug("Creation of the PCE entity")
                myEntity = hass.Entity(myDevice,hass.SENSOR,'pce_state','pce_state',hass.NONE_TYPE,None,None)
                myEntity.setValue(myPce.state)
                myEntity.addAttribute("pce_alias",myPce.alias)
                myEntity.addAttribute("pce_id",myPce.pceId)
                myEntity.addAttribute("freqence",myPce.freqenceReleve)
                myEntity.addAttribute("activation_date ",myPce.activationDate)
                myEntity.addAttribute("owner_name",myPce.ownerName)
                myEntity.addAttribute("postal_code",myPce.postalCode)

                # Process hass's entities to be valuated
                if not myPce.isOk(): # Values when PCE is not correct

                    # Create entities and set values
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'connectivity','Connectivity',hass.CONNECTIVITY_TYPE,None,None).setValue('OFF')

                else: # Values when PCE is correct   

                    # Get last daily measure
                    myMeasure = myPce.getLastMeasureOk()

                    # Create entities and set values
                    
                    ## Last GRDF measure
                    logging.debug("Creation of current entities")
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'last_index','index',hass.GAS_TYPE,hass.ST_TTI,'m³').setValue(myMeasure.endIndex)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'last_gas','last daily gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myMeasure.volume)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'last_energy','last daily energy',hass.ENERGY_TYPE,hass.ST_MEAS,'kWh').setValue(myMeasure.energy)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'last_consumption_date','last consumption date',hass.NONE_TYPE,None,None).setValue(str(myMeasure.gasDate))
                    
                    ## Calculated calendar measures
                    logging.debug("Creation of calendar entities")
                    
                    ### Year
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'current_year_gas','current year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasY0)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'previous_year_gas','previous year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasY1)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'previous_2_year_gas','previous 2 years gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasY2)
                    
                    ### Month
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'current_month_gas','current month gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasM0Y0)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'previous_month_gas','previous year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasM1Y0)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'current_month_last_year_gas','current month of last year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasM0Y1)
                    
                    ### Week
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'current_week_gas','current week gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasW0Y0)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'previous_week_gas','previous week gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasW1Y0)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'current_week_last_year_gas','previous week of last year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasW0Y1)
                    
                    ### Day
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_1_gas','day-1 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD1)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_2_gas','day-2 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD2)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_3_gas','day-3 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD3)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_4_gas','day-4 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD4)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_5_gas','day-5 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD5)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_6_gas','day-6 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD6)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'day_7_gas','day-7 gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasD7)
                    
                    ## Calculated rolling measures
                    logging.debug("Creation of rolling entities")
                    
                    ### Rolling year
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_year_gas','rolling year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1Y)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_year_last_year_gas','rolling year of last year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR2Y1Y)
                    
                    ### Rolling month
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_month_gas','rolling month gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1M)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_month_last_month_gas','rolling month of last month gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR2M1M)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_month_last_year_gas','rolling month of last year gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1MY1)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_month_last_2_year_gas','rolling month of last 2 years gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1MY2)
                    
                    ### Rolling week
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_week_gas','rolling week gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1W)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_week_last_week_gas','rolling week of last week gas',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR2W1W)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_week_last_year_gas','rolling week of last year',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1WY1)
                    myEntity = hass.Entity(myDevice,hass.SENSOR,'rolling_week_last_2_year_gas','rolling week of last 2 years',hass.GAS_TYPE,hass.ST_MEAS,'m³').setValue(myPce.gasR1WY2)
                    
                    ## Other
                    logging.debug("Creation of other entities")
                    myEntity = hass.Entity(myDevice,hass.BINARY,'connectivity','connectivity',hass.CONNECTIVITY_TYPE,None,None).setValue('ON')


                # Publish config, state (when value not none), attributes (when not none)
                logging.info("Publishing devices...")
                logging.info("You can retrieve published values subscribing topic %s",myDevice.hass.prefix + "/+/" + myDevice.id + "/#")
                for topic,payload in myDevice.getStatePayload().items():
                    myMqtt.publish(topic,payload)
                logging.info("Devices published !")



        #except:
            #logging.error("Home Assistant discovery mode : unable to publish value to mqtt broker")


    # STEP 5 : Disconnect mqtt broker
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
    
    
    # STEP 6 : Disconnect from database
    logging.info("-----------------------------------------------------------")
    logging.info("Disconnexion from SQLite database...")
    logging.info("-----------------------------------------------------------")
      
    if myDb.isConnected() :
        myDb.close()
        logging.info("SQLite database disconnected")
    
    # STEP 7 : Display next run info and end of program
    logging.info("-----------------------------------------------------------")
    logging.info("Next run...")
    logging.info("-----------------------------------------------------------")
    if myParams.scheduleTime is not None:
        logging.info("gazpar2mqtt next run scheduled at %s",myParams.scheduleTime)
    else:
        logging.info("No schedule define. It was a oneshot.")
    
    # Release objects
    logging.debug("Release instance objects.")
    myDb = None
    myMqtt = None
    myGrdf = None
    myHass = None
    mySa = None
    myPce = None
    myDailyMeasure = None
    myDevice = None
    myEntity = None
    
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
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=myLevel)
    else:
        myLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=myLevel)
    
    
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
