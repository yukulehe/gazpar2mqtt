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
import json

import argparse
import logging
import pprint
from envparse import env

# OS environment variables
PFILE = "/.params"
DOCKER_MANDATORY_VARENV=['GRDF_USERNAME','GRDF_PASSWORD','MQTT_HOST']
DOCKER_OPTIONAL_VARENV=['MQTT_PORT','MQTT_CLIENTID','MQTT_USERNAME','MQTT_PASSWORD','MQTT_QOS', 'MQTT_TOPIC', 'MQTT_RETAIN']

# Grdf API constants
GRDF_API_MAX_RETRIES = 5 # number of retries max to get accurate data from GRDF
GRDF_API_WAIT_BTW_RETRIES = 10 # number of seconds between two tries
GRDF_API_ERRONEOUS_COUNT = 1 # Erroneous number of results send by GRDF 

# Sensors topics

## Daily
TOPIC_DAILY_DATE = "/daily/date"
TOPIC_DAILY_KWH = "/daily/kwh"
TOPIC_DAILY_MCUBE = "/daily/mcube"

## Monthly
TOPIC_MONTHLY_DATE = "/monthly/month"
TOPIC_MONTHLY_KWH = "/monthly/kwh"
TOPIC_MONTHLY_MCUBE = "/monthly/mcube"

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
        #params['grdf']['username'] = os.environ['GRDF_USERNAME']
        params.put('grdf_username') = os.environ['GRDF_USERNAME']
        
    if not "GRDF_PASSWORD" in os.environ:
        logging.error("Environement variable 'GRDF_USERNAME' is mandatory")
        quit()
    else:
        params['grdf']['password'] = os.environ['GRDF_PASSWORD']
        
    if not "MQTT_HOST" in os.environ:
        logging.error("Environement variable 'MQTT_HOST' is mandatory")
        quit()
    else:
        params['mqtt']['host'] = os.environ['MQTT_HOST']
        
    # Check and get optional environment parameters
    
    if not "SCHEDULE_TIME" in os.environ:
        params['schedule']['time'] = '04:00'
    else:
        params['schedule']['time'] = os.environ['SCHEDULE_TIME']
        
    if not "MQTT_PORT" in os.environ:
        params['mqtt']['port'] = 1883
    else:
        params['mqtt']['port'] = int(os.environ['MQTT_PORT'])
        
    if not "MQTT_CLIENTID" in os.environ:
        params['mqtt']['clientId'] = 'gazpar2mqtt'
    else:
        params['mqtt']['clientId'] = os.environ['MQTT_CLIENTID']
    
    if not "MQTT_USERNAME" in os.environ:
        params['mqtt']['username'] = ''
    else:
        params['mqtt']['username'] = os.environ['MQTT_USERNAME']
    
    if not "MQTT_PASSWORD" in os.environ:
        params['mqtt']['password'] = ''
    else:
        params['mqtt']['password'] = os.environ['MQTT_PASSWORD']
        
    if not "MQTT_QOS" in os.environ:
        params['mqtt']['qos'] = 1
    else:
        params['mqtt']['qos'] = int(os.environ['MQTT_QOS'])
        
    if not "MQTT_TOPIC" in os.environ:
        params['mqtt']['topic'] = 'gazpar'
    else:
        params['mqtt']['topic'] = os.environ['MQTT_TOPIC']
        
    if not "MQTT_RETAIN" in os.environ:
        params['mqtt']['retain'] = 'False'
    else:
        params['mqtt']['retain'] = os.environ['MQTT_RETAIN']
    
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

# Main program
def run(params):
    
    # Store time now
    dtn = _dateTimeToStr(datetime.datetime.now())
    
    # STEP 2 : Log to MQTT broker
    try:
        
        logging.info("Connection to Mqtt broker...")
        
        # Construct mqtt client
        client = mqtt.create_client(params['mqtt']['clientId'],params['mqtt']['username'],params['mqtt']['password'])
    
        # Connect mqtt brocker
        mqtt.connect(client,params['mqtt']['host'],params['mqtt']['port'])
        
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
            token = _log_to_Grdf(params['grdf']['username'], params['grdf']['password'])
            
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
            logging.info("%s : Kwh = %s, Mcube = %s",d['date'],d['kwh'], d['mcube'])
                
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
    
    
    
    # STEP 4 : We publish only the last input from grdf
    if mqtt.MQTT_IS_CONNECTED:   

        try:

            # Prepare topic
            prefixTopic = params['mqtt']['topic']
            
            if dCount <= GRDF_API_ERRONEOUS_COUNT: # Unfortunately, GRDF date are not correct

                ## Publish status values
                logging.info("Publishing to Mqtt status values...")
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, params['mqtt']['qos'], params['mqtt']['retain'])
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Failed", params['mqtt']['qos'], params['mqtt']['retain'])
                logging.info("Status values published !")

            
            else: # Looks good ...

                # Get GRDF last values
                d = resDay[dCount-1]
                m = resMonth[mCount-1]
                
                # Publish daily values
                logging.info("Publishing to Mqtt the last daily values...")
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_DATE, d['date'], params['mqtt']['qos'], params['mqtt']['retain'])
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_KWH, d['kwh'], params['mqtt']['qos'], params['mqtt']['retain'])
                mqtt.publish(client, prefixTopic + TOPIC_DAILY_MCUBE, d['mcube'], params['mqtt']['qos'], params['mqtt']['retain'])
                logging.info("Daily values published !")

                # Publish monthly values
                logging.info("Publishing to Mqtt the last monthly values...")
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_DATE, m['date'], params['mqtt']['qos'], params['mqtt']['retain'])
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_KWH, m['kwh'], params['mqtt']['qos'], params['mqtt']['retain'])
                mqtt.publish(client, prefixTopic + TOPIC_MONTHLY_MCUBE, m['mcube'], params['mqtt']['qos'], params['mqtt']['retain'])
                logging.info("Monthly values published !")

                ## Publish status values
                logging.info("Publishing to Mqtt status values...")
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_DATE, dtn, params['mqtt']['qos'], params['mqtt']['retain'])
                mqtt.publish(client, prefixTopic + TOPIC_STATUS_VALUE, "Success", params['mqtt']['qos'], params['mqtt']['retain'])
                logging.info("Status values published !")

        except:
            logging.error("Unable to publish value to mqtt broker")
            sys.exit(1)
            
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
    
    args = parser.parse_args()
    
    
    # STEP 2 : Get params from environment OS
    params = _getEnvParams()
    
    
    # STEP 3 :  Overwrite for declared args
    if args.grdf_username is not None: params['grdf']['username']=args.grdf_username
    if args.grdf_password is not None: params['grdf']['password']=args.grdf_password
    if args.mqtt_host is not None: params['mqtt']['host']=args.mqtt_host
    if args.mqtt_port is not None: params['mqtt']['port']=int(args.mqtt_port)
    if args.mqtt_clientId is not None: params['mqtt']['clientId']=args.mqtt_clientId
    if args.mqtt_username is not None: params['mqtt']['username']=args.mqtt_username
    if args.mqtt_password is not None: params['mqtt']['password']=args.mqtt_password
    if args.mqtt_qos is not None: params['mqtt']['qos']=int(args.mqtt_qos)
    if args.mqtt_topic is not None: params['mqtt']['topic']=args.mqtt_topic
    if args.mqtt_retain is not None: params['mqtt']['retain']=args.mqtt_retain
    
    # STEP 4 : Log params info         
    logging.info("GRDF config : username = %s, password = %s", params['grdf']['username'], "******")
    logging.info("MQTT config : host = %s, port = %s, clientId = %s, qos = %s, topic = %s, retain = %s", \
                 params['mqtt']['host'], params['mqtt']['port'], params['mqtt']['clientId'], \
                 params['mqtt']['qos'],params['mqtt']['topic'],params['mqtt']['retain'])

    # STEP 5 : Run
    if params['mqtt']['host'] is not None:
        logging.info("qazpar2mqtt run is scheduled at %s everyday",params['schedule']['time'])
        schedule.every().day.at(params['schedule']['time']).do(run(params))
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        run(params)
