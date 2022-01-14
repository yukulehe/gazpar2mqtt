#!/usr/bin/env python3
import sqlite3
import os
import logging
import datetime
import json
from gazpar import TYPE_I,TYPE_P

# Constants
DATABASE_NAME = "gazpar2mqtt.db"
DATABASE_TIMEOUT = 10
DATABASE_DATE_FORMAT = "%Y-%m-%d"
DATABASE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Config constants
G2M_KEY = "g2m"
DB_KEY = "db"
INFLUX_KEY = "influx"
LAST_EXEC_KEY = "last_exec_datetime"

# Convert datetime string to datetime
def _convertDate(dateString):
    if dateString == None: return None
    else:
        myDateTime = datetime.datetime.strptime(dateString,DATABASE_DATE_FORMAT)
        return myDateTime

def _convertDateTime(dateString):
  if dateString == None:
    return None
  else:
    myDateTime = datetime.datetime.strptime(dateString, DATABASE_DATETIME_FORMAT)
    return myDateTime

# Class database
class Database:
  
  # Constructor
  def __init__(self,path):
  
    self.con = None
    self.cur = None
    self.date = datetime.datetime.now().strftime('%Y-%m-%d')
    self.g2mVersion = None
    self.dbVersion = None
    self.influxVersion = None
    self.path = path
    self.pceList = []
  
  # Database initialization
  def init(self,g2mVersion,dbVersion,influxVersion):

    # Create table for configuration
    logging.debug("Creation of config table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS config (
                                key TEXT NOT NULL 
                                , value TEXT NOT NULL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_config_key
                            ON config (key)''')

    ## Create table of PCEs
    logging.debug("Creation of PCEs table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS pces (
                        pce TEXT PRIMARY KEY
                        , alias TEXT
                        , activation_date TYPE TEXT
                        , frequence_releve TYPE TEXT
                        , state TYPE TEXT
                        , owner_name TYPE TEXT
                        , postal_code TYPE TEXT)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_pces_pce
                    ON pces (pce)''')

    # Create table for measures
    logging.debug("Creation of measures table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS measures (
                        pce TEXT NOT NULL
                        , type TEXT NOT NULL
                        , date TEXT NOT NULL
                        , start_index INTEGER NOT NULL
                        , end_index INTEGER NOT NULL
                        , volume INTEGER NOT NULL
                        , energy INTEGER NOT NULL
                        , conversion REAL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_measures_measure
                    ON measures (pce,type,date)''')

    
    # Create table for thresolds
    logging.debug("Creation of thresolds table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS thresolds (
                        pce TEXT NOT NULL 
                        , date TEXT NOT NULL
                        , energy INTEGER NOT NULL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_tresholds_thresold
                    ON thresolds (pce,date)''')

    # Commit
    self.commit()

    # Update configuration values
    logging.debug("Store configuration")
    self.updateVersion(G2M_KEY, g2mVersion)
    self.updateVersion(DB_KEY, dbVersion)
    self.updateVersion(INFLUX_KEY, influxVersion)
    self.updateVersion(LAST_EXEC_KEY, datetime.datetime.now())

    # Commit
    self.commit()

  # Check that table exists
  def existsTable(self,name):

    query = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?"
    queryResult = None
    try:
      self.cur.execute(query,[name])
      queryResult = self.cur.fetchall()
      if queryResult is not None and queryResult[0][0] == 1:
        return True
      else:
        return False
    except Exception as e:
      logging.error("Error when checking table : %s",e)
      return False


  # Update version
  def updateVersion(self,key,value):

    if self.existsTable("config"):
      query = "INSERT OR REPLACE INTO config(key,value) VALUES(?,?)"
      try:
        self.cur.execute(query, [key,value])
        logging.debug("Version of key %s with value %s updated successfully !", key, value)
      except Exception as e:
        logging.error("Error when updating config table : %s",e)


  # Get version
  def getConfig(self, key):

    query = "SELECT value FROM config WHERE key = ?"
    queryResult = None
    try:
      self.cur.execute(query,[key])
      queryResult = self.cur.fetchone()
      if queryResult is not None:
        return queryResult[0]
      else:
        return None
    except Exception as e:
      logging.warning("Error retrieving version of key %s in config table %s", key, e)
      return queryResult


  # Connexion to database
  def connect(self):
    
    # Create directory if not exists
    if not os.path.exists(self.path):
        os.mkdir(self.path)
        logging.debug("Directory %s created",self.path)
    
    # Initialize database if not exists
    if not os.path.exists(self.path + "/" + DATABASE_NAME):
        logging.debug("Initialization of the SQLite database...")
        self.con = sqlite3.connect(self.path + "/" + DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()
        self.init()
    else:
        logging.debug("Connexion to database")
        self.con = sqlite3.connect(self.path + "/" + DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()


  # Get measures statistics
  def getMeasuresCount(self,type):

    valueResult = {}
    query = f"SELECT count(*), count(distinct date), count(distinct pce), min(date), max(date) FROM measures WHERE type = '{type}'"
    self.cur.execute(query)
    queryResult = self.cur.fetchone()
    if queryResult is not None:
            if queryResult[0] is not None:
                valueResult["rows"] = int(queryResult[0])
                valueResult["dates"] = int(queryResult[1])
                valueResult["pce"] = int(queryResult[2])
                valueResult["minDate"] = queryResult[3]
                valueResult["maxDate"] = queryResult[4]
                return valueResult
  

  # Re-initialize the database
  def reInit(self,g2mVersion,dbVersion,influxVersion):
    
    logging.debug("Reinitialization of the database.")
    
    logging.debug("Drop configuration table")
    self.cur.execute('''DROP TABLE IF EXISTS config''')
    
    logging.debug("Drop PCEs table")
    self.cur.execute('''DROP TABLE IF EXISTS pces''')
    
    logging.debug("Drop daily consumptions table")
    self.cur.execute('''DROP TABLE IF EXISTS measures''')
    
    logging.debug("Drop thresolds table")
    self.cur.execute('''DROP TABLE IF EXISTS thresold''') # issue #59 on v0.7.0
    self.cur.execute('''DROP TABLE IF EXISTS thresolds''')
    
    # Commit work
    self.commit()
    
    # Initialize tables
    self.init(g2mVersion,dbVersion,influxVersion)
      
        
  # Check if connected
  def isConnected(self):
    return self.cur
    
    
  # Disconnect
  def close(self):
    logging.debug("Disconnexion of the database")
    self.con.close()
    
    
  # Commit work
  def commit(self):
    self.con.commit()

  # Load
  def load(self):

    # Load PCEs
    self._loadPce()

    # Load measures
    for myPce in self.pceList:
      self._loadMeasures(myPce)

    # Load thresolds
    for myPce in self.pceList:
      self._loadThresolds(myPce)

  # Load PCEs
  def _loadPce(self):

    query = "SELECT * FROM pces"
    self.cur.execute(query)
    queryResult = self.cur.fetchall()

    # Create object PCE
    for result in queryResult:
      myPce = Pce(result)
      self.pceList.append(myPce)

  # Load account info
  def _loadAccount(self):

    query = "SELECT * FROM account"
    self.cur.execute(query)
    queryResult = self.cur.fetchone()

  # Load measures
  def _loadMeasures(self,pce):

    query = f"SELECT * FROM measures WHERE pce = '{pce.pceId}'"
    self.cur.execute(query)
    queryResult = self.cur.fetchall()

    # Create object measure
    for result in queryResult:
      myMeasure = Measure(pce,result)
      pce.measureList.append(myMeasure)

  # Load thresolds
  def _loadThresolds(self, pce):

    query = f"SELECT * FROM thresolds WHERE pce = '{pce.pceId}'"
    self.cur.execute(query)
    queryResult = self.cur.fetchall()

    # Create object measure
    for result in queryResult:
      myThresold = Thresold(pce, result)
      pce.thresoldList.append(myThresold)


# Class PCE
class Pce():

  def __init__(self,result):

    self.pceId = result[0]
    self.alias = result[1]
    self.activationDate = _convertDateTime(result[2])
    self.frequenceReleve = result[3]
    self.state = result[4]
    self.ownerName = result[5]
    self.postalCode = result[6]
    self.measureList = []
    self.thresoldList = []

# Class Measure
class Measure():

  def __init__(self,pce,result):

    self.pce = pce
    self.type = result[1]
    self.date = _convertDate(result[2])
    self.startIndex = result[3]
    self.endIndex = result[4]
    self.volume = result[5]
    self.energy = result[6]
    self.conversionFactor = result[7]

# Class Measure
class Thresold():

  def __init__(self,pce,result):

    self.pce = pce
    self.date = _convertDate(result[1])
    self.energy = result[2]

    
  
