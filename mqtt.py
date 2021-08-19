import paho.mqtt.client as mqtt
import time
import logging

# Broker settings
broker_client = "gazou"

# Initialize variables
mqtt_connected = False

# Callback on_connect
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    print("on_connect: " + mqtt.connack_string(rc))
    mqtt_connected = True

# Callback on_disconnect
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection: {}".format(rc) )

# Callback on_message
#def on_message(client, userdata, msg):
    #print("onMessageArrived: " + msg.topic + " " + str(msg.payload))

# Callback on_subscribe
#def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: mid=" + str(mid) + " QoS=" + str(granted_qos))

# Callback on_publish
#def on_publish(client, userdata, mid):
    print("Published: mid=" + str(mid) )


# Sub create client
def create_client(clientId):
    
    # Create instance
    #print("Instance mqtt client")
    client = mqtt.Client(clientId)
    
    return client


# Sub connect
def connect(client,host,port):
    
    # Activate callbacks
    print("Activate callback")
    client.on_connect = on_connect
    #client.on_message = on_message
    #client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
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
def publish(client,topic,payload,qos,retain):
    
    print("Publish payload")
    client.publish(topic, payload=payload, qos=qos, retain=retain)
    #client.publish(topic, payload=payload, qos=qos, retain=False)
    time.sleep(1)
