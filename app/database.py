import sqlite3
import os
import sys
import logging

# Constants
DATABASE_NAME = "gazpar2mqtt.db"
DATABASE_TIMEOUT = 10

# Class database
class Database:
  
  # Constructor
  def __init__(self,g2mVersion):
  
    self.con = None
    self.cur = None
  
  # Database initialization
  def init(self):
    
    # Create table config
    logging.debug("Creation of configuration table")
    cur.execute('''CREATE TABLE config (
                        key TEXT PRIMARY KEY,
                        value json NOT NULL)''')
    cur.execute('''CREATE UNIQUE INDEX idx_config_key
                    ON config (key)''')

    ## Create table of PCEs
    logging.debug("Creation of PCEs table")
    cur.execute('''CREATE TABLE pces (
                        pce TEXT PRIMARY KEY,
                        json json NOT NULL, 
                        count INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_pces_pce
                    ON pces (pce)''')

    # Create table for daily consumptions
    logging.debug("Creation of daily consumptions table")
    cur.execute('''CREATE TABLE consumption_daily (
                        pce TEXT NOT NULL, 
                        date TEXT NOT NULL, 
                        value INTEGER NOT NULL)''')
    cur.execute('''CREATE UNIQUE INDEX idx_date_consumption
                    ON consumption_daily (date)''')
    
    # Create table for billing
    logging.debug("Creation of billing table")
    cur.execute('''CREATE TABLE billing (
                        pce TEXT NOT NULL, 
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        end_index  INTEGER NOT NULL,
                        conversion REAL NOT NULL)''')
    cur.execute('''CREATE UNIQUE INDEX idx_start_date_billing
                    ON billing (start_date)''')

    # Set default configuration
    logging.debug("Store default configuration")
    config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
    config = {
        "day": datetime.datetime.now().strftime('%Y-%m-%d'),
        "version": g2mVersion
    }
    logging.info(json.dumps(config))
    self.cur.execute(config_query, ["config", json.dumps(config)])
    self.commit()
  
  
  # Connexion to database
  def connect(self):
    
    # Create directory if not exists
    if not os.path.exists('/data'):
        os.mkdir('/data')
        logging.debug("Directory /data created")
    
    # Initialize database if not exists
    if not os.path.exists(DATABASE_NAME):
        logging.debug("Initialization of the SQLite database...")
        self.con = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()
        self.init()
    else:
        logging.debug("Connexion to database")
        self.con = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()
        
        
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
    
    
  
