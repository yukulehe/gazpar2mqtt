#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Work in progress...

import os
import sys
import datetime
import schedule
import time
import locale
from dateutil.relativedelta import relativedelta
import gazpar
import mqtt
import hass
import json

import argparse
import logging
import pprint
from envparse import env

# Grdf API constants
GRDF_API_MAX_RETRIES = 5 # number of retries max to get accurate data from GRDF
GRDF_API_WAIT_BTW_RETRIES = 10 # number of seconds between two tries
GRDF_API_ERRONEOUS_COUNT = 1 # Erroneous number of results send by GRDF 

# Sensors topics for standalone mode

## Daily
TOPIC_DAILY_DATE = "/daily/date"
TOPIC_DAILY_KWH = "/daily/kwh"
TOPIC_DAILY_MCUBE = "/daily/mcube"

## Monthly
TOPIC_MONTHLY_DATE = "/monthly/month"
TOPIC_MONTHLY_KWH = "/monthly/kwh"
TOPIC_MONTHLY_KWH_TSH = "/monthly/kwh/threshold"
TOPIC_MONTHLY_KWH_PREV = "/monthly/kwh/previous"
TOPIC_MONTHLY_MCUBE = "/monthly/mcube"
TOPIC_MONTHLY_MCUBE_TSH = "/monthly/kwh/threshold"
TOPIC_MONTHLY_MCUBE_PREV = "/monthly/kwh/previous"


## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"


#######################################################################
#### Functions
#######################################################################

# Sub to get date with day offset
def _getDayOfssetDate(day, number):
    return _dayToStr(day - relativedelta(days=number))

# Sub to get date with month offset
def _getMonthOfssetDate(day, number):
    return _dayToStr(day - relativedelta(months=number))

# Sub to return format wanted
def _dayToStr(date):
    return date.strftime("%d/%m/%Y")

# Sub to return format wanted
def _dateTimeToStr(datetime):
    return datetime.strftime("%d/%m/%Y - %H:%M:%S")

# Get environment parameters
def _getEnvParams():
    
    # Check and get mandatory environment parameters
    params = {}
    
    if not "GRDF_USERNAME" in os.environ:
        logging.error("Environement variable 'GRDF_USERNAME' is mandatory")
        quit()
    else:
        params['grdf','username'] = os.environ['GRDF_USERNAME']
        
    if not "GRDF_PASSWORD" in os.environ:
        logging.error("Environement variable 'GRDF_USERNAME' is mandatory")
        quit()
    else:
        params['grdf','password'] = os.environ['GRDF_PASSWORD']
        
    if not "MQTT_HOST" in os.environ:
        logging.error("Environement variable 'MQTT_HOST' is mandatory")
        quit()
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
        params['mqtt','port'] = int(os.environ['MQTT_PORT'])
        
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
        params['mqtt','topic'] = 'gazpar'
    else:
        params['mqtt','topic'] = os.environ['MQTT_TOPIC']
        
    if not "MQTT_RETAIN" in os.environ:
        params['mqtt','retain'] = 'False'
    else:
        params['mqtt','retain'] = os.environ['MQTT_RETAIN']
    
    if not "STANDALONE_MODE" in os.environ:
        params['standalone','mode'] = 'True'
    else:
        params['standalone','mode'] = os.environ['STANDALONE_MODE']
        
    if not "HASS_DISCOVERY" in os.environ:
        params['hass','discovery'] = 'False'
    else:
        params['hass','discovery'] = os.environ['HASS_DISCOVERY']
    
    if not "HASS_PREFIX" in os.environ:
        params['hass','prefix'] = 'homeassistant'
    else:
        params['hass','prefix'] = os.environ['HASS_PREFIX']
    
    return params

# Log to GRDF
def _log_to_Grdf(username,password):
    
    # Log to GRDF API
    try:
                      
        logging.info("Logging in GRDF URI %s...", gazpar.API_BASE_URI)
        token = gazpar.login(username, password)
        logging.info("Logged in successfully !")
        return token
                      
    except:
        logging.error("unable to login on %s", gazpar.API_BASE_URI)
        sys.exit(1)

#######################################################################
#### Running program
#######################################################################
def run(params):
    
    # Store time now
    dtn = _dateTimeToStr(datetime.datetime.now())
    
    # Prepare flag
    hasGrdfFailed = False
    
    # STEP 2 : Log to MQTT broker
    logging.info("-----------------------------------------------------------")
    logging.info("Connexion to Mqtt broker")
    logging.info("-----------------------------------------------------------")
    
    try:
        
        logging.info("Connect to Mqtt broker...")
        
        # Construct mqtt client
        client = mqtt.create_client(params['mqtt','clientId'],params['mqtt','username'],params['mqtt','password'])
    
        # Connect mqtt brocker
        mqtt.connect(client,params['mqtt','host'],params['mqtt','port'])
        
        # Wait mqtt callback (connection confirmation)
        time.sleep(2)
        
        if mqtt.MQTT_IS_CONNECTED:
            logging.info("Mqtt broker connected !")
        else:
            sys.exit(1)
        
    except:
        logging.error("Unable to connect to Mqtt broker. Please check that broker is running, or check broker configuration.")
        sys.exit(1)
    
    
    
    # STEP 3 : Get data from GRDF API
    
    ## STEP 3A : Get daily data
    logging.info("-----------------------------------------------------------")
    logging.info("Get data from GRDF")
    logging.info("-----------------------------------------------------------")
    
    
    try:
        
        # Set period (5 days ago)
        startDate = _getDayOfssetDate(datetime.date.today(), 5)
        endDate = _dayToStr(datetime.date.today())

        logging.info("Get daily data from GRDF")

        # Get data and retry when failed
        i= 1
        dCount = 0
        isDailyDataOk = False

        while i <= GRDF_API_MAX_RETRIES:

            if i > 1:
                logging.info("Failed. Please wait %s seconds for next try",GRDF_API_WAIT_BTW_RETRIES)
                time.sleep(GRDF_API_WAIT_BTW_RETRIES)

            logging.info("Try number %s", str(i))
            
            # Log to Grdf
            try:
                logging.info("Trying to log to Grdf...")
                token = _log_to_Grdf(params['grdf','username'], params['grdf','password'])
            except:
                logging.error("Error during log to Grdf")
                i = i + 1
                continue # next try

            # Get result from GRDF by day
            try:
                logging.info("Trying to get daily values from Grdf...")
                resDay = gazpar.get_data_per_day(token, startDate, endDate)
            except:
                logging.error("Error to get Grdf daily data")
                i = i + 1
                continue # next loop
            
            # Check results
            dCount = len(resDay)
            if dCount <= GRDF_API_ERRONEOUS_COUNT:
                logging.warning("Daily values from GRDF seems wrong...")
                i = i + 1
                continue # next loop
            else:
                isDailyDataOk = True
                break # exit loop
  
        # Display results
        if isDailyDataOk:
            logging.info("Grdf daily values are ok !")
            logging.info("Number of daily values retrieved : %s", dCount)
            for d in resDay:
                logging.info("%s : Energy = %s kwh, Gas = %s m3",d['date'],d['kwh'], d['mcube'])
        else:
            logging.info("Unable to get daily data from GRDF after %s tries",GRDF_API_MAX_RETRIES)
            hasGrdfFailed = True
                
    except:
        logging.error("Error on Step 3A")
        hasGrdfFailed = True
                 
    
    ## When daily data are ok
    if isDailyDataOk:
        
        ## STEP 3B : Get monthly data
        
        try:
            logging.info("Get monthly data from GRDF")

            # Set period (5 months ago)
            startDate = _getMonthOfssetDate(datetime.date.today(), 5)
            endDate = _dayToStr(datetime.date.today())

            # Get data and retry when failed
            i= 1
            mCount = 0
            isMonthlyDataOk = False

            while i <= GRDF_API_MAX_RETRIES:

                if i > 1:
                    logging.info("Failed. Please wait %s seconds for next try",GRDF_API_WAIT_BTW_RETRIES)
                    time.sleep(GRDF_API_WAIT_BTW_RETRIES)

                logging.info("Try number %s", str(i))
                
                ## Note : no need to relog to Grdf, we reuse the successful token used for daily data ;-)
                
                # Get result from GRDF by day
                try:
                    logging.info("Trying to get daily values from Grdf...")
                    resMonth = gazpar.get_data_per_month(token, startDate, endDate)
                except:
                    logging.error("Error to get Grdf monthly data")
                    i = i + 1
                    continue # next loop

                
                # Check data quality
                mCount = len(resMonth)
                if mCount <= GRDF_API_ERRONEOUS_COUNT:
                    logging.warning("Monthly values from GRDF seems wrong...")
                    i = i + 1
                    continue # next loop
                else:
                    isMonthlyDataOk = True
                    break # exit loop

            # Display results
            if isMonthlyDataOk:
                logging.info("Grdf monthly values are ok !")
                logging.info("Number of monthly values retrieved : %s", mCount)
                for m in resMonth:
                    logging.info("%s : Kwh = %s, Mcube = %s",m['date'],m['kwh'], m['mcube'])
            else:
                logging.info("Unable to get monthly data from GRDF after %s tries",GRDF_API_MAX_RETRIES)
                hasGrdfFailed = True

        except:
            logging.error("Error on Step 3B")
            hasGrdfFailed = True
    
    # Prepare data
    if not hasGrdfFailed:
        
        logging.info("Grdf data are correct")
        
        # Set flag
        hasGrdfFailed = False
        
    
    if not hasGrdfFailed:
    
        # STEP 4A : Standalone mode
        if mqtt.MQTT_IS_CONNECTED and params['standalone','mode']=="True":   

            try:

                logging.info("-----------------------------------------------------------")
                logging.info("Stand alone publication mode")
                logging.info("-----------------------------------------------------------")

                # Prepare topic
                prefixTopic = params['mqtt','topic']

                # Set values
                if hasGrdfFailed: # Values when Grdf failed

                    ## Publish status values
                    logging.info("Publishing to Mqtt status values...")
                    mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Failed", params['mqtt','qos'], params['mqtt','retain'])
                    logging.info("Status values published !")


                else: # Values when Grdf succeeded


                    # Publish daily values
                    logging.info("Publishing to Mqtt the last daily values...")
                    mqtt.publish(client, prefixTopic + TOPIC_DAILY_DATE, d1['date'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_DAILY_KWH, d1['kwh'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_DAILY_MCUBE, d1['mcube'], params['mqtt','qos'], params['mqtt','retain'])
                    
                    
                    logging.info("Daily values published !")

                    # Publish monthly values
                    logging.info("Publishing to Mqtt the last monthly values...")
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_DATE, m1['date'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH, m1['kwh'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH_TSH, m1['kwh_seuil'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH_PREV, m1['kwh_prec'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE, m1['mcube'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE_TSH, m1['mcube_seuil'], params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE_PREV, m1['mcube_prec'], params['mqtt','qos'], params['mqtt','retain'])
                    logging.info("Monthly values published !")

                    ## Publish status values
                    logging.info("Publishing to Mqtt status values...")
                    mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, params['mqtt','qos'], params['mqtt','retain'])
                    mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Success", params['mqtt','qos'], params['mqtt','retain'])
                    logging.info("Status values published !")

            except:
                logging.error("Standalone mode : unable to publish value to mqtt broker")
                sys.exit(1)

        # STEP 4B : Home Assistant discovery mode
        if params['hass','discovery'] == 'True':

            try:

                logging.info("-----------------------------------------------------------")
                logging.info("Home assistant publication mode")
                logging.info("-----------------------------------------------------------")

                # Set Hass sensors configuration
                logging.info("Update of Home Assistant sensors configurations...")
                mqtt.publish(client, hass.getConfigTopicSensor('daily_gas'), json.dumps(hass.getConfigPayload('daily_gas')), params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, hass.getConfigTopicSensor('monthly_gas'), json.dumps(hass.getConfigPayload('monthly_gas')), params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, hass.getConfigTopicSensor('daily_energy'), json.dumps(hass.getConfigPayload('daily_energy')), params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, hass.getConfigTopicSensor('monthly_energy'), json.dumps(hass.getConfigPayload('monthly_energy')), params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, hass.getConfigTopicSensor('consumption_date'), json.dumps(hass.getConfigPayload('consumption_date')), params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, hass.getConfigTopicSensor('consumption_month'), json.dumps(hass.getConfigPayload('consumption_month')), params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, hass.getConfigTopicBinary('connectivity'), json.dumps(hass.getConfigPayload('connectivity')), params['mqtt','qos'], params['mqtt','retain'])
                logging.info("Home assistant devices configurations updated !")

                if hasGrdfFailed: # Values when Grdf failed

                    logging.info("Update of Home Assistant binary sensors values...")
                    statePayload = {
                        "connectivity": 'OFF'
                        }
                    mqtt.publish(client, hass.getStateTopicBinary(), json.dumps(statePayload), params['mqtt','qos'], params['mqtt','retain'])
                    logging.info("Home Assistant binary sensors values updated !")

                else: # Values when Grdf succeeded                

                    # Publish Hass sensors values
                    logging.info("Update of Home assistant sensors values...")
                    statePayload = {
                        "daily_gas": d1['mcube'],
                        "monthly_gas": m1['mcube'],
                        "daily_energy": d1['kwh'],
                        "monthly_energy": m1['kwh'],
                        "consumption_date": d1['date'],
                        "consumption_month": m1['date'],
                        }
                    mqtt.publish(client, hass.getStateTopicSensor(), json.dumps(statePayload), params['mqtt','qos'], params['mqtt','retain'])
                    logging.info("Home Assistant sensors values updated !")

                    # Publish Hass binary sensors values
                    logging.info("Update of Home assistant binary sensors values...")
                    statePayload = {
                        "connectivity": 'ON'
                        }
                    mqtt.publish(client, hass.getStateTopicBinary(), json.dumps(statePayload), params['mqtt','qos'], params['mqtt','retain'])
                    logging.info("Home Assistant binary sensors values updated !")


            except:
                logging.error("Home Assistant discovery mode : unable to publish value to mqtt broker")
                sys.exit(1)
    
    
    # STEP 5 : Disconnect mqtt broker
    logging.info("-----------------------------------------------------------")
    logging.info("Disconnecion from MQTT")
    logging.info("-----------------------------------------------------------")
    
    if mqtt.MQTT_IS_CONNECTED:
        try:
            mqtt.disconnect(client)
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
    
    
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    
    logging.info("Welcome to gazpar2mqtt")
    logging.info("-----------------------------------------------------------")
    logging.info("-----------------------------------------------------------")
    
    # STEP 1 : Get params from args
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--grdf_username",    help="GRDF user name, ex : myemail@email.com")
    parser.add_argument(
        "--grdf_password",    help="GRDF password")
    parser.add_argument(
        "-s", "--schedule",   help="Schedule the launch of the script at hh:mm everyday")
    parser.add_argument(
        "--mqtt_host",        help="Hostname or ip adress of the Mqtt broker")
    parser.add_argument(
        "--mqtt_port",        help="Port of the Mqtt broker")
    parser.add_argument(
        "--mqtt_clientId",    help="Client Id to connect to the Mqtt broker")
    parser.add_argument(
        "--mqtt_username",    help="Username to connect to the Mqtt broker")
    parser.add_argument(
        "--mqtt_password",    help="Password to connect to the Mqtt broker")
    parser.add_argument(
        "--mqtt_qos",         help="QOS of the messages to be published to the Mqtt broker")
    parser.add_argument(
        "--mqtt_topic",       help="Topic prefix of the messages to be published to the Mqtt broker")
    parser.add_argument(
        "--mqtt_retain",      help="Retain flag of the messages to be published to the Mqtt broker, possible values : True or False")
    parser.add_argument(
        "--standalone_mode",  help="Enable standalone publication mode, possible values : True or False")
    parser.add_argument(
        "--hass_discovery",   help="Enable Home Assistant discovery, possible values : True or False")
    parser.add_argument(
        "--hass_prefix",      help="Home Assistant discovery Mqtt topic prefix")
    
    args = parser.parse_args()
    
    
    # STEP 2 : Get params from environment OS
    params = _getEnvParams()
    
    
    # STEP 3 :  Overwrite for declared args
    if args.grdf_username is not None: params['grdf','username']=args.grdf_username
    if args.grdf_password is not None: params['grdf','password']=args.grdf_password
    if args.schedule is not None: params['schedule','time']=args.schedule
    if args.mqtt_host is not None: params['mqtt','host']=args.mqtt_host
    if args.mqtt_port is not None: params['mqtt','port']=int(args.mqtt_port)
    if args.mqtt_clientId is not None: params['mqtt','clientId']=args.mqtt_clientId
    if args.mqtt_username is not None: params['mqtt','username']=args.mqtt_username
    if args.mqtt_password is not None: params['mqtt','password']=args.mqtt_password
    if args.mqtt_qos is not None: params['mqtt','qos']=int(args.mqtt_qos)
    if args.mqtt_topic is not None: params['mqtt','topic']=args.mqtt_topic
    if args.mqtt_retain is not None: params['mqtt','retain']=args.mqtt_retain
    if args.standalone_mode is not None: params['standalone','mode']=args.standalone_mode
    if args.hass_discovery is not None: params['hass','discovery']=args.hass_discovery
    if args.hass_prefix is not None: params['hass','prefix']=args.hass_prefix
    
    # STEP 4 : Log params info
    logging.info("-----------------------------------------------------------")
    logging.info("Program parameters")
    logging.info("-----------------------------------------------------------")
    logging.info("GRDF config : username = %s, password = %s", params['grdf','username'], "******")
    logging.info("MQTT broker config : host = %s, port = %s, clientId = %s, qos = %s, topic = %s, retain = %s", \
                 params['mqtt','host'], params['mqtt','port'], params['mqtt','clientId'], \
                 params['mqtt','qos'],params['mqtt','topic'],params['mqtt','retain'])
    logging.info("Standlone mode : Enable = %s", params['standalone','mode'])
    logging.info("Home Assistant discovery : Enable = %s, Topic prefix = %s", \
                 params['hass','discovery'], params['hass','prefix'])

    # STEP 5 : Run
    if params['schedule','time'] is not None:
        
        # Run once at lauch
        run(params)

        # Then run at scheduled time
        schedule.every().day.at(params['schedule','time']).do(run,params)
        while True:
            schedule.run_pending()
            time.sleep(1)
        logging.info("End of gazpar2mqtt. See u...")
        
    else:
        
        # Run once
        run(params)
        logging.info("End of gazpar2mqtt. See u...")
