import sqlite3
import os
import sys

# Constants
DATABASE_NAME = "gazpar2mqtt.db"
DATABASE_TIMEOUT = 10

# Class database
class Database:
  
  # Constructor
  def __init__(self):
  
    self.con = None
    self.cur = None
    self.isConnected = False
  
  # Connexion to database
  def connexion(self):
    
    # Create directory if not exists
    if not os.path.exists('/data'):
        os.mkdir('/data')
        logging.debug("Directory /data created")
    
    # Initialize database if not exists
    if not os.path.exists('/data/enedisgateway.db'):
        logging.info("Initialization of the SQLite database...")
        self.con = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = con.cursor()
        init_database(cur)
    else:
        self.con = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = con.cursor()
    
  
