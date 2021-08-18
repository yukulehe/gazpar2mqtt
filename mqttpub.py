# Import
import paho.mqtt.client as mqtt

# Broker settings
broker_address="192.168.1.184" 

# Create mqtt instance
print("creating new instance")
client = mqtt.Client("P1") #create new instance

# Connexion to mqtt
print("connecting to broker")
client.connect(broker_address) #connect to broker
print("Subscribing to topic","house/bulbs/bulb1")

# Publish message
print("Publishing message to topic","house/bulbs/bulb1")
client.publish("house/bulbs/bulb1","OFF")
