import paho.mqtt.client as paho
from paho import mqtt
import threading
import log
from thread_monitor import ThreadMonitor, ThreadMonitorExitStrategySystemdWatchdog
import credentials

if credentials.project == "ekofarma":
    import logic_ekofarma as logic
elif credentials.project == "havas":
    import logic_havas as logic
else:
    import logic_generic as logic

logger = log.get()

DEVICE_NAME = credentials.name
DEVICE_INPUT = "%s/input/" % DEVICE_NAME


def check_mqtt_send(mqtt_client):
    topic, message = logic.get_mqtt()
    if topic != None:
        mqtt_client.publish("%s/output/%s" % (DEVICE_NAME, topic), payload=message, retain=True, qos=1)


def main(mqtt_client):
    logger.info("[LOOP]: main begin")
    logic.init()
    logger.info("[LOOP]: main end")
    while True:
        logic.loop()
        check_mqtt_send(mqtt_client)


def on_connect(client, userdata, flags, rc, properties=None):
    logger.info("[MQTT]: CONNACK received with code %s." % str(rc))


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

    mqtt_client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
    mqtt_client.on_connect = on_connect

    mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    mqtt_client.username_pw_set(credentials.user, credentials.password)
    mqtt_client.connect(credentials.host, credentials.port)

    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish

    mqtt_client.subscribe("%s/input/#" % (DEVICE_NAME), qos=1)

    main_client_thread = threading.Thread(target=main, args=(mqtt_client,))

    logger.info("[MAIN]: start end")

    main_client_thread.start()
    ThreadMonitor.watch(main_client_thread)
    mqtt_client.loop_start()
    ThreadMonitor.watch(mqtt_client._thread)
    ThreadMonitor.join()


if __name__ == "__main__":
    start()
