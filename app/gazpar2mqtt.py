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
import gazpar2
import mqtt
import hass
import json
import requests
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
TOPIC_MONTHLY_MCUBE_PREV = "/monthly/kwh/previous"


## Status
TOPIC_STATUS_DATE = "/status/date"
TOPIC_STATUS_VALUE = "/status/value"

# Hass global
HASS_AUTODISCOVERY_PREFIX = None
HASS_DEVICE_NAME = None

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
        client = mqtt.create_client(params['mqtt','clientId'],params['mqtt','username'],params['mqtt','password'],params['mqtt','ssl'])
    
        # Connect mqtt brocker
        mqtt.connect(client,params['mqtt','host'],params['mqtt','port'])
        
        # Wait mqtt callback (connection confirmation)
        time.sleep(2)
        
        if mqtt.MQTT_IS_CONNECTED:
            logging.info("Mqtt broker connected !")
        
    except:
        logging.error("Unable to connect to Mqtt broker. Please check that broker is running, or check broker configuration.")
        
    
    
    
    # STEP 3 : Get data from GRDF website
    
    session = requests.Session()
    
    session = gazpar2.login(params['grdf','username'],params['grdf','password'])
    hasGrdfFailed = True
    
    
    # Prepare data
    if not hasGrdfFailed:
        
        logging.info("Grdf data are correct")
        
        # Set flag
        hasGrdfFailed = False
        
        # Get GRDF last values
        d1 = resDay[dCount-1]
        m1 = resMonth[mCount-1]

    

    # STEP 4A : Standalone mode
    if mqtt.MQTT_IS_CONNECTED and params['standalone','mode'].lower()=="true":   

        try:

            logging.info("-----------------------------------------------------------")
            logging.info("Stand alone publication mode")
            logging.info("-----------------------------------------------------------")

            # Set variables
            prefixTopic = params['mqtt','topic']
            retain = params['mqtt','retain']
            qos = params['mqtt','qos']

            # Set values
            if hasGrdfFailed: # Values when Grdf failed

                ## Publish status values
                logging.info("Publishing to Mqtt status values...")
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Failed", qos, retain)
                logging.info("Status values published !")


            else: # Values when Grdf succeeded


                # Publish daily values
                logging.info("Publishing to Mqtt the last daily values...")
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_DATE, d1['date'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_KWH, d1['kwh'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_MCUBE, d1['mcube'], qos, retain)

                logging.info("Daily values published !")

                # Publish monthly values
                logging.info("Publishing to Mqtt the last monthly values...")
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_DATE, m1['date'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH, m1['kwh'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH_TSH, m1['kwh_seuil'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH_PREV, m1['kwh_prec'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE, m1['mcube'], qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE_PREV, m1['mcube_prec'], qos, retain)
                logging.info("Monthly values published !")

                ## Publish status values
                logging.info("Publishing to Mqtt status values...")
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, qos, retain)
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Success", qos, retain)
                logging.info("Status values published !")

        except:
            logging.error("Standalone mode : unable to publish value to mqtt broker")
            sys.exit(1)

    # STEP 4B : Home Assistant discovery mode
    if mqtt.MQTT_IS_CONNECTED and params['hass','discovery'].lower() == 'true':

        try:

            logging.info("-----------------------------------------------------------")
            logging.info("Home assistant publication mode")
            logging.info("-----------------------------------------------------------")

            # Set variables
            retain = params['mqtt','retain']
            qos = params['mqtt','qos']
            ha_prefix = params['hass','prefix']
            device_name = params['hass','device_name']

            # Set Hass sensors configuration
            logging.info("Update of Home Assistant configurations...")
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'daily_gas'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'daily_gas')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'monthly_gas'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'monthly_gas')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'monthly_gas_prev'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'monthly_gas_prev')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'daily_energy'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'daily_energy')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'monthly_energy'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'monthly_energy')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'monthly_energy_tsh'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'monthly_energy_tsh')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'monthly_energy_prev'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'monthly_energy_prev')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'consumption_date'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'consumption_date')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicSensor(ha_prefix,device_name,'consumption_month'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'consumption_month')), qos, retain)
            mqtt.publish(client, hass.getConfigTopicBinary(ha_prefix,device_name,'connectivity'), json.dumps(hass.getConfigPayload(ha_prefix,device_name,'connectivity')), qos, retain)
            logging.info("Home assistant configurations updated !")

            if hasGrdfFailed: # Values when Grdf failed

                logging.info("Update of Home Assistant binary sensors values...")
                statePayload = {
                    "connectivity": 'OFF'
                    }
                mqtt.publish(client, hass.getStateTopicBinary(ha_prefix,device_name), json.dumps(statePayload), qos, retain)
                logging.info("Home Assistant binary sensors values updated !")

            else: # Values when Grdf succeeded                

                # Publish Hass sensors values
                logging.info("Update of Home assistant sensors values...")
                statePayload = {
                    "daily_gas": d1['mcube'],
                    "monthly_gas": m1['mcube'],
                    "monthly_gas_prev": m1['mcube_prec'],
                    "daily_energy": d1['kwh'],
                    "monthly_energy": m1['kwh'],
                    "monthly_energy_tsh": m1['kwh_seuil'],
                    "monthly_energy_prev": m1['kwh_prec'],
                    "consumption_date": d1['date'],
                    "consumption_month": m1['date'],
                    }
                mqtt.publish(client, hass.getStateTopicSensor(ha_prefix,device_name), json.dumps(statePayload), qos, retain)
                logging.info("Home Assistant sensors values updated !")

                # Publish Hass binary sensors values
                logging.info("Update of Home assistant binary sensors values...")
                statePayload = {
                    "connectivity": 'ON'
                    }
                mqtt.publish(client, hass.getStateTopicBinary(ha_prefix,device_name), json.dumps(statePayload), qos, retain)
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
        "--mqtt_ssl",      help="Enable MQTT SSL connexion, possible values : True or False")
    parser.add_argument(
        "--standalone_mode",  help="Enable standalone publication mode, possible values : True or False")
    parser.add_argument(
        "--hass_discovery",   help="Enable Home Assistant discovery, possible values : True or False")
    parser.add_argument(
        "--hass_prefix",      help="Home Assistant discovery Mqtt topic prefix")
    parser.add_argument(
        "--hass_device_name",      help="Home Assistant device name")
    
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
    if args.mqtt_ssl is not None: params['mqtt','ssl']=args.mqtt_ssl
    if args.standalone_mode is not None: params['standalone','mode']=args.standalone_mode
    if args.hass_discovery is not None: params['hass','discovery']=args.hass_discovery
    if args.hass_prefix is not None: params['hass','prefix']=args.hass_prefix
    if args.hass_device_name is not None: params['hass','device_name']=args.hass_device_name
        
    # STEP 4 : Check mandatory parameters (fix issue #12)
    if params['grdf','username'] is None:
        logging.error("Parameter GRDF username is mandatory.")
        quit()
    if params['grdf','password'] is None:
        logging.error("Parameter GRDF password is mandatory.")
        quit()
    if params['mqtt','host'] is None:
        logging.error("Parameter MQTT host is mandatory.")
        quit()
    if params['standalone','mode'] is False and params['hass','discovery'] is False:
        logging.warning("Both Standalone mode and Home assistant discovery are disable. No value will be published to MQTT ! Please check your parameters.")
    
    # STEP 5 : Log params info
    logging.info("-----------------------------------------------------------")
    logging.info("Program parameters")
    logging.info("-----------------------------------------------------------")
    logging.info("GRDF config : username = %s, password = %s", "******@****.**", "******")
    logging.info("MQTT broker config : host = %s, port = %s, clientId = %s, qos = %s, topic = %s, retain = %s, ssl = %s", \
                 params['mqtt','host'], params['mqtt','port'], params['mqtt','clientId'], \
                 params['mqtt','qos'],params['mqtt','topic'],params['mqtt','retain'], \
                 params['mqtt','ssl']),
    logging.info("Standlone mode : Enable = %s", params['standalone','mode'])
    logging.info("Home Assistant discovery : Enable = %s, Topic prefix = %s, Device name = %s", \
                 params['hass','discovery'], params['hass','prefix'], params['hass','device_name'])

    # STEP 6 : Run
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
