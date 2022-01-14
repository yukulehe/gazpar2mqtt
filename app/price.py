#!/usr/bin/env python3

import sqlite3
import os
import logging
import datetime
from gazpar import Pce
import pandas

FILE_NAME = "prices.csv"

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
            myDf = pandas.read_csv(self.filePath,sep=";",header=0,parse_dates=[1,2])
        except Exception as e:
            logging.error("Exception when reading unit price file : ",e)
            return

        logging.debug("Unit prices (10 first rows) :")
        logging.debug("%s",myDf.head(10))

        for myData in myDf.iterrows():
            # Create price
            myPrice = Price(myData[1])
            self.pricesList.append(myPrice)

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
        self.startDate = data[1]
        self.endDate = data[2]
        self.kwhPrice = data[3]
        self.fixPrice = data[4]

        logging.debug("Add price : pce = %s, startDate = %s, endDate = %s, price = %s", self.pceId, self.startDate,
                      self.endDate, self.kwhPrice, self.fixPrice)
