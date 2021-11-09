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
TOPIC_DAILY_DELTA = "/daily/delta"

## Monthly
TOPIC_MONTHLY_DATE = "/monthly/month"
TOPIC_MONTHLY_KWH = "/monthly/kwh"
TOPIC_MONTHLY_MCUBE = "/monthly/mcube"
TOPIC_MONTHLY_DELTA = "/monthly/delta"

## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"


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
    
    # Check and get manadatory environment parameters
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
        
    if not "HASS_AUTODISCOVERY" in os.environ:
        params['hass','autodiscovery'] = 'False'
    else:
        params['hass','autodiscovery'] = os.environ['HASS_AUTODISCOVERY']
    
    if not "HASS_PREFIX" in os.environ:
        params['hass','prefix'] = 'False'
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
#### Main program
#######################################################################
def run(params):
    
    # Store time now
    dtn = _dateTimeToStr(datetime.datetime.now())
    
    # STEP 2 : Log to MQTT broker
    try:
        
        logging.info("Connection to Mqtt broker...")
        
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
        logging.error("Unable to connect to mqtt broker. Please check that broker is running, or check broker configuration.")
        sys.exit(1)
    
    
    
    # STEP 3 : Get data from GRDF API
    
    ## STEP 3A : Get daily data
    try:
        logging.info("Get daily data from GRDF")
                     
        # Set period (5 days ago)
        startDate = _getDayOfssetDate(datetime.date.today(), 5)
        endDate = _dayToStr(datetime.date.today())
        
        # Get data and retry when failed
        i= 1
        dCount = 0
        
        while i <= GRDF_API_MAX_RETRIES and dCount <= GRDF_API_ERRONEOUS_COUNT:
        
            if i > 1:
                logging.info("Failed. Please wait %s seconds for next try",GRDF_API_WAIT_BTW_RETRIES)
                time.sleep(GRDF_API_WAIT_BTW_RETRIES)
                
            logging.info("Try number %s", str(i))
            
            # Log to Grdf
            token = _log_to_Grdf(params['grdf','username'], params['grdf','password'])
            
            # Get result from GRDF by day
            resDay = gazpar.get_data_per_day(token, startDate, endDate)
            
            # Update loop conditions
            i = i + 1
            dCount = len(resDay)

        # Display infos
        if dCount <= GRDF_API_ERRONEOUS_COUNT:
            logging.warning("Daily values from GRDF seems wrong...")
        else:
            logging.info("Number of daily values retrieved : %s", dCount)
        
        # Display results
        for d in resDay:
            logging.info("%s : Energy = %s kwh, Gas = %s m3",d['date'],d['kwh'], d['mcube'])
                
    except:
        logging.error("Unable to get daily data from GRDF")
        sys.exit(1)
                 
    
    ## When daily data are ok
    if dCount > GRDF_API_ERRONEOUS_COUNT:
        
        ## STEP 3B : Get monthly data
        
        try:
            logging.info("Get monthly data from GRDF")

            # Set period (5 months ago)
            startDate = _getMonthOfssetDate(datetime.date.today(), 5)
            endDate = _dayToStr(datetime.date.today())

            # Get data and retry when failed
            i= 1
            mCount = 0

            while i <= GRDF_API_MAX_RETRIES and mCount <= GRDF_API_ERRONEOUS_COUNT:

                if i > 1:
                    logging.info("Failed. Please wait %s seconds for next try",GRDF_API_WAIT_BTW_RETRIES)
                    time.sleep(GRDF_API_WAIT_BTW_RETRIES)

                logging.info("Try number %s", str(i))
                
                ## Note : no need to relog to Grdf, we reuse the successful token used for daily data ;-)
                
                # Get result from GRDF by day
                resMonth = gazpar.get_data_per_month(token, startDate, endDate)

                # Update loop conditions
                i = i + 1
                mCount = len(resMonth)

            # Display infos
            if mCount <= GRDF_API_ERRONEOUS_COUNT:
                logging.warning("Monthly values from GRDF seems wrong...")
            else:
                logging.info("Number of monthly values retrieved : %s", mCount)

            # Display results
            for m in resMonth:
                logging.info("%s : Kwh = %s, Mcube = %s",m['date'],m['kwh'], m['mcube'])         

        except:
            logging.error("Unable to get monthly data from GRDF")
            sys.exit(1)
    
    
    # STEP 4 : Check data quality and prepare values
    
    if dCount <= GRDF_API_ERRONEOUS_COUNT and dCount > 1: # Unfortunately, GRDF date are not correct
        
        # Set flag
        hasGrdfFailed = True
        
    else: # GRDF date are correct
        
        # Set flag
        hasGrdfFailed = False
        
        # Get GRDF -1 values
        d1 = resDay[dCount-1]
        m1 = resMonth[mCount-1]

        # Get GRDF -2 values
        d2 = resDay[dCount-2]
        m2 = resMonth[mCount-2]

        # Calculate delta in %
        if d2['mcube'] is None or d2['mcube'] == '0':
            d1['delta'] = 0
        else:
            d1['delta'] = round((( d1['mcube'] - d2['mcube'] ) / d2['mcube']) * 100,2)
        if m2['mcube'] is None or m2['mcube'] == '0':
            m1['delta'] = 0
        else:
            m1['delta'] = round((( m1['mcube'] - m2['mcube'] ) / m2['mcube']) * 100,2)
        
        
    
    # STEP 5A : Standalone mode
    if mqtt.MQTT_IS_CONNECTED and 1 == 2:   

        try:

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
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_DELTA, d1['delta'], params['mqtt','qos'], params['mqtt','retain'])
                logging.info("Daily values published !")

                # Publish monthly values
                logging.info("Publishing to Mqtt the last monthly values...")
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_DATE, m1['date'], params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH, m1['kwh'], params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE, m1['mcube'], params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_DELTA, m1['delta'], params['mqtt','qos'], params['mqtt','retain'])
                logging.info("Monthly values published !")

                ## Publish status values
                logging.info("Publishing to Mqtt status values...")
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, params['mqtt','qos'], params['mqtt','retain'])
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Success", params['mqtt','qos'], params['mqtt','retain'])
                logging.info("Status values published !")

        except:
            logging.error("Standalone mode : unable to publish value to mqtt broker")
            sys.exit(1)
    
    # STEP 5B : Home Assistant discovery mode
    if params['hass','autodiscovery'] and mqtt.MQTT_IS_CONNECTED:

        #try:
            
            # Set Hass sensors configuration
            logging.info("Update of Home Assistant sensors configurations...")
            mqtt.publish(client, json.dumps(hass.getConfigTopic('daily_gas')), json.dumps(hass.getConfigPayload('daily_gas')), params['mqtt','qos'], params['mqtt','retain'])
            #mqtt.publish(client, hass.getConfigTopic, hass.getConfigPayload('monthly_gas'), params['mqtt','qos'], params['mqtt','retain'])
            #mqtt.publish(client, hass.getConfigTopic, hass.getConfigPayload('daily_energy'), params['mqtt','qos'], params['mqtt','retain'])
            #mqtt.publish(client, hass.getConfigTopic, hass.getConfigPayload('monthly_energy'), params['mqtt','qos'], params['mqtt','retain'])
            #mqtt.publish(client, hass.getConfigTopic, hass.getConfigPayload('consumption_date'), params['mqtt','qos'], params['mqtt','retain'])
            #mqtt.publish(client, hass.getConfigTopic, hass.getConfigPayload('consumption_month'), params['mqtt','qos'], params['mqtt','retain'])
            #mqtt.publish(client, hass.getConfigTopic, hass.getConfigPayload('connectivity'), params['mqtt','qos'], params['mqtt','retain'])
            logging.info("Home assistant devices configurations updated !")
            
            # Check data quality
            if hasGrdfFailed: # Values when Grdf failed
                
                logging.info("Update of Home Assistant sensors values...")
                statePayload = {
                    "connectivity": 'OFF'
                    }
                #mqtt.publish(client, hass.getStateTopic, statePayload, params['mqtt','qos'], params['mqtt','retain'])
                logging.info("Home Assistant sensors values updated !")
            
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
                    "connectivity": 'ON'
                    }
                #mqtt.publish(client, hass.getStateTopic, statePayload, params['mqtt','qos'], params['mqtt','retain'])
                logging.info("Home Assistant sensors values updated !")
                

        #except:
        #    logging.error("Home Assistant discovery mode : unable to publish value to mqtt broker")
        #    sys.exit(1)
    
    else:
        logging.error("Unable to publish value to mqtt broker cause it seems to be disconnected")
        sys.exit(1)
    
    
    # STEP 5 : Disconnect mqtt broker
    if mqtt.MQTT_IS_CONNECTED:
        try:
            mqtt.disconnect(client)
            logging.info("Mqtt broker disconnected")
        except:
            logging.error("Unable to disconnect mqtt broker")
            sys.exit(1)
    
    # Game over
    if params['schedule','time'] is not None: 
        logging.info("gazpar2mqtt next run scheduled at %s",params['schedule','time'])
    else: 
        logging.info("End of gazpar2mqtt. See u...")
        
        
        
                
if __name__ == "__main__":
    
    
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    
    # STEP 1 : Get params from args
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "--grdf_username",   help="GRDF user name, ex : myemail@email.com")
    parser.add_argument(
        "--grdf_password",   help="GRDF password")
    parser.add_argument(
        "-s", "--schedule",   help="Schedule the launch of the script at hh:mm everyday")
    parser.add_argument(
        "--mqtt_host",   help="Hostname or ip adress of the Mqtt broker")
    parser.add_argument(
        "--mqtt_port",   help="Port of the Mqtt broker")
    parser.add_argument(
        "--mqtt_clientId",   help="Client Id to connect to the Mqtt broker")
    parser.add_argument(
        "--mqtt_username",   help="Username to connect to the Mqtt broker")
    parser.add_argument(
        "--mqtt_password",   help="Password to connect to the Mqtt broker")
    parser.add_argument(
        "--mqtt_qos",   help="QOS of the messages to be published to the Mqtt broker")
    parser.add_argument(
        "--mqtt_topic",   help="Topic prefix of the messages to be published to the Mqtt broker")
    parser.add_argument(
        "--mqtt_retain",   help="Retain flag of the messages to be published to the Mqtt broker, possible values : True or False")
    parser.add_argument(
        "--hass_autodiscovery",   help="Enable Home Assistant autodiscovery, possible values : True or False")
    parser.add_argument(
        "--hass_prefix",   help="Home Assistant autodiscovery Mqtt topic prefix")
    
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
    if args.hass_autodiscovery is not None: params['hass','autodiscovery']=args.hass_autodiscovery
    if args.hass_prefix is not None: params['hass','prefix']=args.hass_prefix
    
    # STEP 4 : Log params info         
    logging.info("GRDF config : username = %s, password = %s", params['grdf','username'], "******")
    logging.info("Schedule : time = %s", params['schedule','time'])
    logging.info("MQTT config : host = %s, port = %s, clientId = %s, qos = %s, topic = %s, retain = %s", \
                 params['mqtt','host'], params['mqtt','port'], params['mqtt','clientId'], \
                 params['mqtt','qos'],params['mqtt','topic'],params['mqtt','retain'])
    logging.info("Home Assistant config : Enable = %s, Topic prefix = %s", \
                 params['hass','autodiscovery'], params['hass','prefix'])

    # STEP 5 : Run
    if params['schedule','time'] is not None:
        logging.info("gazpar2mqtt next run scheduled at %s",params['schedule','time'])
        schedule.every().day.at(params['schedule','time']).do(run,params)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        run(params)
