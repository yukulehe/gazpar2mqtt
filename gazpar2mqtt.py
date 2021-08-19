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
currentValueDateTopic = "/current/date"
currentValueKwhTopic = "/current/kwh"
currentValueMcubeTopic = "/current/mcube"
statusDateTopic = "/status/date"
statusValueTopic = "/status/value"


# Sub to get StartDate depending today - daysNumber
def _getStartDate(today, daysNumber):
    return _dayToStr(today - relativedelta(days=daysNumber))

# Sub to return format wanted by linky.py
def _dayToStr(date):
    return date.strftime("%d/%m/%Y")
  
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
    
    
    # Get params from environment OS
    params = _openParams(PFILE)
                
    logging.info("GRDF config : username = %s, password = %s", params['grdf']['username'], params['grdf']['password'])
    logging.info("MQTT config : host = %s, port = %s, clientId = %s, qos = %s, topic = %s, retain = %s", \
                 params['mqtt']['host'], params['mqtt']['port'], params['mqtt']['clientId'], \
                 params['mqtt']['qos'],params['mqtt']['topic'],params['mqtt']['retain'])
    
    
    # Log to GRDF API
    try:
        logging.info("logging in GRDF URI %s...", gazpar.API_BASE_URI)
        token = gazpar.login(params['grdf']['username'], params['grdf']['password'])
        logging.info("logged in successfully!")
    except:
        logging.error("unable to login on %s", gazpar.API_BASE_URI)
        sys.exit(1)
    
    # Get data from GRDF API
    startDate = _getStartDate(datetime.date.today(), args.days)
    endDate = _dayToStr(datetime.date.today())
    
    #resGrdf = gazpar.get_data_per_day(token, startDate, endDate)
    try:
        logging.info("get Data from GRDF from {0} to {1}".format(startDate, endDate))
        # Get result from GRDF by day
        resGrdf = gazpar.get_data_per_day(token, startDate, endDate)

        if (args.verbose):
            pp.pprint(resGrdf)
                
    except:
        logging.error("unable to get data from GRDF")
        sys.exit(1)
        
    # Loop on results
    c = len(resGrdf)
    logging.info("Number of values : %s", c)
    for d in resGrdf:
        #t = datetime.datetime.strptime(d['date'] + " 12:00", '%d-%m-%Y %H:%M')
        logging.info("%s : Kwh = %s, Mcube = %s",d['date'],d['kwh'], d['mcube'])
    
    
    # Create mqtt client
    client = mqtt.create_client(params['mqtt']['clientId'])
    logging.info("Mqtt client instantiated")
    
    # Connect mqtt brocker
    mqtt.connect(client,params['mqtt']['host'],params['mqtt']['port'])
    logging.info("Mqtt broker connected")
   
    # We publish only the last input from grdf
    d = resGrdf[c-1]
    
    
    prefixTopic = params['mqtt']['topic']
    
    if d['date'] == "0":
        
        ## Publish status values
        mqtt.publish(client, prefixTopic + statusDateTopic, _dayToStr(datetime.date.today()), params['mqtt']['qos'], params['mqtt']['retain'])
        mqtt.publish(client, prefixTopic + statusValueTopic, "Error", params['mqtt']['qos'], params['mqtt']['retain'])
        
    else:
        # Publish current values
        mqtt.publish(client, prefixTopic + currentValueDateTopic, d['date'], params['mqtt']['qos'], params['mqtt']['retain'])
        mqtt.publish(client, prefixTopic + currentValueKwhTopic, d['kwh'], params['mqtt']['qos'], params['mqtt']['retain'])
        mqtt.publish(client, prefixTopic + currentValueMcubeTopic, d['mcube'], params['mqtt']['qos'], params['mqtt']['retain'])
       
    
    # Disconnect mqtt broker
    mqtt.disconnect(client)
    logging.info("Mqtt broker disconnected")
    
    
                
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-d",  "--days",    type=int,
                        help="Number of days from now to download", default=1)
    parser.add_argument("-l",  "--last",    action="store_true",
                        help="Check from InfluxDb the number of missing days", default=False)
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
