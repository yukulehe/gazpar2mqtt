import paho.mqtt.client as mqtt
import mqttutil
import time

# Broker settings
broker_client = "gazou"

# Initialize variables
mqtt_connected = False

# on_connect
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    print("on_connect: " + mqtt.connack_string(rc))
    mqtt_connected = True

# Sub create client
def create_client(clientId)
    
    # Create instance
    print("Instance mqtt client")
    client = mqtt.Client(clientId)
    
    return client

# Sub connect
def connect(client,host,port):
    
    # Activate callbacks
    print("Activate callback")
    client.on_connect = on_connect
    client.on_message = mqttutil.on_message
    client.on_publish = mqttutil.on_publish
    client.on_disconnect = mqttutil.on_disconnect
    
    # Connect
    print("Connexion to broker")
    client.connect(host,port, 60)
    time.sleep(2)
    
    # Start loop
    client.loop_start()
    
# Sub disconnect
def disconnect(client):
    
    # End loop
    client.loop_stop()
    
    # Disconnect
    print("Disconnexion")
    client.disconnect
  
# Sub publish
def publish(client,topic,payload,qos,retain)
    
    print("Publish payload")
    client.publish(topic, payload=payload, qos=qos, retain=retain)
    time.sleep(1)
