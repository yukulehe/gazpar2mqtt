import paho.mqtt.client as mqtt

# Mqtt broker
broker_address = "192.168.1.184"
broker_port = "1883"
broker_client = "gazou"

# Create instance
print("Create mqtt instance")
client = mqtt.Client(broker_client)

# Connect
print("Connexion to broker")
client.connect(broker_address, broker_port, 60)

# Publish
client.publish("gazpar/status","ON")
