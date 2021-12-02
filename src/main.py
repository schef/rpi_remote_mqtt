import time
import paho.mqtt.client as paho
from paho import mqtt
import credentials
import threading
import log
import time
import network_info
import sensors

logger = log.get()
light_state = 0


def get_millis():
    return round(time.time() * 1000)


def millis_passed(timestamp):
    return get_millis() - timestamp


def get_uptime(timestamp):
    return int(millis_passed(timestamp) / 1000)


def set_light(state):
    global light_state
    light_state = state
    client.publish("device_outdoor/output/light", payload=light_state, retain=True, qos=1)


def get_ip():
    return network_info.get_ip_from_device(network_info.get_network_devices()[0])

def get_temp():
    return sensors.get_temperature()

def loop(client):
    logger.info("[LOOP]: init begin")
    start_timestamp = get_millis()
    set_light(0)
    logger.info("[LOOP]: init end")
    count = 0
    while True:
        client.publish("device_outdoor/output/uptime", payload=get_uptime(start_timestamp), retain=True, qos=1)
        time.sleep(10)
        if count == 0:
            client.publish("device_outdoor/output/network", payload=get_ip(), retain=True, qos=1)
            client.publish("device_outdoor/output/sensors", payload=get_temp(), retain=True, qos=1)
        count += 1
        if count == 10:
            count = 0


def parse_on_message(topic, payload):
    if topic == "device_outdoor/input/light":
        set_light(int(payload))


def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("[MQTT]: CONNACK received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    logger.info("[MQTT]: on_publish mid[%s]" % (str(mid)))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    logger.info("[MQTT]: on_subscribe mid[%s], granted_qos[%s]" % (str(mid), str(granted_qos)))


def on_message(client, userdata, msg):
    logger.info("[MQTT]: on_message topic[%s], qos[%s], payload[%s]" % (msg.topic, str(msg.qos), str(msg.payload)))
    parse_on_message(msg.topic, msg.payload)


if __name__ == "__main__":
    logger.info("[MAIN]: init begin")
    client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(credentials.user, credentials.password)
    client.connect(credentials.host, credentials.port)

    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    client.subscribe("device_outdoor/input/#", qos=1)

    logger.info("[MAIN]: init end")

    x = threading.Thread(target=loop, args=(client,))
    x.start()

    client.loop_forever()
