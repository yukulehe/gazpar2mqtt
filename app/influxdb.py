#!/usr/bin/env python3

import logging
import time
import json
from database import Pce, Measure
from datetime import datetime, timedelta
from influxdb_client import Point,InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import price

# Constants
WRITE_MAX_ERROR = 20 # maximum number of write errors accepted before abort
WRITE_SLEEP = 0.005 # time to sleep between two write

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
    def setMeasurePoint(self,measure,prices):

        myDate = measure.date

        # Retrieve the corresponding prices, if not found use the default price
        myKwhPrice = prices.defaultKwhPrice
        myFixPrice = prices.defaultFixPrice

        for myPrice in prices.getPricesByPce(measure.pce.pceId):
            if myDate.date() >= myPrice.startDate and myDate.date() <= myPrice.endDate:
                myKwhPrice = myPrice.kwhPrice
                myFixPrice = myPrice.fixPrice

        # Calculate the cost in Eur
        myCost = ( myKwhPrice * measure.energy ) + myFixPrice

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
                "gas_mcube": float(measure.volume),
                "energy_kWh" : float(measure.energy),
                "conversion_factor": float(measure.conversionFactor),
                "cost_eur" : float(myCost)
            },
            "time": myDate
        }]

        logging.debug("Point : %s",point)
        return point

    # Set PCE point
    def setPcePoint(self,pce):

        myDate = datetime.today()

        point = [{
            "measurement": "gazpar_pce_measure",  # container of tags
            "tags": {
                "pce": pce.pceId,
                "type": "pce",
                "pce_alias": pce.alias,
                "year": myDate.strftime("%Y"),
                "month": myDate.strftime("%m"),
                "month_name": myDate.strftime("%b"),
                "owner_name": pce.ownerName,
                "postal_code": pce.postalCode,
                "activation_date": pce.activationDate,
                "frequence_releve": pce.frequenceReleve,
                "state": pce.state,
            },
            "fields": {
                "pce_count": 1,
            },
            "time": myDate
        }]

        logging.debug("Point : %s", point)
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
                "energy_kWh": float(thresold.energy),
            },
            "time": myDate
        }]

        logging.debug("Point : %s", point)
        return point

    # Set price point
    def setPricePoint(self, pce, price,isDefault,defaultKwh,defaultFix):

        myDate = datetime.today()

        if isDefault:
            myKwh = defaultKwh
            myFix = defaultFix
        else:
            myKwh = price.kwhPrice
            myFix = price.fixPrice

        point = [{
            "measurement": "gazpar_price_measure",  # container of tags
            "tags": {
                "pce": pce.pceId,
                "pce_alias": pce.alias,
                "type": "price",
                "year": myDate.strftime("%Y"),
                "month": int(myDate.strftime("%m")),
                "month_name": myDate.strftime("%b"),
                "weekday_name": myDate.strftime("%A"),
                "weekday_no": myDate.weekday()
            },
            "fields": {
                "price_kwh_eur": float(myKwh),
                "price_fix_eur": float(myFix)
            },
            "time": myDate
        }]

        logging.debug("Point : %s", point)
        return point

    # Write
    def write(self,point):

        try:
            self.writeApi.write(bucket=self.bucket, org=self.org, record=point)
            time.sleep(WRITE_SLEEP)
            logging.debug("Point written successfully: %s",point)
            return True

        except Exception as e:
            logging.error("Unable to write point : %s", e)
            logging.debug("Point : %s", point)
            return False

    # Close client
    def close(self):

        try:
            self.client.close()
            logging.debug("Influxdb disconnected.")
        except Exception as e:
            logging.error("Unable to close influx connexion.")
