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
  def connect(self):
    
    # Create directory if not exists
    if not os.path.exists('/data'):
        os.mkdir('/data')
        logging.debug("Directory /data created")
    
    # Initialize database if not exists
    if not os.path.exists('/data/enedisgateway.db'):
        logging.debug("Initialization of the SQLite database...")
        self.con = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()
        init_database(self.cur)
    else:
        logging.debug("Connexion to database")
        self.con = sqlite3.connect(DATABASE_NAME, timeout=DATABASE_TIMEOUT)
        self.cur = self.con.cursor()
        
  
  def isConnected(self):
    if self.cur is not None:
      return True
    else:
      return False
    
  def close(self):
    logging.debug("Disconnexion of the database")
    self.con.close()
    
    
  
