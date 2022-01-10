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

# Convert datetime string to datetime
def _convertDateTime(dateString):
    if dateString == None: return None
    else:
        myDateTime = datetime.datetime.strptime(dateString,DATABASE_DATE_FORMAT)
        return myDateTime

# Class database
class Database:
  
  # Constructor
  def __init__(self,g2mVersion,dbVersion,influxVersion,path):
  
    self.con = None
    self.cur = None
    self.date = datetime.datetime.now().strftime('%Y-%m-%d')
    self.g2mVersion = g2mVersion
    self.dbVersion = dbVersion
    self.influxVersion = influxVersion
    self.path = path
    self.pceList = []
  
  # Database initialization
  def init(self):
    
    # Create table config
    logging.debug("Creation of configuration table")
    self.cur.execute('''CREATE TABLE IF NOT EXISTS config (
                        date TEXT PRIMARY KEY,
                        g2m_version TEXT NOT NULL,
                        db_version TEXT NOT NULL,
                        influx_version TEXT NOT NULL)''')
    self.cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_config_date
                    ON config (date)''')

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


    # Set default configuration
    logging.debug("Store configuration")

    config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?, ?, ?)"
    self.cur.execute(config_query, [self.date, self.g2mVersion, self.dbVersion, self.influxVersion])
    logging.debug("Database new config : date = %s, g2m version = %s, database version = %s, influxdb version = %s", self.date,self.g2mVersion, self.dbVersion, self.influxVersion)
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
  def getVersion(self,type):

    query = f"SELECT {type} FROM config"
    queryResult = None
    try:
      self.cur.execute(query)
      queryResult = self.cur.fetchone()
      if queryResult is not None:
        return queryResult[0]
      else:
        return None
    except Exception as e:
      logging.warning("Error retrieving g2m version in config: %s",e)
      return queryResult

  # Get current db version
  def getDbVersion(self):
    query = f"SELECT db_version FROM config"
    queryResult = None
    try:
      self.cur.execute(query)
      queryResult = self.cur.fetchone()
      if queryResult is not None:
        return queryResult[0]
      else:
        return None
    except Exception as e:
      logging.warning("Error retrieving db version in config: %s", e)
      return queryResult

    
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
    self.cur.execute('''DROP TABLE IF EXISTS thresold''') # issue #59 on v0.7.0
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

  # Load
  def load(self):

    # Load PCEs
    self._loadPce()

    # Load measures
    for myPce in self.pceList:
      self._loadMeasures(myPce)


  # Load PCEs
  def _loadPce(self):

    query = "SELECT * FROM pces"
    self.cur.execute(query)
    queryResult = self.cur.fetchall()

    # Create object PCE
    for result in queryResult:
      myPce = Pce(result)
      self.pceList.append(myPce)


  # Load measures
  def _loadMeasures(self,pce):

    query = f"SELECT * FROM measures WHERE pce = '{pce.pceId}'"
    self.cur.execute(query)
    queryResult = self.cur.fetchall()

    # Create object measure
    for result in queryResult:
      myMeasure = Measure(pce,result)
      pce.measureList.append(myMeasure)


# Class PCE
class Pce():

  def __init__(self,result):

    self.pceId = result[0]
    self.pceJson = result[1]
    info = json.loads(result[1])
    self.alias = info["alias"]
    self.measureList = []

# Class Measure
class Measure():

  def __init__(self,pce,result):

    self.pce = pce
    self.type = result[1]
    self.date = _convertDateTime(result[2])
    self.startIndex = result[3]
    self.endIndex = result[4]
    self.volume = result[5]
    self.energy = result[6]
    self.conversionFactor = result[7]


    
    
  
