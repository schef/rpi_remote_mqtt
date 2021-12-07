import paho.mqtt.client as paho
from paho import mqtt
import credentials
import threading
import log
import rpi_peripherals
import logic

logger = log.get()

DEVICE_NAME = "device_outdoor"


def main():
    logger.info("[LOOP]: main begin")
    rpi_peripherals.init()
    logic.init()
    logger.info("[LOOP]: main end")
    while True:
        rpi_peripherals.loop()
        logic.loop()


def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("[MQTT]: CONNACK received with code %s." % rc)


def on_publish(client, userdata, mid, properties=None):
    logger.info("[MQTT]: on_publish mid[%s]" % (str(mid)))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    logger.info("[MQTT]: on_subscribe mid[%s], granted_qos[%s]" % (str(mid), str(granted_qos)))


def on_message(client, userdata, msg):
    logger.info("[MQTT]: on_message topic[%s], qos[%s], payload[%s]" % (msg.topic, str(msg.qos), str(msg.payload)))


def start():
    logger.info("[MAIN]: start begin")
    mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    mqtt_client.on_connect = on_connect

    mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    mqtt_client.username_pw_set(credentials.user, credentials.password)
    mqtt_client.connect(credentials.host, credentials.port)

    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish

    mqtt_client.subscribe("%s/input/#" % (DEVICE_NAME), qos=1)

    main_thread = threading.Thread(target=main)
    logger.info("[MAIN]: start end")

    main_thread.start()
    mqtt_client.loop_forever()


if __name__ == "__main__":
    start()
