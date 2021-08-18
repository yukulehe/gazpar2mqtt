import paho.mqtt.client as mqtt
import mqttutil

# Create instance
print("Create mqtt instance")
client = mqtt.Client(mqttutil.broker_client)

# Connect
print("Connexion to broker")
client.connect(mqttutil.broker_address, mqttutil.broker_port, 60)

# Publish
client.publish("gazpar/status","ON")
