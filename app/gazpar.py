#!/usr/bin/env python3

import sys
import logging
import requests
import json
import datetime

global JAVAVXS

# Constants
GRDF_DATE_FORMAT = "%Y-%m-%d"
GRDF_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Tools

# Convert string to date
def _convertDate(dateString):
    if dateString == None: return None
    else:
        myDate = datetime.datetime.strptime(dateString,GRDF_DATE_FORMAT).date()
        return myDate
    
# Convert string to datetime
def _convertDateTime(dateTimeString):
    
    if dateTimeString == None: return None
    else:
        myDateTimeString = dateTimeString[0:19].replace('T',' ') # we remove timezone
        myDateTime = datetime.datetime.strptime(myDateTimeString,GRDF_DATETIME_FORMAT)
        return myDateTime

# Class GRDF
class Grdf:
    
    def __init__(self):
        
        self.session = None
        self.auth_nonce = None
        self.pceList = []
        self.whoiam = None
        
        
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Mobile Safari/537.36',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept':'application/json, */*',
            'Connection': 'keep-alive'
        }
    
    # Login
    def login(self,username,password):
        
        # Get cookie
        req = self.session.get('https://monespace.grdf.fr/client/particulier/accueil')
        
        if not 'auth_nonce' in self.session.cookies:
            raise GazparLoginException("Cannot get auth_nonce.")
        else:
            logging.info("Cookies ok")
            
        self.auth_nonce = self.session.cookies.get('auth_nonce')
        logging.info("auth_nonce: " + self.auth_nonce)

        payload = {
            'email': username,
            'password': password,
            'capp': 'meg',
            'goto': 'https://sofa-connexion.grdf.fr:443/openam/oauth2/externeGrdf/authorize?response_type=code&scope=openid%20profile%20email%20infotravaux%20%2Fv1%2Faccreditation%20%2Fv1%2Faccreditations%20%2Fdigiconso%2Fv1%20%2Fdigiconso%2Fv1%2Fconsommations%20new_meg%20%2FDemande.read%20%2FDemande.write&client_id=prod_espaceclient&state=0&redirect_uri=https%3A%2F%2Fmonespace.grdf.fr%2F_codexch&nonce=' + self.auth_nonce + '&by_pass_okta=1&capp=meg'
        }
        
        # Login step 1
        req = self.session.post('https://login.monespace.grdf.fr/sofit-account-api/api/v1/auth', data=payload, allow_redirects=False)
        if not 'XSRF-TOKEN' in self.session.cookies:
            raise GazparLoginException("Login unsuccessful. Check your credentials.")
        else:
            logging.info("Login sucessfull.")
            
        
        # Login step 2
        req = self.session.get('https://sofa-connexion.grdf.fr:443/openam/oauth2/externeGrdf/authorize?response_type=code&scope=openid%20profile%20email%20infotravaux%20%2Fv1%2Faccreditation%20%2Fv1%2Faccreditations%20%2Fdigiconso%2Fv1%20%2Fdigiconso%2Fv1%2Fconsommations%20new_meg%20%2FDemande.read%20%2FDemande.write&client_id=prod_espaceclient&state=0&redirect_uri=https%3A%2F%2Fmonespace.grdf.fr%2F_codexch&nonce=' + self.auth_nonce + '&by_pass_okta=1&capp=meg')
    
        return req
        
    
    # Get account info
    def getWhoami(self):
        
        req = self.session.get('https://monespace.grdf.fr/api/e-connexion/users/whoami')
        account = json.loads(req.text)
        self.account = Account(account)
        
               
    # Get list of PCE
    def getPceList(self):
        
        req = self.session.get('https://monespace.grdf.fr/api/e-conso/pce')
        pceList = json.loads(req.text)
        
        for item in pceList:
            # Create PCE
            myPce = Pce(item)
            # Add PCE to list
            self.addPce(myPce)
    
    # Add PCE to list
    def addPce(self, pce):
        self.pceList.append(pce)
        
    # Count PCEs in list
    def countPce(self):
        return len(self.pceList)
    
    # Get measures of a single PCE for a period range
    def getPceDailyMeasures(self,pce, startDate='2018-11-27', endDate='2021-11-27'):
        
        req = self.session.get('https://monespace.grdf.fr/api/e-conso/pce/consommation/informatives?dateDebut=' + startDate + '&dateFin=' + endDate + '&pceList%5B%5D=' + pce.pceId)
        measureList = json.loads(req.text)
        
        for measure in measureList[pce.pceId]["releves"]:
            
            # Create the measure
            myDailyMeasure = DailyMeasure(measure)
            
            # Append measure to the PCE's measure list
            pce.dailyMeasureStart = startDate
            pce.dailyMeasureEnd = endDate
            pce.addDailyMeasure(myDailyMeasure)
            
            

# Account class
class Account:
    
    def __init__(self, account):
        
        self.type = account["type"]
        self.firstName = account["first_name"]
        self.lastName = account["last_name"]
        self.lastName = account["email"]

        
# PCE class      
class Pce:
    
    def __init__(self, pce):
        
        self.alias = pce["alias"]
        self.pceId = pce["pce"]
        self.activationDate = pce["dateActivation"]
        self.freqenceReleve = pce["frequenceReleve"]
        self.state = pce["etat"]
        self.ownerName = pce["nomTitulaire"]
        self.postalCode = pce["codePostal"]
        
        self.dailyMeasureList = []
        self.dailyMeasureStart = None
        self.dailyMeasureEnd = None
        
        
        
    def addDailyMeasure(self, measure):
        self.dailyMeasureList.append(measure)
        
    def countDailyMeasure(self):
        return len(self.dailyMeasureList)
    
    def countDailyMeasureOk(self):
        i = 0
        for myMeasure in self.dailyMeasureList:
            if myMeasure.isOk() == True:
                i += 1
        return i
    
    # Return the last valid measure
    def getLastMeasureOk(self):
        
        i = self.countDailyMeasure() - 1
        measure = None
        
        while i>=0:
            if self.dailyMeasureList[i].isOk() == True:
                measure = self.dailyMeasureList[i]
                break;
            i -= 1
        
        return measure
    
    # Return a measure by date
    def getDailyMeasureByDate(self,date):
        
        result = None
        for measure in self.dailyMeasureList:
            if measure.gasDate == date:
                result = measure
                break
        return result
    
    # Return volume difference for a range of date
    def getDailyMeasureVolumeDiff(self,startDate,endDate):
        
        # Get the first measure:
        firstMeasure = self.getDailyMeasureByDate(startDate)
        
        # Get the last measure:
        lastMeasure = self.getDailyMeasureByDate(endDate)
        
        if firstMeasure == None or lastMeasure == None:
            return None
        elif firstMeasure.isOk() == False or lastMeasure.isOk() == False:
            return None
        else:
            # Calculate the volume difference
            result = lastMeasure.volume - firstMeasure.volume
            return result
            
        
        
        
        
        
# Daily Measure class          
class DailyMeasure:
    
    def __init__(self, measure):
        
        self.startDateTime = _convertDateTime(measure["dateDebutReleve"])
        self.endDateTime = _convertDateTime(measure["dateFinReleve"])
        self.gasDate = _convertDate(measure["journeeGaziere"])
        self.startIndex = measure["indexDebut"]
        self.endIndex = measure["indexFin"]
        self.volume = measure["volumeBrutConsomme"]
        self.energy = measure["energieConsomme"]
        self.temperature = measure["temperature"]
        
        
    # Check measure quality
    def isOk(self):
        
        if self.volume == None: return False
        elif self.energy == None: return False
        elif self.startIndex == None: return False
        elif self.endIndex == None: return False
        else: return True
        
        
