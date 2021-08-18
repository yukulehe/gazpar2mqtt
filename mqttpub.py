import paho.mqtt.client as mqtt

# Broker settings
broker_address = "mosquitto" #'172.28.0.3
broker_port = 1883
broker_client = "gazou"

# Initialize variables
mqtt_connected = False

# on_connect
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    print("on_connect: " + mqtt.connack_string(rc))
    mqtt_connected = True

# ----------------------------
# Main
# ----------------------------

# Create instance
print("Create mqtt instance")
client = mqtt.Client(broker_client)

# Activate callbacks
client.on_connect = on_connect
client.on_message = mqttutil.on_message
client.on_publish = mqttutil.on_publish
client.on_disconnect = mqttutil.on_disconnect

# Connect
print("Connexion to broker: %s : %s", broker_address, broker_port)
client.connect(broker_address, broker_port)

# Publish
print("Publication to broker")
client.publish("gazpar/status","ON")
