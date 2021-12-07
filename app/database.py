import sqlite3
import os
import sys
import logging
import datetime
import json

# Constants
DATABASE_NAME = "gazpar2mqtt.db"
DATABASE_PATH = '/data'
DATABASE_TIMEOUT = 10

# Class database
class Database:
  
  # Constructor
  def __init__(self,g2mVersion):
  
    self.con = None
    self.cur = None
    self.version = g2mVersion
  
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
                        pce TEXT PRIMARY KEY,
                        json json NOT NULL, 
                        count INTEGER)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_pces_pce
                    ON pces (pce)''')

    # Create table for daily consumptions
    logging.debug("Creation of daily consumptions table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS consumption_daily (
                        pce TEXT NOT NULL, 
                        date TEXT NOT NULL, 
                        value INTEGER NOT NULL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_date_consumption
                    ON consumption_daily (date)''')
    
    # Create table for billing
    logging.debug("Creation of billing table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS billing (
                        pce TEXT NOT NULL, 
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        end_index  INTEGER NOT NULL,
                        conversion REAL NOT NULL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_start_date_billing
                    ON billing (start_date)''')

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
    if not os.path.exists(DATABASE_PATH):
        os.mkdir(DATABASE_PATH)
        logging.debug("Directory %s created",DATABASE_PATH)
    
    # Initialize database if not exists
    if not os.path.exists(DATABASE_PATH + "/" + DATABASE_NAME):
        logging.debug("Initialization of the SQLite database...")
        self.con = sqlite3.connect(DATABASE_PATH + "/" + DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()
        self.init()
    else:
        logging.debug("Connexion to database")
        self.con = sqlite3.connect(DATABASE_PATH + "/" + DATABASE_NAME, timeout=DATABASE_TIMEOUT)
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
    
    
  
