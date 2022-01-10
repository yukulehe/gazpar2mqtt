#!/usr/bin/env python3

import logging
import time
import json
from database import Pce, Measure
from datetime import datetime, timedelta
from influxdb_client import Point,InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


# Class influx DB
class InfluxDb:

    # Constructor
    def __init__(self, version):

        logging.debug("Iniatilization of InfluxDB.")
        self.isConnected = False
        self.version = version
        self.token = None
        self.org = None
        self.client = None
        self.writeApi = None

    # Connexion
    def connect(self,host,port, org, bucket, token):

        self.host = host
        self.port = port
        self.org = org
        self.bucket = bucket
        self.token = token

        url = "http://" + host + ":" + str(port)

        try:
            self.client = InfluxDBClient(url=url, token=token, org=org)
            self.writeApi = self.client.write_api(write_options=SYNCHRONOUS)

        except Exception as e:
            print(e)

    # Set measure point
    def setMeasurePoint(self,measure):

        myDate = measure.date

        point = [{
            "measurement": "gazpar_informative_measure", # container of tags
            "tags": {
                "pce": measure.pce.pceId,
                "pce_alias": measure.pce.alias,
                "type": measure.type,
                "year": myDate.strftime("%Y"),
                "month": int(myDate.strftime("%m")),
                "month_name": myDate.strftime("%b"),
                "weekday_name": myDate.strftime("%A"),
                "weekday_no": myDate.weekday()
            },
            "fields": {
                "start_index": measure.startIndex,
                "end_index" : measure.endIndex,
                "gas_mcube": measure.volume,
                "energy_kWh" : measure.energy,
                "conversion_factor": measure.conversionFactor
            },
            "time": myDate
        }]

        logging.debug("Point : %s",point)
        return point

    # Set measure point
    def setThresoldPoint(self, thresold):


        myDate = thresold.date

        point = [{
            "measurement": "gazpar_thresold_measure",  # container of tags
            "tags": {
                "pce": thresold.pce.pceId,
                "type": "thresold",
                "pce_alias": thresold.pce.alias,
                "year": myDate.strftime("%Y"),
                "month": myDate.strftime("%m"),
                "month_name": myDate.strftime("%b"),
            },
            "fields": {
                "energy_kWh": thresold.energy,
            },
            "time": myDate
        }]

        logging.debug("Point : %s", point)
        return point

    # Write
    def write(self,point):

        try:
            self.writeApi.write(bucket=self.bucket, org=self.org, record=point)
            time.sleep(0.005)
            logging.debug("Point writed successfully: %s",point)
            return True

        except Exception as e:
            logging.error("Unable to write point : %s", e)
            logging.debug("Point : %s", point)
            return False
