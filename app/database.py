#!/usr/bin/env python3

import sys
import logging
import datetime
import sqlite3


class database:
  
    def __init__(self):
        self.isConnected = False
        self.con = None
        self.cur = None
    
  
    def connect(self,database):
        logging.debug("Connexion to sqlite database...")
        self.con = sqlite3.connect(database)
        wait(3)
        logging.debug("Get database cursor...")
        self.cur = self.con.cursor()
        
