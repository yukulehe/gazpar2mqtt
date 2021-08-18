topic_name = "gazpar"
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection: {}".format(rc) )
def on_message(client, userdata, msg):
    print("onMessageArrived: " + msg.topic + " " + str(msg.payload))
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: mid=" + str(mid) + " QoS=" + str(granted_qos))
def on_publish(client, userdata, mid):
    print("Published: mid=" + str(mid) )
