#!/usr/bin/env python3

import sys
import logging
import requests
import json

def getConsoDataByPce(session,pce):
    
    req = session.get('https://monespace.grdf.fr/api/e-conso/pce/consommation/informatives?dateDebut=2018-11-27&dateFin=2021-11-27&pceList%5B%5D=' + pce)
    logging.info("CONSO:")
    logging.info(req.text)
    
    return req
    

def login(username, password):

    """Logs the user into the Linky API.
    """
    global JAVAVXS
    session = requests.Session()

    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Mobile Safari/537.36',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept':'application/json, */*',
        'Connection': 'keep-alive'
    }

    #Get essential cookies
    logging.info("Get essential cookies...")
    req = session.get('https://monespace.grdf.fr/client/particulier/accueil')
    if not 'auth_nonce' in session.cookies:
        raise GazparLoginException("Cannot get auth_nonce.")
    else:
        logging.info("Cookies ok")
    auth_nonce = session.cookies.get('auth_nonce')
    logging.info("auth_nonce: " + auth_nonce)

    payload = {
        'email': username,
        'password': password,
        'capp': 'meg',
        'goto': 'https://sofa-connexion.grdf.fr:443/openam/oauth2/externeGrdf/authorize?response_type=code&scope=openid%20profile%20email%20infotravaux%20%2Fv1%2Faccreditation%20%2Fv1%2Faccreditations%20%2Fdigiconso%2Fv1%20%2Fdigiconso%2Fv1%2Fconsommations%20new_meg%20%2FDemande.read%20%2FDemande.write&client_id=prod_espaceclient&state=0&redirect_uri=https%3A%2F%2Fmonespace.grdf.fr%2F_codexch&nonce=' + auth_nonce + '&by_pass_okta=1&capp=meg'
    }

    logging.info("Try to log...")
    req = session.post('https://login.monespace.grdf.fr/sofit-account-api/api/v1/auth', data=payload, allow_redirects=False)
    if not 'XSRF-TOKEN' in session.cookies:
        raise GazparLoginException("Login unsuccessful. Check your credentials.")
    else:
        logging.info("Login sucessfull.")
    
    logging.info("Try to get 1... ")
    req = session.get('https://sofa-connexion.grdf.fr:443/openam/oauth2/externeGrdf/authorize?response_type=code&scope=openid%20profile%20email%20infotravaux%20%2Fv1%2Faccreditation%20%2Fv1%2Faccreditations%20%2Fdigiconso%2Fv1%20%2Fdigiconso%2Fv1%2Fconsommations%20new_meg%20%2FDemande.read%20%2FDemande.write&client_id=prod_espaceclient&state=0&redirect_uri=https%3A%2F%2Fmonespace.grdf.fr%2F_codexch&nonce=' + auth_nonce + '&by_pass_okta=1&capp=meg')
    logging.info(req.text)
    
    logging.info("Try to get account informations ")
    req = session.get('https://monespace.grdf.fr/api/e-connexion/users/whoami')
    logging.info(req.text)
    
    
    logging.info("Try to get PCE list... ")
    req = session.get('https://monespace.grdf.fr/api/e-conso/pce')
    logging.info("PCEs:")
    logging.info(req.text)
    
    
    jsonPce = json.loads(req.text)
    for key in jsonPce:
        print(key)
        
    logging.info("Try to get conso data... ")
    #req = getConsoDataByPce(session,pce)
    
    
  

    return session
