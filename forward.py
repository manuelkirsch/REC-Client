import websocket
import _thread
import time
import rel
import random
import time
import json

from paho.mqtt import client as mqtt_client

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
    
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def on_message(ws, message):
    jsonData = json.loads(message)
    if jsonData["type"] == 'status':
        result = client.publish("rec/bms/soc", jsonData["bms_array"]["master"]["soc"])
        result = client.publish("rec/bms/ibat", jsonData["bms_array"]["master"]["ibat"])
        result = client.publish("rec/bms/vbat", jsonData["bms_array"]["master"]["vbat"])
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send status message to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
    else:
        print(f"Ignored settings message")

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    # mqtt setup:
    broker = '10.0.0.20'
    port = 1883
    topic = "rec/bms"
    client_id = f'rec-bms-{random.randint(0, 1000)}'
    username = 'loxberry'
    password = '6AaZnZX8hhllQvjo'
    
    client = connect_mqtt()
    client.loop_start()
    
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://10.0.0.95/ws",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
    client.loop_stop()