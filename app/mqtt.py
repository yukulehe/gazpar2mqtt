#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import logging
import ssl

class Mqtt:

    def __init__(self,clientId,username,password,isSsl,qos,retain):
        
        self.isConnected = False
        self.isSsl = isSsl
        self.qos = qos
        self.retain = retain
        
        # Create instance
        self.client = mqtt.Client(clientId)
        
        # Set authentification
        if username != "" and password != "":
            self.client.username_pw_set(username, password)
            
        # Set SSL if required
        if self.isSsl:
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)
    

    # Callback on_connect
    def onConnect(self,client, userdata, flags, rc):
        logging.debug("Mqtt on_connect callback : %s",mqtt.connack_string(rc))
        if rc != 0:
            logging.error("Mqtt on_connect callback : connexion failed")
            self.isConnected = False
        else: 
            logging.debug("Mqtt on_connect callback : connected")
            self.isConnected = True
    

    # Callback on_disconnect
    def onDisconnect(self,client, userdata, rc):
        logging.debug("Mqtt on_disconnect callback : %s",mqtt.connack_string(rc))
        if rc != 0:
            logging.error("Mqtt on_disconnect callback : broker has been disconnected unexpectly")
            self.isConnected = False
        else: logging.debug("Mqtt on_disconnect callback : disconnected")
            

    # Callback on_publish
    def onPublish(self,client, userdata, mid):
        logging.debug("Mqtt on_publish callback : message published")
            
    # Connect
    def connect(self,host,port):

        # Activate callbacks
        logging.debug("Mqtt connect : activation of callbacks")
        self.host = host
        self.port = port
        self.client.on_connect = self.onConnect
        self.client.on_publish = self.onPublish
        self.client.on_disconnect = self.onDisconnect

        # Connect
        logging.debug("Mqtt connect : connection to broker %s:%s...",self.host,self.port)
        self.client.connect(self.host,self.port, 60)
        logging.debug("Wait for conexion callback")
        if self.isSsl:
            time.sleep(5)
        else:
            time.sleep(2)

        # Start loop
        self.client.loop_start()

    
    # Disconnect
    def disconnect(self):

        # End loop
        self.client.loop_stop()

        # Disconnect
        logging.debug("Mqtt disconnect : disconnection...")
        self.client.disconnect
  

    # Publish
    def publish(self,topic,payload):

        logging.debug("Mqtt publish : publication...")
        myPayload = str(payload)
        logging.debug("Publishing payload %s to topic %s, qos %s, retain %s",payload,topic, self.qos, self.retain)
        self.client.publish(topic, payload=myPayload, qos=self.qos, retain=self.retain)
        if self.isSsl:
            time.sleep(1)
        else:
            time.sleep(200/1000) # 200ms
