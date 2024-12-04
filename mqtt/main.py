import threading
import os, sys

import paho.mqtt.client as paho
from paho import mqtt
import credentials

mqtt_client = None
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from common.thread_monitor import ThreadMonitor, ThreadMonitorExitStrategySystemdWatchdog
from common import log

if credentials.project == "ekofarma":
    import logic_ekofarma as logic
elif credentials.project == "grijanje":
    import logic_grijanje as logic
elif credentials.project == "rmale":
    import logic_rmale as logic
elif credentials.project == "sauna":
    import logic_sauna as logic
elif credentials.project == "autofarmika":
    import logic_autofarmika as logic
elif credentials.project == "ssc_powermeter":
    import logic_ssc_powermeter as logic

logger = log.get()
logger.setLevel("INFO")

DEVICE_NAME = credentials.name
DEVICE_INPUT = "%s/input/" % DEVICE_NAME
init_status = False


def check_mqtt_send(mqtt_client):
    topic, message = logic.get_mqtt()
    if topic != None:
        mqtt_client.publish("%s/output/%s" % (DEVICE_NAME, topic), payload=message, retain=True, qos=1)


def main_unblocking(mqtt_client):
    global init_status
    logger.info("[LOOP]: main unblocking begin")
    logic.init()
    logger.info("[LOOP]: main unblocking end")
    init_status = True
    while True:
        logic.loop_unblocking()
        check_mqtt_send(mqtt_client)


def main_blocking():
    while not init_status:
        pass
    logger.info("[LOOP]: main blocking begin")
    logger.info("[LOOP]: main blocking end")
    while True:
        logic.loop_blocking()


def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("[MQTT]: CONNACK received with code %s." % str(rc))
    mqtt_client.subscribe("%s/input/#" % (DEVICE_NAME), qos=1)


def on_publish(client, userdata, mid, properties=None):
    logger.info("[MQTT]: on_publish mid[%s]" % (str(mid)))


def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    logger.info("[MQTT]: on_subscribe mid[%s], granted_qos[%s]" % (str(mid), str(granted_qos)))


def on_message(client, userdata, msg):
    logger.info("[MQTT]: on_message topic[%s], qos[%s], payload[%s]" % (msg.topic, str(msg.qos), str(msg.payload)))
    try:
        if DEVICE_INPUT in msg.topic:
            logic.set_mqtt(msg.topic[len(DEVICE_INPUT):], msg.payload.decode())
    except Exception as e:
        logger.error("[MQTT]: on_message %s" % (e))


def start():
    logger.info("[MAIN]: start begin")

    ThreadMonitor.set_exit_strategy(ThreadMonitorExitStrategySystemdWatchdog())
    ThreadMonitor.watch_main_thread()

    global mqtt_client
    mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    mqtt_client.on_connect = on_connect

    if len(credentials.user) > 0:
        mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        mqtt_client.username_pw_set(credentials.user, credentials.password)

    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish

    mqtt_client.connect(credentials.host, credentials.port)

    unblocking_thread = threading.Thread(target=main_unblocking, args=(mqtt_client,))
    blocking_thread = threading.Thread(target=main_blocking)

    logger.info("[MAIN]: start end")

    unblocking_thread.start()
    ThreadMonitor.watch(unblocking_thread)
    blocking_thread.start()
    ThreadMonitor.watch(blocking_thread)
    mqtt_client.loop_start()
    ThreadMonitor.watch(mqtt_client._thread)
    ThreadMonitor.join()


if __name__ == "__main__":
    start()
