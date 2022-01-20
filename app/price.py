#!/usr/bin/env python3

import sqlite3
import os
import logging
import datetime
from gazpar import Pce
#import pandas
import csv

PRICE_DATE_FORMAT = "%Y-%m-%d"

FILE_NAME = "prices.csv"

# Convert GRDF datetime string to date
def _convertDate(dateString):
    if dateString == None: return None
    else:
        myDate = datetime.datetime.strptime(dateString,PRICE_DATE_FORMAT).date()
        return myDate

class Prices():

    def __init__(self,path,defaultKwhPrice,defaultFixPrice):

        self.path = path
        self.filePath = self.path + "/" + FILE_NAME
        self.defaultKwhPrice = defaultKwhPrice
        self.defaultFixPrice = defaultFixPrice
        self.pricesList = []

        logging.debug("Retrieve list of prices...")

        # Check directory
        if not os.path.exists(self.filePath):
            logging.warning("Unable to find price file %s in directory %s",FILE_NAME,self.path)
            return # exit sub

        # Read csv
        try:
            with open(self.filePath,newline='') as f:
                myCsv = csv.reader(f,delimiter=';')
                next(myCsv)
                for myRow in myCsv:
                    logging.debug("%s", myRow)
                    # Create price
                    myPrice = Price(myRow)
                    self.pricesList.append(myPrice)

        except Exception as e:
            logging.error("Exception when reading unit price file : ",e)
            return


    # Return prices of a single Pce
    def getPricesByPce(self,pceId):

        myPriceList = []
        for myPrice in self.pricesList:
            if myPrice.pceId == pceId:
                myPriceList.append(myPrice)
        return myPriceList


# Class Price
class Price():

    def __init__(self,data):

        self.pceId = str(data[0])
        self.startDate = _convertDate(data[1])
        self.endDate = _convertDate(data[2])
        self.kwhPrice = float(data[3])
        self.fixPrice = float(data[4])

        logging.debug("Add price : pce = %s, startDate = %s, endDate = %s, price = %s", self.pceId, self.startDate,
                      self.endDate, self.kwhPrice, self.fixPrice)
