import mqttutil
import paho.mqtt.client as mqtt
def on_connect(client, userdata, flags, rc):
    print("on_connect: " + mqtt.connack_string(rc))
    client.subscribe(mqttutil.topic_name, 2)
client = mqtt.Client("gazou_sub")
client.on_connect = on_connect
client.on_message = mqttutil.on_message
client.on_subscribe = mqttutil.on_subscribe
client.on_disconnect = mqttutil.on_disconnect
client.connect(mqttutil.mqtt_host["hostname"], mqttutil.mqtt_host["port"], 60)
client.loop_forever()
