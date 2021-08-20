import paho.mqtt.client as mqtt
import time
import logging

# Callback on_connect
def on_connect(client, userdata, flags, rc):
    logging.debug("Mqtt on_connect : %s", mqtt.connack_string(rc))

# Callback on_disconnect
def on_disconnect(client, userdata, rc):
    if rc != 0:
        logging.debug("Mqtt on_disconnect : unexpected disconnection %s", mqtt.connack_string(rc))
        logging.error("MQTT broker has been disconnected unexpectly")
        sys.exit(0)

# Callback on_publish
def on_publish(client, userdata, mid):
    logging.debug("Mqtt on_publish : message published")

# Sub constructor
def create_client(clientId):
    
    # Create instance
    client = mqtt.Client(clientId)    
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
    client.publish(topic, payload=payload, qos=qos, retain=retain)
    time.sleep(1)
