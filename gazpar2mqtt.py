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
import mqttpub
import json

import argparse
import logging
import pprint
from envparse import env


PFILE = "/.params"
DOCKER_MANDATORY_VARENV=['GRDF_USERNAME','GRDF_PASSWORD','MQTT_HOST']
DOCKER_OPTIONAL_VARENV=['MQTT_PORT','MQTT_CLIENTID','MQTT_QOS', 'MQTT_TOPIC', 'MQTT_RETAIN']


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
                           'qos': env(DOCKER_OPTIONAL_VARENV[2],default=1),
                           'topic': env(DOCKER_OPTIONAL_VARENV[3], default='gazpar'),
                           'retain': env(DOCKER_OPTIONAL_VARENV[4], default=False)}}
    
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
                
    # Create mqtt client
    client = mqttpub.create_client(params['mqtt']['clientId'])
    logging.info("Mqtt client instantiated")
    
    # Connect to mqtt brocker
    mqttpub.connect(client,params['mqtt']['host'],params['mqtt']['port'])
    logging.info("Mqtt broker connected")
    
    # Publsh payload
    payload = "Hello world"
    mqttpub.publish(client,payload,params['mqtt']['topic'],params['mqtt']['qos'],params['mqtt']['retain'])
    
    
                
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
