import paho.mqtt.client as mqtt
import mqttutil

# Create instance
print("Create mqtt instance")
client = mqtt.Client(mqttutil.broker_client)

# Connect
print("Connexion to broker: %s : %s", mqttutil.broker_address, mqttutil.broker_port)
client.connect(mqttutil.broker_address, mqttutil.broker_port)

# Publish
client.publish("gazpar/status","ON")
