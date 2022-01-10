import sqlite3
import os
import logging
import datetime
import json

# Constants
DATABASE_NAME = "gazpar2mqtt.db"
DATABASE_TIMEOUT = 10

# Class database
class Database:
  
  # Constructor
  def __init__(self,g2mVersion,path):
  
    self.con = None
    self.cur = None
    self.version = g2mVersion
    self.path = path
  
  # Database initialization
  def init(self):
    
    # Create table config
    logging.debug("Creation of configuration table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS config (
                        key TEXT PRIMARY KEY,
                        value json NOT NULL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_config_key
                    ON config (key)''')

    ## Create table of PCEs
    logging.debug("Creation of PCEs table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS pces (
                        pce TEXT PRIMARY KEY
                        , json json NOT NULL
                        , count INTEGER)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_pces_pce
                    ON pces (pce)''')

    # Create table for measures
    logging.debug("Creation of measures table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS measures (
                        pce TEXT NOT NULL
                        , type TEXT NOT NULL
                        , date TEXT NOT NULL
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


    # Set default configuration
    logging.debug("Store default configuration")
    config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
    config = {
        "day": datetime.datetime.now().strftime('%Y-%m-%d'),
        "version": self.version
    }
    logging.debug("Database new config : %s", json.dumps(config))
    self.cur.execute(config_query, ["config", json.dumps(config)])
    self.commit()
  
  
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

  # Get current G2M version
  def getG2MVersion(self):
    query = f"SELECT value FROM config"
    self.cur.execute(query)
    queryResult = self.cur.fetchone()
    if queryResult is not None:
      resultValue = json.loads(queryResult[0])
      return resultValue["version"]
    else:
      return None
    
  # Get measures statistics
  def getMeasuresCount(self,type):
    valueResult = {}
    query = f"SELECT count(date), min(date), max(date) FROM measures WHERE type = '{type}'"
    self.cur.execute(query)
    queryResult = self.cur.fetchone()
    if queryResult is not None:
            if queryResult[0] is not None:
                valueResult["count"] = int(queryResult[0])
                valueResult["minDate"] = queryResult[1]
                valueResult["maxDate"] = queryResult[2]
                return valueResult
  

    
  # Re-initialize the database
  def reInit(self):
    
    logging.debug("Reinitialization of the database.")
    
    logging.debug("Drop configuration table")
    self.cur.execute('''DROP TABLE IF EXISTS config''')
    
    logging.debug("Drop PCEs table")
    self.cur.execute('''DROP TABLE IF EXISTS pces''')
    
    logging.debug("Drop daily consumptions table")
    self.cur.execute('''DROP TABLE IF EXISTS measures''')
    
    logging.debug("Drop thresold table")
    self.cur.execute('''DROP TABLE IF EXISTS thresold''')
    
    logging.debug("Drop thresolds table")
    self.cur.execute('''DROP TABLE IF EXISTS thresolds''')
    
    # Commit work
    self.commit()
    
    # Initialize tables
    self.init()
      
        
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
    
    
  
