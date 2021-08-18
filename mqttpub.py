import paho.mqtt.client as mqtt

broker_address = "mosquitto" #'172.28.0.3
broker_port = 1883
broker_client = "gazou"

# Create instance
print("Create mqtt instance")
client = mqtt.Client(broker_client)

# Connect
print("Connexion to broker: %s : %s", broker_address, broker_port)
client.connect(broker_address, broker_port)

# Publish
print("Publication to broker)
client.publish("gazpar/status","ON")
