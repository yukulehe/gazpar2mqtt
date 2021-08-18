# Import
import mqttutil
import paho.mqtt.client as mqtt
import time


mqtt_connected = False

def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    print("on_connect: " + mqtt.connack_string(rc))
    mqtt_connected = True
    
client = mqtt.Client("pub-client-id")
client.on_connect = on_connect
client.on_message = util.on_message
client.on_publish = util.on_publish
client.on_disconnect = util.on_disconnect
client.connect(util.mqtt_host["hostname"], util.mqtt_host["port"], 60)
client.loop_start()

def loopX() :
    global mqtt_connected
    while 1:
        if mqtt_connected :
            client.publish(util.topic_name, "Hello from a publish call")
            time.sleep(3)
loopX()
