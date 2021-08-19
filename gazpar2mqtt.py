#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Work in progress...

import os
import sys
import datetime
#import schedule
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
DOCKER_OPTIONAL_VARENV=['MQTT_PORT','MQTT_CLIENTID','MQTT_QOS', 'MQTT_TOPIC', 'MQTT_RETAIN']

# Sensors topics

## Daily
dailyValueDateTopic = "/daily/date"
dailyValueKwhTopic = "/daily/kwh"
dailyValueMcubeTopic = "/daily/mcube"

## Monthly
monthlyValueDateTopic = "/monthly/month"
monthlyValueKwhTopic = "/monthly/kwh"
monthlyValueMcubeTopic = "/monthly/mcube"

## Status
statusDateTopic = "/status/date"
statusValueTopic = "/status/value"


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

  
# Open file with params for mqtt broker and GRDF API
def _openParams(pfile):
    
    # Try to load environment variables
    if set(DOCKER_MANDATORY_VARENV).issubset(set(os.environ)):
        return {'grdf': {'username': env(DOCKER_MANDATORY_VARENV[0]),
                         'password': env(DOCKER_MANDATORY_VARENV[1])},
                'mqtt': {'host': env(DOCKER_MANDATORY_VARENV[2]),
                           'port': env.int(DOCKER_OPTIONAL_VARENV[0], default=1883),
                           'clientId': env(DOCKER_OPTIONAL_VARENV[1], default='gazpar2mqtt'),
                           'qos': env.int(DOCKER_OPTIONAL_VARENV[2],default=1),
                           'topic': env(DOCKER_OPTIONAL_VARENV[3], default='gazpar'),
                           'retain': env(DOCKER_OPTIONAL_VARENV[4], default=False).lower in ("true","True","TRUE","1","false","False","FALSE","0") }}
    
    # Try to load .params then programs_dir/.params
    elif os.path.isfile(os.getcwd() + pfile):
        p = os.getcwd() + pfile
    elif os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + pfile):
        p = os.path.dirname(os.path.realpath(__file__)) + pfile
    else:
        if (os.getcwd() + pfile != os.path.dirname(os.path.realpath(__file__)) + pfile):
            logging.error('file %s or %s not exist', os.path.realpath(os.getcwd() + pfile) , os.path.dirname(os.path.realpath(__file__)) + pfile)
        else:
            logging.error('file %s not exist', os.getcwd() + pfile )
        sys.exit(1)
    try:
        f = open(p, 'r')
        try:
            array = json.load(f)
        except ValueError as e:
            logging.error('decoding JSON has failed', e)
            sys.exit(1)
    except IOError:
        logging.error('cannot open %s', p)
        sys.exit(1)
    else:
        f.close()
        return array

                

# Let's start here !

def main():
    
    # Store time now
    dtn = _dateTimeToStr(datetime.datetime.now())
    
    # Get params from environment OS
    params = _openParams(PFILE)
                
    logging.info("GRDF config : username = %s, password = %s", params['grdf']['username'], params['grdf']['password'])
    logging.info("MQTT config : host = %s, port = %s, clientId = %s, qos = %s, topic = %s, retain = %s", \
                 params['mqtt']['host'], params['mqtt']['port'], params['mqtt']['clientId'], \
                 params['mqtt']['qos'],params['mqtt']['topic'],params['mqtt']['retain'])
    
    
    # Create mqtt client
    client = mqtt.create_client(params['mqtt']['clientId'])
    logging.info("Mqtt client instantiated")
    
    # Connect mqtt brocker
    mqtt.connect(client,params['mqtt']['host'],params['mqtt']['port'])
    logging.info("Mqtt broker connected")
    
    
    # Log to GRDF API
    try:
        logging.info("logging in GRDF URI %s...", gazpar.API_BASE_URI)
        token = gazpar.login(params['grdf']['username'], params['grdf']['password'])
        logging.info("logged in successfully!")
    except:
        logging.error("unable to login on %s", gazpar.API_BASE_URI)
        sys.exit(1)
    
    
    # Wait
    time.sleep(2)
    
    # Get data from GRDF API
    
    ## Get daily data
    try:
        logging.info("Get daily data from GRDF")
                     
        # Set period (5 days ago)
        startDate = _getDayOfssetDate(datetime.date.today(), 5)
        endDate = _dayToStr(datetime.date.today())
        
        # Get result from GRDF by day
        resDay = gazpar.get_data_per_day(token, startDate, endDate)
        
        # Display daily results
        dCount = len(resDay)
        logging.info("Number of daily values : %s", dCount)
        for d in resDay:
            logging.info("%s : Kwh = %s, Mcube = %s",d['date'],d['kwh'], d['mcube'])
                
    except:
        logging.error("Unable to get daily data from GRDF")
        sys.exit(1)
                 
    
    ## Get monthly data
    try:
        logging.info("Get monthly data from GRDF")
        
        # Set period (5 months ago)
        startDate = _getMonthOfssetDate(datetime.date.today(), 5)
        endDate = _dayToStr(datetime.date.today())
                     
        # Get result from GRDF by day
        resMonth = gazpar.get_data_per_month(token, startDate, endDate)
        
        # Display monthly results
        mCount = len(resMonth)
        logging.info("Number of monthly values : %s", mCount)
        for m in resMonth:
            logging.info("%s : Kwh = %s, Mcube = %s",m['date'],m['kwh'], m['mcube'])
                
    except:
        logging.error("Unable to get monthly data from GRDF")
        sys.exit(1)
    
    
    # We publish only the last input from grdf
    d = resDay[dCount-1]
    m = resMonth[mCount-1]
    prefixTopic = params['mqtt']['topic']
    
    try:
        
        # Unfortunately, GRDF date are not correct
        if dCount == 1 or mCount == 1:

            ## Publish status values
            mqtt.publish(client, prefixTopic + statusDateTopic, dtn, params['mqtt']['qos'], params['mqtt']['retain'])
            mqtt.publish(client, prefixTopic + statusValueTopic, "Error", params['mqtt']['qos'], params['mqtt']['retain'])

        # Looks good ...
        else:

            # Publish daily values
            mqtt.publish(client, prefixTopic + dailyValueDateTopic, d['date'], params['mqtt']['qos'], params['mqtt']['retain'])
            mqtt.publish(client, prefixTopic + dailyValueKwhTopic, d['kwh'], params['mqtt']['qos'], params['mqtt']['retain'])
            mqtt.publish(client, prefixTopic + dailyValueMcubeTopic, d['mcube'], params['mqtt']['qos'], params['mqtt']['retain'])

            # Publish monthly values
            mqtt.publish(client, prefixTopic + monthlyValueDateTopic, m['date'], params['mqtt']['qos'], params['mqtt']['retain'])
            mqtt.publish(client, prefixTopic + monthlyValueKwhTopic, m['kwh'], params['mqtt']['qos'], params['mqtt']['retain'])
            mqtt.publish(client, prefixTopic + monthlyValueMcubeTopic, m['mcube'], params['mqtt']['qos'], params['mqtt']['retain'])

            ## Publish status values
            mqtt.publish(client, prefixTopic + statusDateTopic, dtn, params['mqtt']['qos'], params['mqtt']['retain'])
            mqtt.publish(client, prefixTopic + statusValueTopic, "Success", params['mqtt']['qos'], params['mqtt']['retain'])
    
    except:
        logging.error("Unable to publish value to mqtt broker")
        sys.exit(1)
    
    # Disconnect mqtt broker
    mqtt.disconnect(client)
    logging.info("Mqtt broker disconnected")
    
    
                
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v",  "--verbose", action="store_true",
                        help="More verbose", default=False)
    parser.add_argument(
        "-s", "--schedule",   help="Schedule the launch of the script at hh:mm everyday")
    
    args = parser.parse_args()

    pp = pprint.PrettyPrinter(indent=4)
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    if args.schedule:
        logging.info(args.schedule)
        schedule.every().day.at(args.schedule).do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        main()
