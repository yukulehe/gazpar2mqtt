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

#######################################################################
#### Usefull functions
#######################################################################

# Convert GRDF datetime string to date
def _convertDate(dateString):
    if dateString == None: return None
    else:
        myDate = datetime.datetime.strptime(dateString,GRDF_DATE_FORMAT).date()
        return myDate
    
# Convert GRDF datetime string to datetime
def _convertDateTime(dateTimeString):
    
    if dateTimeString == None: return None
    else:
        myDateTimeString = dateTimeString[0:19].replace('T',' ') # we remove timezone
        myDateTime = datetime.datetime.strptime(myDateTimeString,GRDF_DATETIME_FORMAT)
        return myDateTime
    
# Convert date to GRDF date string
def _convertGrdfDate(date):
    return date.strftime(GRDF_DATE_FORMAT)


#######################################################################
#### Class GRDF
#######################################################################
class Grdf:
    
    # Constructor
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
            logging.debug("Cookies ok")
            
        self.auth_nonce = self.session.cookies.get('auth_nonce')
        logging.debug("auth_nonce: " + self.auth_nonce)

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
    
    # Return GRDF quality status
    def isOk():
        
        # GRDF is ok when contains at least one valid PCE
        if self.countPce() == 0 or self.countPce() is None:
            return False
        elif self.countPceOk() == 0 or self.countPceOk() Is None:
            return False
        else:
            return True
        
    
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
        
    # Return the number of PCE
    def countPce(self):
        return len(self.pceList)
    
    # Return the number of valid PCE
    def countPceOk(self):
        i = 0
        for myPce in self.pceList:
            if myPce.isOk() == True:
                i += 1
        return i
    
    # Get measures of a single PCE for a period range
    def getPceDailyMeasures(self,pce, startDate, endDate):
        
        # Convert date
        myStartDate = _convertGrdfDate(startDate)
        myEndDate = _convertGrdfDate(endDate)
        
        req = self.session.get('https://monespace.grdf.fr/api/e-conso/pce/consommation/informatives?dateDebut=' + myStartDate + '&dateFin=' + myEndDate + '&pceList%5B%5D=' + pce.pceId)
        measureList = json.loads(req.text)
        
        for measure in measureList[pce.pceId]["releves"]:
            
            # Create the measure
            myDailyMeasure = DailyMeasure(measure)
            
            # Append measure to the PCE's measure list
            pce.dailyMeasureStart = startDate
            pce.dailyMeasureEnd = endDate
            pce.addDailyMeasure(myDailyMeasure)
            
            

#######################################################################
#### Class Account
#######################################################################
class Account:
    
    # Constructor
    def __init__(self, account):
        
        self.type = account["type"]
        self.firstName = account["first_name"]
        self.lastName = account["last_name"]
        self.lastName = account["email"]


#######################################################################
#### Class PCE
#######################################################################    
class Pce:
    
    # Constructor
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
        
        
    # Add a measure to the PCE    
    def addDailyMeasure(self, measure):
        self.dailyMeasureList.append(measure)
        
    # Return the number of measure for the PCE
    def countDailyMeasure(self):
        return len(self.dailyMeasureList)
    
    # Return the number of valid measure for the PCE
    def countDailyMeasureOk(self):
        i = 0
        for myMeasure in self.dailyMeasureList:
            if myMeasure.isOk() == True:
                i += 1
        return i
    
    # Return PCE quality status
    def isOk():
         # To be ok, the PCE must contains at least one valid measure
         if self.countDailyMeasure() == 0 or self.countDailyMeasure() is None:
            return False
         elif self.countDailyMeasureOk() == 0 or self.countDailyMeasureOk() is None:
            return False
         else:
            return True 
    
    # Return the last valid measure for the PCE
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
            
        
        
        
        
#######################################################################
#### Class Daily Measure
#######################################################################                
class DailyMeasure:
    
    # Constructor
    def __init__(self, measure):
        
        self.startDateTime = _convertDateTime(measure["dateDebutReleve"])
        self.endDateTime = _convertDateTime(measure["dateFinReleve"])
        self.gasDate = _convertDate(measure["journeeGaziere"])
        self.startIndex = measure["indexDebut"]
        self.endIndex = measure["indexFin"]
        self.volume = measure["volumeBrutConsomme"]
        self.energy = measure["energieConsomme"]
        self.temperature = measure["temperature"]
        
        
    # Return measure measure quality status
    def isOk(self):
        
        if self.volume == None: return False
        elif self.energy == None: return False
        elif self.startIndex == None: return False
        elif self.endIndex == None: return False
        else: return True
        
        
