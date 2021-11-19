import paho.mqtt.client as mqtt
import time
import logging
import sys
import ssl

MQTT_IS_CONNECTED = False

# Callback on_connect
def on_connect(client, userdata, flags, rc):
    global MQTT_IS_CONNECTED
    logging.debug("Mqtt on_connect : %s", mqtt.connack_string(rc))
    MQTT_IS_CONNECTED = True
    

# Callback on_disconnect
def on_disconnect(client, userdata, rc):
    global MQTT_IS_CONNECTED
    if rc != 0:
        logging.debug("Mqtt on_disconnect : unexpected disconnection %s", mqtt.connack_string(rc))
        logging.error("MQTT broker has been disconnected unexpectly")
        MQTT_IS_CONNECTED = False
        sys.exit(1)

# Callback on_publish
def on_publish(client, userdata, mid):
    logging.debug("Mqtt on_publish : message published")

# Sub constructor
def create_client(clientId,username,password,ssl):
    
    # Create instance
    client = mqtt.Client(clientId)
    
    # Set authentification
    if username != "" and password != "":
        client.username_pw_set(username, password)
    
    # Set SSL if required
    ssl_boolean = False
    ssl_boolean = ssl.lower() in ("t","true","1","Yes","Y","Yup","Oui","Si","Da")
    if ssl_boolean:
        client.tls_set(cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
    
    return client

# Sub connect
def connect(client,host,port):
    
    # Activate callbacks
    logging.debug("Mqtt connect : activation of callbacks")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    # Connect
    logging.debug("Mqtt connect : connection to broker...")
    client.connect(host,port, 60)
    time.sleep(2)
    
    # Start loop
    client.loop_start()

    
# Sub disconnect
def disconnect(client):
    
    # End loop
    client.loop_stop()
    
    # Disconnect
    logging.debug("Mqtt disconnect : disconnection...")
    client.disconnect
  
# Sub publish
def publish(client,topic,payload,qos,retain):
    
    logging.debug("Mqtt publish : publication...")
    
    retain_boolean = False
    retain_boolean = retain.lower() in ("t","true","1","Yes","Y","Yup","Oui","Si","Da")
    
    logging.debug("Publishing payload %s to topic %s, qos %s, retain %s",payload,topic, qos, retain_boolean)
    client.publish(topic, payload=payload, qos=qos, retain=retain_boolean)
    time.sleep(1)
